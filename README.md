# findMe backend

This repository contains the backend for the `findMe` application. `findMe` is a social media platform where users can
follow each other and engage in a unique game of location riddles.

In this game, users post photos containing a geolocation. Other users then have to guess as precisely as possible where
the photo was taken. The closer the guess, the higher the score. This creates a fun and engaging way for users to test
their geographical knowledge and observational skills.

The backend is composed of three microservices:

- `findme-location-riddles`: Handles the creation and management of location riddles.
- `findme-scores`: Manages the scoring system based on how accurately users guess the locations.
- `findme-users`: Manages user profiles, including follow relationships.

Each microservice is developed using Python, and they are all deployed using Docker and Serverless. The backend API can
be accessed locally for development purposes.

Please refer to the sections below for detailed instructions on local development setup, hot reloading, common problems,
how to get a token for development, and how to run tests.

## Local Development

### Prerequisites

- Docker
- [LocalStack CLI](https://docs.localstack.cloud/getting-started/installation/#localstack-cli)
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
2. install all serverless dependencies with `npm install` in the root directory
2. using python3.12 create a virtual environment inside each microservice directory py running `python -m venv .venv`
3. activate the environment to use the local project pip and python
4. install dependencies with:
    1. `pip install -r requirements.txt --platform manylinux2014_x86_64 --only-binary=:all: -t .venv/lib/python3.12/site-packages`
5. start the localstack container with `localstack start`
6. run `sh deploy.sh --stage local` to deploy the services (or `sls deploy --stage local` first in the `/infrastructure`
   directory and then in the root directory)
6. access the backend API
   on [http://localhost:4566/restapis/findme/local/_user_request_/](http://localhost:4566/restapis/findme/local/_user_request_/)
7. add new dependencies by extending the `requirements.txt` file in the microservice directory

### Hot reloading

With this setup the lambda functions are configured to automatically hot reload. This means that if you perform a change
in e.g findme-users/ you will see the change after saving without redeploying.

### Common Problems

- verify that you're using the specified python version to create the virtual environment
- double-check the absolute path in the `sls-config-local.yml` file
- The properties in the `sls-config-local.yml` file have to be named exactly like serverless names the cloudformation
  resources, double-check that the names match to the ones in `.serverless/cloudformation-template-update-stack.json`

### Testing

> :warning: Caution: We have to use a different virtual environment while testing as during the setup, because we run
> the tests locally on our device and do not mount them into the lambda function.
> To do this either create a seperate venv outside or replace the one inside the microservice directory.
>
>`python -m venv .venv`
>
>`.venv/bin/pip install -r <path_to>/requirements.txt`

To run the tests for the microservices, run ` python -m unittest discover` from the backend root.
(If the virtual environment hasn't been activated yet, you can do so by running the
command ` source .venv/bin/activate`.)

### Token

To get a token for developing use the following curl command:

```
curl --request POST \
  --url https://findme-dev.eu.auth0.com/oauth/token \
  --header 'content-type: application/json' \
  --data '{"client_id":"0FhpaZeIjhSG1lwNR3RWPI20VgLgU5rk",
            "client_secret":<client_secret>,
            "audience":"https://findme-dev.eu.auth0.com/api/v2/","grant_type":"client_credentials"}'
```

### Documentation

For the detailed api documentation start the application as described above and visit the following endpoints:

- `{your_application_url}/users/swagger`
- `{your_application_url}/location-riddles/swagger`

### Tips and Tricks

This file is a collection of useful tips and tricks which facilitate the development process.

#### Inspecting table content

- By running `awslocal dynamodb scan --table-name FollowerTable --region eu-central-2` in the terminal, one can inspect
  the FollowerTable content
- By running `awslocal dynamodb scan --table-name usersTable --region eu-central-2` in the terminal, one can inspect the
  FollowerTable content