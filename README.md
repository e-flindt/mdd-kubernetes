# mdd-kubernetes
This project contains all infrastructure components required for a gitops-driven mdd workflow.  
Clone url: https://github.com/e-flindt/mdd-kubernetes.git  

Thank you to vfarcic at GitHub for the great [demo](https://github.com/vfarcic/argo-combined-demo) on Argo CD, Argo Events and Argo Workflows!

## Overview

To run this prototype, a kubernetes cluster is required as well as two persistent volumes for the local Gitea git server.  
If you run this prototype on a cluster that is reachable by GitHub or any other repository that can contact your cluster, you might not need the volumes and the Gitea git server.  
In this case you need to edit a lot of files in this project because the Gitea URL is hardcoded everywhere.
You also need to set up credentials in this case.  
The services kubernetes dashboard, gitea, postgres, argo cd, argo events and argo workflows will be deployed to the cluster.  
Additionally, some example git repositories will be created to run the mdd workflow.

## Requirements

The resources in this repo have been tested with Microsoft Windows 10 Pro, Version 10.0.19044.  
The following programs are required to run this prototype:

- Docker Desktop v4.11.1 or higher, WSL 2 based engine and Kubernetes enabled
- kubectl client version v1.24.3 or higher
- helm version is v3.9.3 or higher
- git version 2.34 or higher
- python 3.10.7 or higher

Make sure that you edit your C:\Windows\System32\drivers\etc\hosts file to contain the following hosts pointing towards the cluster.  
These hostnames depend on the service names and namespaces in the cluster and are not defined by Ingress.  
Rather, Ingress needs to conform to the kubernetes naming in this case.  
Pattern: 'service-name'.'namespace including default'.svc.cluster.local  
```
127.0.0.1 kubernetes.docker.internal svc.cluster.local infra-kubernetes-dashboard.default.svc.cluster.local infra-gitea-http.default.svc.cluster.local argocd-server.argocd.svc.cluster.local argo-workflows-server.argo.svc.cluster.local
```

## Nginx, kubernetes dashboard and gitea

Start by opening https://infra-kubernetes-dashboard.default.svc.cluster.local/ in your browser.  
The connection will be refused, this is expected.  

Now run 
```
helm upgrade --install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx
``` 
Refresh the browser every few seconds until the connection error in your browser switches to an HTTPS error.  
This is expected because the cluster created a self-signed certificate, proceed anyway.  
The 404 not found error indicates that the nginx is ready to serve ingress resources.  

The persistent volumes for gitea and postgres point towards the following directories on the host (your computer).  
Edit .\infra\templates\persistence.yaml to change this.  
This cannot be changed after gitea and postgres are deployed.  
Be careful when wiping these directories, files will be lost!  
- C:\temp\docker-volumes\gitea
- C:\temp\docker-volumes\postgresql

Proceed to run
```
helm dependency update ./infra
helm upgrade --install infra ./infra
```
Refresh your browser again and you will now be prompted to enter a token for dashboard access.  
Run the batch file 'print-dashboard-admin-token.bat' and enter the token output into the login page.  
You should now see the dashboard.  
Switch to 'All namespaces' in the dropdown menu.  
It may take a while for the persistent volume claims to be bound to the pods, an erroneous state is normal until this is resolved.  

## Setup repositories in gitea

These steps are only necessary when the volumes of the cluster host have been wiped or the volumes have been newly created.  

The reason why Gitea is used instead of using GitHub directly is that Argo Events relies on webhooks, which means the local cluster must be reachable from the outside.  
For this prototype it has been assumed to be easier to provide a local git server instead of providing an external cluster.

Gitea admin access is 'gitea-admin:password'.

A python script will be used to create all the repositories (see .\setup-examples.py).  
These include example mdd artifacts and this project itself (mdd-kubernetes).
```
pip install -r requirements.txt
python setup-examples.py 
```

To let Argo CD deploy Argo Workflows and Argo Events, commit everything in this directory to http://infra-gitea-http.default.svc.cluster.local/gitea-admin/mdd-kubernetes.git  
If you cloned this repository, add the following remote and push to it:
```
git remote add local-git http://infra-gitea-http.default.svc.cluster.local/gitea-admin/mdd-kubernetes.git
git push -u local-git --all --force
```

## Argo CD

Argo Worflows requires a custom container image to run urllib3 inside a workflow.
Build it with
```
docker build -t urllib3-docker ./urllib3-docker
```

Proceed with 
```
helm dependency update ./argocd
helm upgrade --install argocd ./argocd --namespace argocd --create-namespace
```
Open https://argocd-server.argocd.svc.cluster.local in your browser.  
Run the batch file 'print-argocd-admin-password.bat' and enter the credentials into the login page of argocd.  
It may take a few minutes until all Argo Applications are ready.

## Run the workflow

Either check out any of the created repositories, for example http://infra-gitea-http.default.svc.cluster.local/gitea-admin/customer-microservice.git or test the delivery of a webhook in the gitea admin UI http://infra-gitea-http.default.svc.cluster.local/gitea-admin/customer-microservice/settings/hooks
Access the Argo Workflows UI to watch the workflow execution https://argo-workflows-server.argo.svc.cluster.local/
