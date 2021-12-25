FROM node:latest

COPY package.json /app/
COPY serve.js /app/

COPY pollution/berlin.json /app/data/pollution/
COPY pollution/delhi.json /app/data/pollution/
COPY pollution/moscow.json /app/data/pollution/
COPY pollution/warsaw.json /app/data/pollution/

COPY weather/berlin.json /app/data/weather/
COPY weather/delhi.json /app/data/weather/
COPY weather/moscow.json /app/data/weather/
COPY weather/warsaw.json /app/data/weather/


WORKDIR /app
RUN npm install
EXPOSE 80
ENTRYPOINT [ "node", "serve.js" ]