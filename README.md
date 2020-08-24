# KSAM
Kubernetes Service Account Manager.  This project creates Kuberentes service account and stores the kube config file in an Azure KeyVault.  Afterward an Azure Devops Service Connection is made with the kube config file.

## Using kube configs

# API calls

## Health check
This API call is for the Kubernetes deployment resource health check.<br>
**VERB:** get<br>
**URL:** https://localhost/HealthCheck<br>
<br>
**Example Response:**
<pre>
works
</pre>
<br><br>

## Create Service Account
Creates a Kubernetes service account with RBAC.yaml template in the namespace provided.  Namespace will be created if it does not exist.  A kube config file is generated from the service account and stored in an Azure Key Vault.  After storing the secret, an Azure Devops service connection is made with the kube config file.<br><br>
**VERB:** post<br>
**URL:** https://localhost/createServiceAccount<br>
**Headers:** Content-Type: application/json<br>
**Parameters:**<br>
<pre>
{
    "org":"allan05",
    "pat":"abcdefghigklmnopqrstuvwxyz", 
    "project":"Kubernetes",
    "namespace":"example-project"
}
</pre>
**Example Command:**
<pre>
curl --location --request POST 'https://localhost:5000/createServiceAccount' \
--header 'Content-Type: application/json' \
--data-raw '{
    "org":"allan05",
    "pat":"abcdefghigklmnopqrstuvwxyz", 
    "project":"Kubernetes",
    "namespace":"dynatrace"
}'
</pre>
<br><br>
**Example Response:**
<pre>
{
  "data": {
    "authorizationType": "Kubeconfig",
    "acceptUntrustedCerts": "true"
  },
  "id": "3ef3fe8b-5efc-42b7-a2b6-eeefc0f3b8b3",
  "name": "docker-desktop-dynatrace-k8s-service-account",
  "type": "kubernetes",
  "url": "https://kubernetes.docker.internal:6443",
  "createdBy": {
    "displayName": "Allan taylor",
    "url": "https://spsprodcus3.vssps.visualstudio.com/A6e4de358-5d5f-4cdb-acf6-8780ecd413f4/_apis/Identities/a89514c1-9a8e-4dfe-a522-24d0e0eb8289",
    "_links": {
      "avatar": {
        "href": "https://dev.azure.com/allan05/_apis/GraphProfile/MemberAvatars/msa.YmRjNWIxYzQtMGMzZS03NzZiLWE4MTktNTJjY2VkN2M4N2Q3"
      }
    },
    "id": "a89514c1-9a8e-4dfe-a522-24d0e0eb8289",
    "uniqueName": "allan@startmail.com",
    "imageUrl": "https://dev.azure.com/allan05/_apis/GraphProfile/MemberAvatars/msa.YmRjNWIxYzQtMGMzZS03NzZiLWE4MTktNTJjY2VkN2M4N2Q3",
    "descriptor": "msa.YmRjNWIxYzQtMGMzZS03NzZiLWE4MTktNTJjY2VkN2M4N2Q3"
  },
  "authorization": {
    "parameters": {
      "kubeConfig": null
    },
    "scheme": "Kubernetes"
  },
  "isShared": true,
  "isReady": true,
  "owner": "library",
  "serviceEndpointProjectReferences": [
    {
      "projectReference": {
        "id": "51f340e1-4fc5-4dd0-8a43-3ce695c1e9cb",
        "name": "Kubernetes"
      },
      "name": "docker-desktop-dynatrace-k8s-service-account"
    }
  ]
}
</pre>
<br><br>

## Delete Service Account
Delete a Kubernetes service account and Azure Devops service connection.  This will not delete the target namespace, it will only delete the service account and RBAC resources.  The kube config file is also deleted from the Azure Key Vault.<br><br>
**VERB:** post<br>
**URL:** https://localhost/deleteServiceAccount<br>
**Headers:** Content-Type: application/json<br>
**Parameters:**<br>
<pre>
{
    "org":"allan05",
    "pat":"abcdefghigklmnopqrstuvwxyz", 
    "project":"Kubernetes",
    "namespace":"example-project"
}
</pre>
**Example Command:**
<pre>
curl --location --request POST 'https://localhost:5000/deleteServiceAccount' \
--header 'Content-Type: application/json' \
--data-raw '{
    "org":"allan05",
    "pat":"abcdefghigklmnopqrstuvwxyz", 
    "project":"Kubernetes",
    "namespace":"dynatrace"
}'
</pre>
<br><br>
**Example Response:**
<pre>
{
  "count": 1,
  "value": [
    {
      "data": {
        "authorizationType": "Kubeconfig",
        "acceptUntrustedCerts": "true"
      },
      "id": "a52c2153-498a-480b-923f-381795c2284a",
      "name": "docker-desktop-dynatrace-k8s-service-account",
      "type": "kubernetes",
      "url": "https://kubernetes.docker.internal:6443",
      "createdBy": {
        "displayName": "Allan taylor",
        "url": "https://spsprodcus3.vssps.visualstudio.com/A6e4de358-5d5f-4cdb-acf6-8780ecd413f4/_apis/Identities/a89514c1-9a8e-4dfe-a522-24d0e0eb8289",
        "_links": {
          "avatar": {
            "href": "https://dev.azure.com/allan05/_apis/GraphProfile/MemberAvatars/msa.YmRjNWIxYzQtMGMzZS03NzZiLWE4MTktNTJjY2VkN2M4N2Q3"
          }
        },
        "id": "a89514c1-9a8e-4dfe-a522-24d0e0eb8289",
        "uniqueName": "allan@startmail.com",
        "imageUrl": "https://dev.azure.com/allan05/_apis/GraphProfile/MemberAvatars/msa.YmRjNWIxYzQtMGMzZS03NzZiLWE4MTktNTJjY2VkN2M4N2Q3",
        "descriptor": "msa.YmRjNWIxYzQtMGMzZS03NzZiLWE4MTktNTJjY2VkN2M4N2Q3"
      },
      "description": "",
      "authorization": {
        "scheme": "Kubernetes"
      },
      "isShared": false,
      "isReady": true,
      "owner": "Library",
      "serviceEndpointProjectReferences": [
        {
          "projectReference": {
            "id": "51f340e1-4fc5-4dd0-8a43-3ce695c1e9cb",
            "name": "Kubernetes"
          },
          "name": "docker-desktop-dynatrace-k8s-service-account"
        }
      ]
    }
  ]
}
</pre>
