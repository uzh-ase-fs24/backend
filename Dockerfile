FROM node:18-bullseye

# Install serverless dependencies
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    netcat \
 && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1 \
 && pip3 install --upgrade pip \
 && npm install -g serverless


WORKDIR /app

COPY . /app

RUN npm install

EXPOSE 4566

RUN chmod +x deploy.sh
CMD ["sh", "deploy.sh"]
