# TODO

- openfaas
- k8s

## 前端

需要安装nodejs，在webapp文件夹下，

```bash
npm install
npm run serve
```

前端程序默认启动于 localhost:8080。

前端已经初步编写了一个 dockerfile，访问后端的接口暂时固定为
```
export const BASE_URL = "http://localhost:5000";
```

用以下命令构建 docker 镜像并启动容器。

```bash
docker build -t todo-frontend .
docker run -d --name todo-frontend -p 8080:8080 todo-frontend
```


## Openfaas

环境配置比较复杂，下面以Ubuntu 22.04 EC2 为例。

安装依赖，都是必要组件

```bash
# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Install Docker socat conntrack
sudo apt-get update 
sudo apt-get install docker.io socat conntrack -y

# Install arkade
curl -sLS https://get.arkade.dev | sudo sh

# Install faas-cli
curl -sL https://cli.openfaas.com | sudo sh

sudo sysctl fs.protected_regular=0
```

切到 root 用户

```
sudo -i
```

启动minikube和openfaas

```bash
minikube start --kubernetes-version=v1.22.0 HTTP_PROXY=https://minikube.sigs.k8s.io/docs/reference/networking/proxy/ --extra-config=apiserver.service-node-port-range=6000-32767 disk=20000MB --vm=true --driver=none

arkade install openfaas

# Forward the gateway to your machine
kubectl rollout status -n openfaas deploy/gateway
# kubectl port-forward -n openfaas svc/gateway 8080:8080 &

# If basic auth is enabled, you can now log into your gateway:
PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n $PASSWORD | faas-cli login --username admin --password-stdin
```

现在应该可以访问 `public IP: 31112` 访问 OpenFaas管理界面，注意设置EC2的防火墙规则为允许所有流量。

默认用户名是`admin`，密码通过 `echo $PASSWORD` 获得。



## MySQL

拉取MySQL docker镜像并启动容器。

- 设置启动时运行 ./mysql/db.sql，初始化数据库
- 设置root密码为123456

```bash
# build container
docker pull mysql
docker run --name mysql -p 3306:3306 -v $PWD/mysql:/docker-entrypoint-initdb.d:ro -e MYSQL_ROOT_PASSWORD=123456 -d mysql
```

如果需要调试，可以用如下命令打开MySQL cmd

 ```bash
 docker exec -it mysql mysql -p
 ```

## TF Service

从TFHub下载模型，解压到 ./model 文件夹下

```bash
curl -L "https://tfhub.dev/google/imagenet/efficientnet_v2_imagenet21k_ft1k_s/classification/2?tf-hub-format=compressed" -o efficientnet_v2_imagenet21k_ft1k_s.tar.gz

mkdir -p ./model
tar -xzf efficientnet_v2_imagenet21k_ft1k_s.tar.gz -C ./model
```

8501 端口是 TF Service 的 RestFul API 端口

容器启动之后，访问 [localhost:8501/v1/models/efficientnet_v2_imagenet21k_ft1k_s/metadata](http://localhost:8501/v1/models/efficientnet_v2_imagenet21k_ft1k_s/metadata) 应该能看到一些 metadata

```bash
# build container
docker pull tensorflow/serving
docker run --name tf -d -p 8501:8501 -p 8500:8500 -v $PWD/model:/models/efficientnet_v2_imagenet21k_ft1k_s/2 -e MODEL_NAME=efficientnet_v2_imagenet21k_ft1k_s tensorflow/serving
```

## MINIO

一个分布式存储服务，可以用来存图片。

```bash
docker run -p 9000:9000 -p 9090:9090 -d --name minio -v $PWD/minio/data:/data -e "MINIO_ROOT_USER=root" -e "MINIO_ROOT_PASSWORD=12345678" quay.io/minio/minio server /data --console-address ":9090"
```