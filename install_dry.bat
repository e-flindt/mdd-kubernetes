@ECHO OFF
helm upgrade --dry-run --debug --install ingress-nginx ingress-nginx --repo https://kubernetes.github.io/ingress-nginx
helm dependency update ./infra
helm install test --dry-run --debug ./infra