<!---
Copyright BigchainDB GmbH and BigchainDB contributors
SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
Code is Apache-2.0 and docs are CC-BY-4.0
--->

# Set Up NGINX

If you don't want HTTPS
(for communications between the external world and your node),
then you can skip all the NGINX steps on this page.

Note: This simple deployment template uses NGINX for more than just HTTPS.
For example, it also does basic rate limiting.

## Install NGINX

SSH into your machine and install NGINX:

```
sudo apt update
sudo apt install nginx
```

## Configure & Reload NGINX

Get an SSL certificate for your node's subdomain (such as `bnode.example.com`).

* Copy the SSL private key into `/etc/nginx/ssl/cert.key`
* Create a "PEM file" (text file) by concatenating your SSL certificate with all intermediate certificates (_in that order, with the intermediate certs last_).
* Copy that PEM file into `/etc/nginx/ssl/cert.pem`
* In the
  [bigchaindb/bigchaindb repository on GitHub](https://github.com/bigchaindb/bigchaindb),
  find the file `nginx/nginx.conf` and copy its contents to
  `/etc/nginx/nginx.conf` on your machine (i.e. replace the existing file there).
* Edit that file (`/etc/nginx/nginx.conf`): replace the two instances of
  the string `example.testnet2.com`
  with your chosen subdomain (such as `bnode.example.com`).
* Reload NGINX by doing:
  ```
  sudo service nginx reload
  ```
