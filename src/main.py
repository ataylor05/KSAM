from flask import Flask, jsonify, request, render_template
import pathlib
import os
import json
from kubeconfig import KubeConfig
from keyvault import KeyVault
from azuredevops import AzureDevops

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route("/HealthCheck", methods=["GET"])
def healthCheck():
    return "Works"

@app.route("/createServiceAccount", methods=["POST"])
def createServiceAccount():
    org = str(request.json.get('org', ''))
    pat = str(request.json.get('pat', ''))
    project = str(request.json.get('project', ''))
    namespace = str(request.json.get('namespace', ''))

    kc = KubeConfig()
    kubeconfig = kc.createNewKubeConfig(namespace)

    kv = KeyVault(vault_url="https://ksam.vault.azure.net/")
    secret_name = namespace + "-sa"
    kv.update_secret(secret_name, kubeconfig)

    ado = AzureDevops()
    return ado.createServiceConnection(kubeconfig, kc.cluster_name, namespace, kc.api_server, project, org, pat)

@app.route("/deleteServiceAccount", methods=["POST"])
def deleteServiceAccount():
    org = str(request.json.get('org', ''))
    pat = str(request.json.get('pat', ''))
    project = str(request.json.get('project', ''))
    namespace = str(request.json.get('namespace', ''))

    kc = KubeConfig()
    kc._deleteServiceAccount(namespace)

    kv = KeyVault(vault_url="https://ksam.vault.azure.net/")
    secret_name = namespace + "-sa"
    kv.delete_secret(secret_name)

    ado = AzureDevops()
    service_endpoint_name = kc.cluster_name + "-" + namespace + "-k8s-service-account"
    return ado.getServiceEndpointId(service_endpoint_name, pat, org, project)


app.run(host='0.0.0.0', ssl_context='adhoc')