import unittest
import os
import time
import src.kubeconfig

class KubeConfigTest(unittest.TestCase):

    namespace = "test"

    def setUp(self):
        self.kc = src.kubeconfig.KubeConfig()
        self.kc._createNameSpace(KubeConfigTest.namespace)

    def tearDown(self):
        try:
            self.kc._deleteNameSpace(KubeConfigTest.namespace)
            while self.kc._getNamespaceStatus(KubeConfigTest.namespace) != None:
                time.sleep(1)
        except:
            print("Namespace no longer found")

    def test_config_path(self):
        path = os.path.isfile(self.kc.config_path)
        self.assertTrue(path)

    def test_api_var_not_empty(self):
        api = self.kc.api_server
        self.assertRegex(api, r'^https://([a-z0-9_\.-]+):6443')

    def test_cluster_name_var_not_empty(self):
        name = self.kc.cluster_name
        self.assertTrue(name)

    def test_cluster_context_var_not_empty(self):
        name = self.kc.current_context
        self.assertTrue(name)

    def test_create_service_account(self):
        sa = self.kc._createServiceAccount(KubeConfigTest.namespace)
        self.assertRegex(str(sa.metadata), r'-service-account')

    def test_get_service_account_token(self):	
        self.kc._createServiceAccount(KubeConfigTest.namespace)
        token = self.kc._getServiceAccountToken(KubeConfigTest.namespace)
        self.assertTrue(len(token) > 100)

    def test_delete_service_account(self):
        self.kc._createServiceAccount(KubeConfigTest.namespace)
        sa = self.kc._deleteServiceAccount(KubeConfigTest.namespace)
        self.assertRegex(str(sa.metadata.resource_version), r'([0-9])')

