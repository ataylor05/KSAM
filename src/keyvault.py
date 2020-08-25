from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import time

class KeyVault():

    def __init__(self, vault_url):
        self.credential = DefaultAzureCredential()
        self.secret_client = SecretClient(vault_url=vault_url, credential=self.credential)

    def get_secret(self, secret_name):
        secret = self.secret_client.get_secret(secret_name)
        print(secret.enabled)
        return secret.value

    def update_secret(self, secret_name, secret_data):
        secret = self.secret_client.set_secret(secret_name, secret_data)
        return secret.properties.version

    def delete_secret(self, secret_name):
        secret = self.secret_client.begin_delete_secret(secret_name).wait()
        self.secret_client.purge_deleted_secret(secret_name)
        print(secret)