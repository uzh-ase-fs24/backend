FROM nikolaik/python-nodejs:python3.12-nodejs21

# Install serverless dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
 && npm install -g serverless

RUN apt-get install -y jq
RUN pip install awscli awscli-local

WORKDIR /app

COPY . /app

RUN npm install

EXPOSE 4566

RUN chmod +x deploy.sh
CMD ["bash", "deploy.sh", "--stage", "dev", "--load-default-state"]
