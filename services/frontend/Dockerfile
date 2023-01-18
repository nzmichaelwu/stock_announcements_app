# base image
FROM node:18.13-alpine3.17

# set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH

# install app and project dependencies
COPY ./ui/package.json /app/package.json
COPY ./ui/package-lock.json /app/package-lock.json

RUN npm install
RUN npm install -g @vue/cli@latest

# fixing node_modules permission error
# source: https://stackoverflow.com/questions/67087735/eacces-permission-denied-mkdir-usr-app-node-modules-cache-how-can-i-creat
RUN mkdir -p /app/node_modules/.cache && chmod -R 777 /app/node_modules/.cache

# copy files
COPY ./ui /app

CMD npm run serve