import yaml
import logging
import base64
import kubernetes
import shutil
import os
import subprocess
import pathlib

class KubeConfig():

    config_path = "/home/scm/.kube/config"

    def __init__(self):
        self.config_path = KubeConfig.config_path
        with open(self.config_path) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        self.api_server = data["clusters"][0]["cluster"]["server"]
        self.cluster_name = data["clusters"][0]["name"]
        self.current_context = data["contexts"][0]["name"]

    def _k8sCoreApi(self):
        kubernetes.config.load_kube_config(config_file=self.config_path)
        return kubernetes.client.ApiClient()

    def _createNameSpace(self, namespace):
        try:
            with open("templates/namespace.yaml", "r") as file:
                data = file.read()
                data = data.replace("##namespace##", namespace)
            with open("namespace.yaml", "w") as file:
                file.write(data)
            client = KubeConfig._k8sCoreApi(self)
            request = kubernetes.utils.create_from_yaml(client, "namespace.yaml")
            return request
        except Exception as e:
            logging.error(e)

    def _createServiceAccount(self, namespace):
        try:
            sa_name = namespace + "-service-account"
            with open("templates/service-account.yaml", "r") as file:
                data = file.read()
                data = data.replace("##namespace##", namespace)
            with open("service-account.yaml", "w") as file:
                file.write(data)
            client = KubeConfig._k8sCoreApi(self)
            request = kubernetes.utils.create_from_yaml(client, "service-account.yaml")
            return sa_name
        except Exception as e:
            logging.error(e)

    def _createSaRbac(self, namespace):
        try:
            with open("templates/rbac.yaml", "r") as file:
                data = file.read()
                data = data.replace("##namespace##", namespace)
            with open("rbac.yaml", "w") as file:
                file.write(data)
            client = KubeConfig._k8sCoreApi(self)
            request = kubernetes.utils.create_from_yaml(client, "rbac.yaml")
            return request
        except Exception as e:
            logging.error(e)

    def _getServiceAccountToken(self, sa, namespace):
        try:
            kubernetes.config.load_kube_config(config_file=self.config_path)
            client = kubernetes.client.CoreV1Api()
            request = client.read_namespaced_service_account(name=sa, namespace=namespace)
            secret_name = request.secrets[0].name
            request = client.read_namespaced_secret(secret_name, namespace)
            encoded_token = request.data["token"]
            decoded_token = base64.b64decode(encoded_token)
            return str(decoded_token, "utf-8")
        except Exception as e:
            logging.error(e)

    def _setKubeConfigContext(self, config_path, namespace, token):
        starting_context = "demo-build-cluster-01"
        subprocess.call(["kubectl", "--kubeconfig", config_path, "config", "use-context", starting_context])
        subprocess.call(["kubectl", "--kubeconfig", config_path, "config", "view", "--flatten", "--minify"])
        subprocess.call(["kubectl", "config", "--kubeconfig", config_path, "rename-context", starting_context, namespace])
        subprocess.call(["kubectl", "config", "--kubeconfig", config_path, "set-credentials", (namespace + "-token-user"), "--token", token])
        subprocess.call(["kubectl", "config", "--kubeconfig", config_path, "set-context", namespace, "--user", (namespace + "-token-user")])
        subprocess.call(["kubectl", "config", "--kubeconfig", config_path, "set-context", namespace, "--namespace", namespace])
        subprocess.call(["kubectl", "config", "--kubeconfig", config_path, "view", "--flatten", "--minify"])

    def createNewKubeConfig(self, namespace):
        # Copy kube config file
        new_name = (os.path.basename(self.config_path) + "-" + namespace)
        config_path = "/home/scm/SCM/" + new_name
        shutil.copyfile(self.config_path, new_name)

        # Create namespace
        KubeConfig._createNameSpace(self, namespace)

        # Create service account
        KubeConfig._createServiceAccount(self, namespace)
        sa_name = namespace + "-service-account"

        # Create service account rbac policy
        KubeConfig._createSaRbac(self, namespace)

        # Get service account token
        token = KubeConfig._getServiceAccountToken(self, sa_name, namespace)
        
        # Set kube config contexts
        KubeConfig._setKubeConfigContext(self, config_path, namespace, token)

        # Clean up
        files = ["namespace.yaml", "service-account.yaml", "rbac.yaml"]
        for f in files:
            path = pathlib.Path(f)
            if path.exists ():
                os.remove(f)

        return config_path