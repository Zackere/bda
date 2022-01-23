FROM node:latest

COPY package.json /app/
COPY serve.js /app/


WORKDIR /app
RUN npm install
EXPOSE 80
ENTRYPOINT [ "node", "serve.js" ]