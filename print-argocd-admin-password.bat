@ECHO OFF
ECHO Username: admin
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" > encoded-argo-token.txt
certutil -decode ./encoded-argo-token.txt ./decoded-argo-token.txt
del encoded-argo-token.txt
ECHO Password:
type decoded-argo-token.txt
del decoded-argo-token.txt
ECHO:
PAUSE