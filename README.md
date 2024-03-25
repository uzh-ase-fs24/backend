# findme backend

The backend consists of three microservices

- findme-location-riddles
- findme-scores
- findme-users

## Local Development

### Prerequisites

- Docker
- [LocalStack CLI](https://docs.localstack.cloud/getting-started/installation/#localstack-cli)
- [poetry](https://python-poetry.org)
- [serverless](https://www.serverless.com)

### Setup

1. create a sls-config-local.yml file in the root directory with the following content:
    ```yaml
    FindmeDashusersLambdaFunction:
      Properties:
        Code:
          S3Bucket: hot-reload
          S3Key: <absoloute-path-to-repository>/workspace/backend/findme-users
    FindmeDashlocationDashriddlesLambdaFunction:
      Properties:
        Code:
          S3Bucket: hot-reload
          S3Key: <absoloute-path-to-repository>/workspace/backend/findme-location-riddles
    ```
   verify that the paths are absolute and point to the correct directories
2. using python3.12 create a virtual environment inside each microservice directory py running `python -m venv .venv`
3. generate requirements.txt file by running `poetry export --without-hashes -f requirements.txt -o requirements.txt`
4. install dependencies with:
    1. `pip install -r requirements.txt --platform manylinux2014_x86_64 --only-binary=:all: -t .venv/lib/python3.12/site-packages`
5. run `sh deploy.sh --stage local` to deploy the services (or `sls deploy --stage local` in each microservice directory
   including `/infrastructure`)
6. access the backend API
   on [http://localhost:4566/restapis/findme/local/_user_request_/](http://localhost:4566/restapis/findme/local/_user_request_/)
7. add new dependencies with `poetry add <package-name>` if something is not working verify that the correct platform is
   installed (also not the default with pydantic, see 3.)

### Hot reloading

With this setup the lambda functions are configured to automatically hot reload. This means that if you perform a change
in e.g findme-users/ you will instantly see the change after saving.
