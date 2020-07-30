import requests
import base64
import logging
import json

class ServiceConnection():

    def __init__(self, project_name, org, pat, namespace, kubeconfig_path):
        self.project_name = project_name
        self.org = org
        self.pat = pat
        self.namespace = namespace
        self.kubeconfig_path = kubeconfig_path
        self.cluster_name = "demo-build-cluster-01"
        self.api_server = "https://demo-build-cluster-01-dns-ff0a38da.hcp.eastus.azmk8s.io:443"

    def _adoRequest(self, url, verb, data=""):
        try:
            auth = str(base64.b64encode(bytes(":"+self.pat, "ascii")), 'ascii')
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

    def _adoGetProjectId(self, project_name, org):
        try:
            url = "https://dev.azure.com/" + org + "/_apis/projects/" + project_name + "?api-version=5.1"
            project = ServiceConnection._adoRequest(self, url, "get")
            project_dict = json.loads(project)
            return project_dict["id"]
        except Exception as e:
            logging.error(e)

    def _createJsonBody(self, kube_config, project_id):
        try:
            service_endpoint_name = self.cluster_name + "-" + self.namespace + "-k8s-service-account"
            with open("templates/body-template.json", "r") as file:
                data = file.read()
                data = data.replace("##kube_config##", kube_config)
                data = data.replace("##service_endpoint_name##", service_endpoint_name)
                data = data.replace("##api_server##", self.api_server)
                data = data.replace("##project_id##", project_id)
                data = data.replace("##project_name##", self.project_name)
            with open("body.json", "w") as file:
                file.write(data)
            #return request
        except Exception as e:
            logging.error(e)

    def _createAdoServiceConnection(self):
        try:
            json_body = open("body.json", "r")
            url = "https://dev.azure.com/" + self.org + "/" + self.project_name + "/_apis/serviceendpoint/endpoints?api-version=6.0-preview.4"
            return ServiceConnection._adoRequest(self, url, "post", json_body)
        except Exception as e:
            logging.error(e)

    def createServiceConnection(self):
        # Get project id
        project_id = ServiceConnection._adoGetProjectId(self, self.project_name, self.org)

        # Create json body for API request
        kube_config = open(self.kubeconfig_path, "r")
        ServiceConnection._createJsonBody(self, kube_config.read(), project_id)

        # Create ADO service connection
        return ServiceConnection._createAdoServiceConnection(self)