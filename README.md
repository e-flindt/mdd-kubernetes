# mdd-kubernetes
Contains all infrastructure components for a gitops-driven mdd workflow.

Thank you to vfarcic at GitHub for the great [demo](https://github.com/vfarcic/argo-combined-demo)!

## Requirements

The resources in this repo have been tested with Docker Desktop v4.11.1, WSL 2 based engine and kubernetes enabled on the MS Windows 10 Pro OS.
The kubectl client version is v1.24.3, kustomize version is v4.5.4 and helm version is v3.9.3.

Make sure that you edit your etc/hosts file to contain the following hosts pointing towards the cluster.
These hostnames depend on the service names and namespaces in the cluster and are not defined by Ingress.
Rather, Ingress needs to conform to the kubernetes naming in this case.
Pattern: <service-name>.<namespace including default>.svc.cluster.local
```
127.0.0.1 kubernetes.docker.internal svc.cluster.local infra-kubernetes-dashboard.default.svc.cluster.local infra-gitea-http.default.svc.cluster.local argocd-server.argocd.svc.cluster.local argo-workflows-server.argo.svc.cluster.local
```

## Nginx, kubernetes dashboard and gitea

Start by opening https://svc.cluster.local/ in your browser.
The connection will be refused, this is expected.

Now run `helm upgrade --install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx`.
Refresh the browser every few seconds until the connection error in your browser switches to an HTTPS error.
This is expected because the cluster created a self-signed certificate, proceed anyway.
The 404 not found error indicates that the nginx is ready to serve ingress resources.

Proceed to run `helm dependency update ./infra` and `helm upgrade --install infra ./infra`.
Refresh your browser again and you will now be prompted to enter a token for dashboard access.
Run the batch file 'print-dashboard-admin-token.bat' and enter the token output into the login page.
You should now see the dashboard. Switch to 'All namespaces' in the dropdown menu.
It may take a while for the persistent volume claims to be bound to the pods.

## Migrate GitHub repos to gitea

These steps are only necessary when the volumes of the cluster host have been wiped or the cluster host has been freshly installed.

The reason why gitea is used instead of using GitHub directly is that Argo Events relies on webhooks, which means the local cluster must be reachable from the outside.
For this prototype it has been assumed to be easier to provide a local git server instead of providing an external cluster.

Gitea admin access is 'gitea-admin:password'.

Create an access token: https://github.com/settings/tokens
Create new migrations for each of these repositories, do not tick the check box for mirror, ignore the webhook url for now.

1. https://github.com/e-flindt/k8-mdd.git (webhook url: http://argocd-server.argocd.svc.cluster.local/api/webhook)
2. https://github.com/e-flindt/k8-mdd-argo-events.git (webhook url: http://argocd-server.argocd.svc.cluster.local/api/webhook)
3. https://github.com/e-flindt/k8-test-app.git (webhook url: http://webhook-eventsource-svc.argo-events:12000/webhook)

Because we will not be working with this repository anymore and instead only interact with gitea, create a push mirror from gitea to GitHub by following this guide:
Use the access token created earlier and set the mirror intervall to the minimum of 0h10m0s so that changes in gitea are pushed to GitHub every 10 minutes.

We want Argo CD to manage as many Kubernetes resources as possible, therefore above repositories are referenced inside Argo CD Application resources.
Create webhooks in gitea to let Argo CD know when changes have been pushed to the gitea repositories.
Use the webhook urls in the list above.

## Change remotes in local git repo

After the initial checkout from GitHub we now want to push changes to gitea.
In the repository, change the remote accordingly. Example for k8-mdd:
```
git remote remove origin
git remote add origin http://infra-gitea-http.default.svc.cluster.local/gitea-admin/k8-mdd.git
git push --set-upstream origin main
```

## Argo CD

Proceed with `helm dependency update ./argocd` and `helm upgrade --install argocd ./argocd --namespace argocd --create-namespace`.
Open https://argocd-server.argocd.svc.cluster.local in your browser.
Run the batch file 'print-argocd-admin-password.bat' and enter the credentials into the login page of argocd.


docker build -t urllib3-docker ./urllib3-docker

change upstream
git remote add local-git http://infra-gitea-http.default.svc.cluster.local/gitea-admin/mdd-kubernetes.git
git push -u local-git --all