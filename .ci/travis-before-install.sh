#!/bin/bash

apt-get update -qq
wget https://github.com/miloyip/rapidjson/archive/v1.1.0.tar.gz -O /tmp/v1.1.0.tar.gz
tar -xvf /tmp/v1.1.0.tar.gz
cp -r $PWD/rapidjson-1.1.0/include/rapidjson /usr/include/


curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && chmod +x minikube
curl -Lo kubectl https://storage.googleapis.com/kubernetes-release/release/v1.8.0/bin/linux/amd64/kubectl && chmod +x kubectl

export MINIKUBE_WANTUPDATENOTIFICATION=false
export MINIKUBE_WANTREPORTERRORPROMPT=false
export MINIKUBE_HOME=$HOME
export CHANGE_MINIKUBE_NONE_USER=true
mkdir $HOME/.kube || true
touch $HOME/.kube/config

export KUBECONFIG=$HOME/.kube/config
./minikube start --vm-driver=none

# this for loop waits until kubectl can access the api server that Minikube has created
for i in {1..150}; do # timeout for 5 minutes
    ./kubectl get po &> /dev/null
    if [ $? -ne 1 ]; then
        break
    fi
    sleep 2
done
