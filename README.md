# IMS
For job interview application
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