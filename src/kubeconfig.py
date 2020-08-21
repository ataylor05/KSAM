import yaml
import logging
import base64
import kubernetes
import shutil
import os
import subprocess
import pathlib

class KubeConfig():

    home_path = str(pathlib.Path.home())
    config_path = os.path.join(home_path, ".kube", "config")

    def __init__(self):
        self.config_path = KubeConfig.config_path
        with open(self.config_path) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        self.certificate_authority_data = data["clusters"][0]["cluster"]["certificate-authority-data"]
        self.api_server = data["clusters"][0]["cluster"]["server"]
        self.cluster_name = data["clusters"][0]["name"]
        self.current_context = data["contexts"][0]["name"]

    def _k8sApi(self):
        try:
            kubernetes.config.load_kube_config(config_file=self.config_path)
            return kubernetes.client.ApiClient()
        except Exception as e:
            logging.error(e)

    def _k8sCoreV1Api(self):
        try:
            configuration = kubernetes.client.Configuration(config_file=self.config_path)
            return kubernetes.client.CoreV1Api()
        except Exception as e:
            logging.error(e)

    def _getNamespaceStatus(self, namespace):
        kubernetes.config.load_kube_config()
        v1 = kubernetes.client.CoreV1Api()
        request =  v1.read_namespace(namespace)
        return request.status

    def _createNameSpace(self, namespace):
        try:
            kubernetes.config.load_kube_config()
            v1 = kubernetes.client.CoreV1Api()
            ns = kubernetes.client.V1Namespace()
            ns.metadata = kubernetes.client.V1ObjectMeta()
            ns.metadata.name = namespace
            return v1.create_namespace(ns)
        except Exception as e:
            logging.error(e)

    def _deleteNameSpace(self, namespace):
        try:
            kubernetes.config.load_kube_config()
            v1 = kubernetes.client.CoreV1Api()
            return v1.delete_namespace(name=namespace)
        except Exception as e:
            logging.error(e)

    def _createServiceAccount(self, namespace):
        try:
            kubernetes.config.load_kube_config()
            v1 = kubernetes.client.CoreV1Api()
            service_account = kubernetes.client.V1ServiceAccount()
            service_account.metadata = kubernetes.client.V1ObjectMeta()
            service_account.metadata.name = (namespace + "-service-account")
            return v1.create_namespaced_service_account(namespace, service_account)
        except Exception as e:
            logging.error(e)

    def _deleteServiceAccount(self, namespace):
        try:
            kubernetes.config.load_kube_config()
            v1 = kubernetes.client.CoreV1Api()
            service_account = (namespace + "-service-account")
            return v1.delete_namespaced_service_account(service_account, namespace)
        except Exception as e:
            logging.error(e)

    def _getServiceAccountToken(self, namespace):
        try:
            kubernetes.config.load_kube_config(config_file=self.config_path)
            v1 = kubernetes.client.CoreV1Api()
            name = (namespace + "-service-account")
            sa = v1.read_namespaced_service_account(name=name, namespace=namespace)
            secret_name = sa.secrets[0].name
            secret = v1.read_namespaced_secret(secret_name, namespace)
            encoded_token = secret.data["token"]
            decoded_token = base64.b64decode(encoded_token)
            return str(decoded_token, "utf-8")
        except Exception as e:
            logging.error(e)

    def _createSaRbac(self, namespace):
        try:
            shutil.copyfile("templates/rbac.yaml", "./rbac.yaml")
            with open("./rbac.yaml", "r") as file:
                data = file.read()
                data = data.replace("##namespace##", namespace)
            with open("rbac.yaml", "w") as file:
                file.write(data)
            client = KubeConfig._k8sApi(self)
            request = kubernetes.utils.create_from_yaml(client, "rbac.yaml")
            return request
        except Exception as e:
            logging.error(e)

    def _createKubeConfig(self, token, namespace):
        try:
            shutil.copyfile("templates/config", "./config")
            with open("./config", "r") as file:
                data = file.read()
                data = data.replace("##certificate_authority_data##", self.certificate_authority_data)
                data = data.replace("##api_server##", self.api_server)
                data = data.replace("##cluster_name##", self.cluster_name)
                data = data.replace("##namespace##", namespace)
                data = data.replace("##token##", token)
            with open("config", "w") as file:
                file.write(data)
        except Exception as e:
            logging.error(e)

    def createNewKubeConfig(self, namespace):
        try:
            # Create namespace
            KubeConfig._createNameSpace(self, namespace)

            # Create service account
            KubeConfig._createServiceAccount(self, namespace)
            sa_name = namespace + "-service-account"

            # Create service account rbac policy
            KubeConfig._createSaRbac(self, namespace)

            # Get service account token
            token = KubeConfig._getServiceAccountToken(self, namespace)
            
            # Create kubeconfig
            KubeConfig._createKubeConfig(self, token, namespace)

            with open("./config") as file:
                config = yaml.load(file, Loader=yaml.Loader)

            # Clean up
            os.rename("./config", ("./" + self.cluster_name + "-" + namespace + "-config"))
            os.remove("./rbac.yaml")

            return config
        except Exception as e:
            logging.error(e)