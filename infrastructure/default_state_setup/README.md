# Default State Setup

This module is responsible for setting up a default state of the application. This includes populating the databases
with sample user data and content. It is used for testing to avoid manual setup of user connections and content.

## Usage

The default state can be setup by running (always use this tool from the `workspace/backend` directory):

```bash
sh infrastructure/default_state_setup/setup.sh
```

The script is also automatically called when starting the application via docker or when using the deployment (in
workspace/backend) script like this

```bash
sh deploy.sh --setup-default-state --all
```

you can also specify only setup the user state / location riddle state or connections state individually with the
commandline options:

```
--connections
--location-riddles
--users
```

### Important

- The application must be deployed and running locally
- If you setup states individually beware that some relate to others by ID or username

## Structure

The sample application state is stored in the following directory structure:

```
/infrastructure
  /default_state_setup
    /dynamodb
      -- default_connections.json
      -- default_location_riddles.json
      -- default_users.json
    /s3
      /location_riddle_images
        -- uuid1.png
        -- uuid2.png
        -- uuid3.png
        -- ...  .png
```

The json files are dumps of the dynamodb databases and gan be generated like this:

```bash
awslocal dynamodb scan --table-name <table_name> > infrastructure/default_state_setup/dynamodb/default_<filename>.json
```

### Important:

- ids of location riddles in dynamodb and filename of images in bucket must match
- usernames in dynamodb must match usernames in the userpool of auth0
- The easiest way to generate the database dumps is by running the application and creating the desired state manually