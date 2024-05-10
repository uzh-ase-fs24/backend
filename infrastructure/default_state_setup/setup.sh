#!/bin/bash

# Define the table name
USERS_TABLE_NAME="usersTable"
FOLLOWERS_TABLE_NAME="FollowerTable"
LOCATION_RIDDLES_TABLE_NAME="locationRiddleTable"
REGION="eu-central-2"
LOCATION_RIDDLES_BUCKET="ase-findme-image-upload-bucket"

# Initialize command line options as false
LOAD_CONNECTIONS="false"
LOAD_LOCATION_RIDDLES="false"
LOAD_USERS="false"

while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        --connections)
        LOAD_CONNECTIONS="true"
        shift # past argument
        ;;
        --location-riddles)
        LOAD_LOCATION_RIDDLES="true"
        shift # past argument
        ;;
        --users)
        LOAD_USERS="true"
        shift # past argument
        ;;
        --all)
        LOAD_CONNECTIONS="true"
        LOAD_LOCATION_RIDDLES="true"
        LOAD_USERS="true"
        shift # past argument
        ;;
        *)    # unknown option
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

if [ "$LOAD_USERS" == "true" ]; then
  while IFS= read -r row; do
    username=$(echo "$row" | jq -r '.username.S')
    echo "adding $username"
    awslocal dynamodb put-item --table-name $USERS_TABLE_NAME --item="$row" --region $REGION
  done < <(jq -c '.Items[]' infrastructure/default_state_setup/dynamodb/default_users.json)
fi

if [ "$LOAD_CONNECTIONS" == "true" ]; then
  while IFS= read -r row; do
    connection=$(echo "$row" | jq -r '.sort_key.S')
    type=$(echo "$row" | jq -r '.partition_key.S')
    echo "adding connection $connection $type"
    awslocal dynamodb put-item --table-name $FOLLOWERS_TABLE_NAME --item="$row" --region $REGION
  done < <(jq -c '.Items[]' infrastructure/default_state_setup/dynamodb/default_connections.json)
fi

if [ "$LOAD_LOCATION_RIDDLES" == "true" ]; then
  while IFS= read -r row; do
    location_riddle=$(echo "$row" | jq -r '.location_riddle_id.S')
    username=$(echo "$row" | jq -r '.username.S')
    echo "adding location_riddle $location_riddle by $username"
    awslocal dynamodb put-item --table-name $LOCATION_RIDDLES_TABLE_NAME --item="$row" --region $REGION
    echo "uploading image"
    awslocal s3api put-object --bucket $LOCATION_RIDDLES_BUCKET --key location-riddles/${location_riddle}.png --body infrastructure/default_state_setup/s3/location_riddle_images/${location_riddle}.png
  done < <(jq -c '.Items[]' infrastructure/default_state_setup/dynamodb/default_location_riddles.json)
fi