# IMS - Inventory Management System
Initially for a job interview homework assignment,
I've been using this as an opportunity to learn a Kubernetes and writing containerized
web applications. This application uses Flask and MongoDB, connecting to ElasticSearch 
for searching.

## Prerequisites
This requires a working Kubernetes with kubectl access, Docker, and helm installed.
I used Docker Desktop on Windows, and win-get to install the other applications.

## MongoDB Setup
Run the following to install MongoDB via helm on an existing kubernetes:
```
helm install my-release oci://registry-1.docker.io/bitnamicharts/mongodb
```
This will install and run a mongodb deployment, you will need to extract the password. If the above call was successful,
it will show you how to do this and set it to an environment variable. However, I just wanted the text, so I used:
```
kubectl get secret --namespace default my-release-mongodb -o jsonpath="{.data.mongodb-root-password}"
Output: something like supersecretpwd==
```
This "supersecretpwd==" should be placed in "iws-secrets.yml".
After this, we need to install the secrets into kubernetes: 
```
kubectl apply -f ims-secrets.yml
```

## ElasticSearch Setup (Optional)
I have a trial of the ElasticSearch Cloud API that I've been using.
If you want to plug in your own API. Modify the ims-secrets file with your info:
```
  elastic_cloud_id: base64cloudid
  elastic_user_password: base64password
```
This will need to applied via: 
```
kubectl apply -f ims-secrets.yml
```
You will need to have an index called "search-ims-prod" already set up in ElasticSearch.

## Flask Setup
Build the image to be deployed: 
```
Docker build . -t ims-image
```
Deploy to kubernetes: 
```
kubectl apply -f ims-deployment.yml
```

## Using the Website
Navigate to 127.0.0.1:5000, and you will see a basic webpage
with some of the backend features being used. At first, there
will be no products. Under the "Admin" - "Product Management" page, there
is an option to import sample data. After this is created, you should
be able to refresh and play around with the normal website.