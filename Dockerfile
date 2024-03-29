FROM nikolaik/python-nodejs:python3.12-nodejs21

# Install serverless dependencies
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
 && npm install -g serverless


WORKDIR /app

COPY . /app

RUN npm install

EXPOSE 4566

RUN chmod +x deploy.sh
CMD ["sh", "deploy.sh"]
