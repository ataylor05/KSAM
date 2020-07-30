from flask import Flask, jsonify, request, render_template
import pathlib
import os
from k8s import KubeConfig
from serviceconnection import ServiceConnection

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route("/HealthCheck", methods=["GET"])
def healthCheck():
    return "Works"

@app.route("/createServiceAccount", methods=["POST"])
def createServiceAccount():
    # Fill vars
    org = str(request.json.get('org', ''))
    pat = str(request.json.get('pat', ''))
    project = str(request.json.get('project', ''))
    namespace = str(request.json.get('namespace', ''))

    # Create kube config
    kc = KubeConfig()
    kubeconfig_path = kc.createNewKubeConfig(namespace)

    # Create ADO service connection
    sc = ServiceConnection(project, org, pat, namespace, kubeconfig_path)

    # Clean up
    path = pathlib.Path("body.json")
    if path.exists ():
        os.remove(f)

    return sc.createServiceConnection()

app.run(host='0.0.0.0')