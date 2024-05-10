# findme-users Microservice

This microservice is a part of the `findMe` application's backend. It is responsible for managing user profiles, including follow relationships

In the `findMe` application, users post photos containing a geolocation. Other users then have to guess as precisely as possible where the photo was taken. The closer the guess, the higher the score. This microservice handles the logic related to these users.

## Local Development

### Prerequisites

- Python 3.12
- pip
- Docker
- [LocalStack CLI](https://docs.localstack.cloud/getting-started/installation/#localstack-cli)
- [serverless](https://www.serverless.com)

### Setup
follow the instructions in the [README.md](../README.md) file in the root directory of the repository.