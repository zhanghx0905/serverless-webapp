export TF_SERVER_HOST=$(kubectl get service tensorflow-serving-service -o jsonpath='{.spec.clusterIP}')
export MYSQL_HOST=$(kubectl get service mysql-service -o jsonpath='{.spec.clusterIP}')
export MINIO_HOST=$(kubectl get service minio-service -o jsonpath='{.spec.clusterIP}')

flask run