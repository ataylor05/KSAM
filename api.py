from flask import Flask, jsonify, request, render_template
import requests
import yaml
import logging
import json
import os
from kubernetes import client, config, utils
import base64
from kubeconfig import KubeConfig
import shutil

app = Flask(__name__)
app.config["DEBUG"] = True
global config_path
global api_server
global cluster_name
config_path = "/SCM/.kube/config"
api_server = "https://demo-build-cluster-01-dns-df698130.hcp.eastus.azmk8s.io"
cluster_name = "demo-build-cluster-01"

def ado_request(url, pat, verb, data=""):
    try:
        auth = str(base64.b64encode(bytes(":"+pat, "ascii")), 'ascii')
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic "+auth
        }
        if verb == "get":
            response = requests.get(url, headers=headers, verify=False)
        elif verb == "post":
            response = requests.post(url, headers=headers, data=data, verify=False)
        return response.text
    except Exception as e:
        logging.error(e)


def connect_k8s_api(cluster_name):
    try:
        config.load_kube_config(config_file=config_path, context=cluster_name)
        return client.ApiClient()
    except Exception as e:
        logging.error(e)


def connect_k8s_core_api(cluster_name):
    try:
        config.load_kube_config(config_file=config_path, context=cluster_name)
        return client.CoreV1Api()
    except Exception as e:
        logging.error(e)


def create_k8s_service_account(cluster_name, namespace):
    try:
        rbac_manifest = render_template("sa-rbac-template.yaml", namespace=namespace)
        k8s_client = connect_k8s_api(cluster_name)
        f = open( "rbac_manifest.yaml", 'w' )
        f.write(rbac_manifest)
        f.close()
        request = utils.create_from_yaml(k8s_client, "rbac_manifest.yaml")
        os.remove("rbac_manifest.yaml")
        return request
    except Exception as e:
        logging.error(e)


def create_kube_config_file(namespace, cluster_name):
    try:
        sa = namespace + "-service-account"
        k8s_client = connect_k8s_core_api(cluster_name)
        api_response = k8s_client.read_namespaced_service_account(sa, namespace)
        sa_secret_name = api_response.secrets[0].name
        api_response = k8s_client.read_namespaced_secret(sa_secret_name, namespace)
        encoded_token = api_response.data["token"]
        decodedBytes = base64.b64decode(encoded_token)
        token = str(decodedBytes, "utf-8")
        shutil.copyfile("/SCM/.kube/config", "/SCM/config")
        conf = KubeConfig("/SCM/config")
        current_context = conf.current_context()
        current_config = conf.view()
        current_user = current_config["users"][0]["name"]
        conf.set_context(name=namespace, cluster=cluster_name, namespace=namespace, user=namespace)
        conf.set_credentials(name=namespace, token=token)
        conf.delete_context(name=current_context)
        conf.use_context(namespace)
        conf.unset('users.clusterUser_ataylor-aks_demo-build-cluster-01')
        with open("config") as file:
            data = file.read()
        return data
    except Exception as e:
        logging.error(e)


def ado_get_project_id(project_name, org, pat):
    try:
        url = "https://dev.azure.com/" + org + "/_apis/projects/" + project_name + "?api-version=5.1"
        project = ado_request(url, pat, "get")
        project_dict = json.loads(project)
        return project_dict["id"]
    except Exception as e:
        logging.error(e)


def create_json_body(api_server, cluster_name, kube_config, namespace, project, project_id):
    try:
        service_endpoint_name = cluster_name + "-" + namespace + "-k8s-service-account"
        json_body = render_template("body-template.json", api_server=api_server, kube_config=kube_config, project_id=project_id, project_name=project, service_endpoint_name=service_endpoint_name)
        return json_body
    except Exception as e:
        logging.error(e)


def create_az_service_connection(json_body, org, project, pat):
    try:
        url = "https://dev.azure.com/" + org + "/" + project + "/_apis/serviceendpoint/endpoints?api-version=6.0-preview.4"
        return ado_request(url, pat, "post", json_body)
    except Exception as e:
        logging.error(e)


@app.route("/testServiceAccountManager", methods=["GET"])
def test():
    return "Works"

@app.route("/createServiceAccount", methods=["POST"])
def createServiceAccount():
    # Fill vars
    org = str(request.json.get('org', ''))
    pat = str(request.json.get('pat', ''))
    project = str(request.json.get('project', ''))
    namespace = str(request.json.get('namespace', ''))

    # Create rbac policy
    create_k8s_service_account(cluster_name, namespace)

    # Create kube config
    kube_config = create_kube_config_file(namespace, cluster_name)

    # Get project id
    project_id = ado_get_project_id(project, org, pat)

    # Create request body
    json_body = create_json_body(api_server, cluster_name, kube_config, namespace, project, project_id)

    # Create ADO service connection
    return create_az_service_connection(json_body, org, project, pat)
app.run(host='0.0.0.0')
