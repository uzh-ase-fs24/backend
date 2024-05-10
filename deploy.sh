#!/bin/bash

# Default stage
STAGE="dev"
HOST="localstack-main"
LOAD_DEFAULT_STATE="false"

# Parse command line options
while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        --stage)
        STAGE="$2"
        shift # past argument
        shift # past value
        ;;
        --load-default-state)
        LOAD_DEFAULT_STATE="true"
        shift # past argument
        ;;
        *)    # unknown option
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

# Set HOST based on stage
if [ "$STAGE" == "local" ]; then
  HOST="localhost"
fi

while ! nc -z $HOST 4566; do
    echo 'Waiting for LocalStack to be ready...';
    sleep 1;
done;
echo 'LocalStack is up. Deploying Serverless app...';

# Deploy first Serverless service
echo "Deploying infrastructure"
cd infrastructure/apigateway
sls deploy -s $STAGE

# Check if deployment of first service was successful
if [ $? -eq 0 ]; then
  echo "apigateway deployment successful."
else
  echo "Error: apigateway deployment failed."
  exit 1
fi

# Deploy second Serverless service
echo "Deploying second Serverless service..."
cd ../..
sls deploy -s $STAGE

# Check if deployment of second service was successful
if [ $? -eq 0 ]; then
  echo "functions deployment successful."
else
  echo "Error: functions deployment failed."
  exit 1
fi

echo "Deployment of all services completed successfully."

if [ "$LOAD_DEFAULT_STATE" == "true" ]; then
  echo "Adding default setup data..."
  bash infrastructure/default_state_setup/setup.sh --all
fi
