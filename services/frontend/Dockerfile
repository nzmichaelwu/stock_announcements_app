# base image
FROM node:18.13-alpine3.17

# set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
# ENV PATH /app/node_modules/.bin:$PATH

# install app and project dependencies
COPY ./ui/package.json /app/package.json
COPY ./ui/package-lock.json /app/package-lock.json
RUN npm install
RUN npm install -g @vue/cli@latest

# copy files
COPY ./ui /app

CMD npm run serve