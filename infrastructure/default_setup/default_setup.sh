#!/bin/bash

# Define the table name
USERS_TABLE_NAME="usersTable"
REGION="eu-central-2"

# Loop through each item in the JSON array
for row in $(jq -c '.[]' infrastructure/default_setup/default_users.json); do
  # Use awslocal to put the item into the DynamoDB table
  username=$(echo $row | jq -r '.username.S')
  echo "adding $username"
  awslocal dynamodb put-item --table-name $USERS_TABLE_NAME --item $row --region $REGION
done