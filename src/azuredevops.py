import requests
import base64
import logging
import json
from kubeconfig import KubeConfig

class AzureDevops():

    def _adoRequest(self, pat, url, verb, data=""):
        try:
            auth = str(base64.b64encode(bytes(":"+pat, "ascii")), 'ascii')
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Basic "+auth
            }
            print(url)
            if verb == "get":
                response = requests.get(url, headers=headers, verify=False)
            elif verb == "post":
                response = requests.post(url=url, headers=headers, data=data, verify=False)
            elif verb == "delete":
                response = requests.delete(url=url, headers=headers, verify=False)
            return response.text
        except Exception as e:
            logging.error(e)

    def _adoGetProjectId(self, project_name, org, pat):
        try:
            url = "https://dev.azure.com/" + org + "/_apis/projects/" + project_name + "?api-version=5.1"
            project = AzureDevops._adoRequest(self, pat, url, "get")
            project_dict = json.loads(project)
            return project_dict["id"]
        except Exception as e:
            logging.error(e)

    def _createJsonBody(self, kubeconfig, project_id, cluster_name, namespace, api_server, project_name):
        try:
            service_endpoint_name = cluster_name + "-" + namespace + "-k8s-service-account"
            with open("templates/body-template.json", "r") as file:
                data = file.read()
                data = data.replace("##kube_config##", kubeconfig)
                data = data.replace("##service_endpoint_name##", service_endpoint_name)
                data = data.replace("##api_server##", api_server)
                data = data.replace("##project_id##", project_id)
                data = data.replace("##project_name##", project_name)
            return data
        except Exception as e:
            logging.error(e)

    def createServiceConnection(self, kubeconfig, cluster_name, namespace, api_server, project_name, org, pat):
        project_id = self._adoGetProjectId(project_name, org, pat)
        data = self._createJsonBody(kubeconfig, project_id, cluster_name, namespace, api_server, project_name)
        url = "https://dev.azure.com/" + org + "/" + project_name + "/_apis/serviceendpoint/endpoints?api-version=6.0-preview.4"
        return self._adoRequest(pat, url, "post", data)

    def getServiceEndpointId(self, service_endpoint_name, pat, org, project):
        url = "https://dev.azure.com/" + org + "/" + project + "/_apis/serviceendpoint/endpoints?endpointNames=" + service_endpoint_name + "&api-version=6.0-preview.4"
        response = self._adoRequest(pat, url, "get")
        return response

    def deleteServiceConnection(self, namespace, project_name, endpoint_id, org, pat):
        project_id = self._adoGetProjectId(project_name, org, pat)
        url = "https://dev.azure.com/" + org + "/_apis/serviceendpoint/endpoints/" + endpoint_id + "?projectIds=" + project_id + "&api-version=6.0-preview.4"
        return self._adoRequest(pat, url, "delete")
