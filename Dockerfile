FROM node:16-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY next.config.js ./next.config.js

COPY .env.local ./
COPY .env ./

COPY api-lib ./api-lib
COPY assets ./assets
COPY components ./components
COPY lib ./lib
COPY page-components ./page-components
COPY pages ./pages
COPY public ./public
COPY jsconfig.json ./

CMD ["npm", "run", "dev"]