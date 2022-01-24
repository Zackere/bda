FROM node:latest

COPY package.json /app/

WORKDIR /app
RUN npm install
EXPOSE 80

COPY serve.js /app/
ENTRYPOINT [ "node", "serve.js" ]
