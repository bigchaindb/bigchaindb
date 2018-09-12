# nginx_3scale agent
nginx_3scale agent is a module that is responsible for providing authentication,
authorization and metering of BigchainDB API users, by communicating with 3scale.
We use the openresty for this, which is nginx bundled with lua libraries.
More information at their [website](openresty.org/en)

It validates the tokens sent by users in HTTP headers.
The user tokens map directly to the Application Plan specified in 3scale.

## Build and Push the Latest Container
Use the `docker_build_and_push.bash` script to build the latest docker image
and upload it to Docker Hub.
Ensure that the image tag is updated to a new version number to properly
reflect any changes made to the container.


## Working

* We define a [lua module](./nginx.lua.template) and
  custom hooks (lua functions to be executed at certain phases of the nginx
  request processing lifecycle) to authenticate an API request.

* Download the template available from 3scale which pre-defines all the
  rules defined using the 3scale UI for monitoring, and the basic nginx
  configuration.

* We heavily modify these templates to add our custom functionality.

* The nginx_3scale image reads the environment variables and accordingly
  creates the nginx.conf and nginx.lua files from the templates.

* Every request calls the `_M.access()` function. This function extracts the
  `app_id` and `app_key` from the HTTP request headers and forwards it to
  3scale to see if a request is allowed to be forwarded to the BigchainDB
  backend. The request also contains the
  various parameters that one would like to set access policies on. If the
  `app_id` and `app_key` is successful, the access rules for the parameters
  passed with the request are checked to see if the request can pass through.
  For example, we can send a parameter, say `request_body_size`, to the 3scale
  auth API. If we have defined a rule in the 3scale dashboard to drop
  `request_body_size` above a certain threshold, the authorization will fail
  even if the `app_id` and `app_key` are valid.

* A successful response from the auth API causes the request to be proxied to
  the backend. After a backend response, the `_M.post_action_content` hook is
  called. We calculate details about all the metrics we are interested in and
  form a payload for the 3scale reporting API. This ensures that we update
  parameters of every metric defined in the 3scale UI after every request.

* Note: We do not cache the keys in nginx so that we can validate every request
  with 3scale and apply plan rules immediately. We can add auth caching to
  improve performance, and in case we move to a fully post-paid billing model.

* Refer to the references made in the [lua module](./nginx.lua.template) for 
  more details about how nginx+lua+3scale works

* For HTTPS support, we also need to add the signed certificate and the
  corresponding private key to the folder
  `/usr/local/openresty/nginx/conf/ssl/`. Name the pem-encoded certificate as
  `cert.pem` and the private key as `cert.key`.
