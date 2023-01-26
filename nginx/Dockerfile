# build web app - base image
FROM node:18.13-alpine3.17 as build-stage

# set working directory
WORKDIR /app

# install app and project dependencies
COPY ./frontend/ui/package.json /app/package.json
COPY ./frontend/ui/package-lock.json /app/package-lock.json

RUN npm install
RUN npm install -g @vue/cli@latest

# copy files
COPY ./frontend/ui .

# fixing node_modules permission error
# source: https://stackoverflow.com/questions/67087735/eacces-permission-denied-mkdir-usr-app-node-modules-cache-how-can-i-creat
RUN mkdir -p /app/node_modules/.cache && chmod -R 777 /app/node_modules/.cache

RUN npm run build


# nginx
FROM nginx:stable-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY ./nginx/etc/ /etc/nginx
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]