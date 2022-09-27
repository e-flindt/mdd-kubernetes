:: https://github.com/vfarcic/argo-combined-demo
@ECHO OFF
helm upgrade --install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx
helm dependency update ./infra
timeout /t 20 /nobreak
helm upgrade --install infra ./infra
helm dependency update ./argocd
helm upgrade --install argocd ./argocd --namespace argocd --create-namespace