FROM node:lts

COPY frontend /frontend
WORKDIR /frontend
RUN npm install

ENV CI true
ENV CHOKIDAR_USEPOLLING true
ENV HOST 127.0.0.1

CMD ["npm", "start"]