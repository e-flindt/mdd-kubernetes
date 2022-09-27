@ECHO OFF
ECHO Dashboard admin token:
kubectl -n kubernetes-dashboard create token admin-user
PAUSE