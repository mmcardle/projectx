FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1

##### We require some dev packages to install python requirements
RUN apt-get -y update && apt-get install --no-install-recommends -y \
  python3.9 \
  python3.9-dev \
  python3 \
  python3-dev \
  python3-venv \
  python3-pip \
  python3-setuptools \
  libssl-dev \
  gcc \
  nginx \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

RUN groupadd user && useradd --create-home --home-dir /home/user -g user user

WORKDIR /home/user/

##### Installing base python dependancies
RUN python3.9 -m pip install -U pip
RUN python3.9 -m pip install circus pipenv uvicorn

COPY Pipfile /home/user/
COPY Pipfile.lock /home/user/

ENV PIPENV_VENV_IN_PROJECT=1
RUN pipenv install

COPY backend/app/ ./backend/app/
RUN chown -R user:user /home/user/backend/

##### Adding configuration files ######
COPY backend/config/ /home/user/config/
RUN rm /etc/nginx/sites-enabled/default /etc/nginx/nginx.conf
RUN ln -s /home/user/config/nginx.conf /etc/nginx/nginx.conf
RUN ln -s /home/user/config/backend-nginx.conf /etc/nginx/sites-enabled/backend-nginx.conf
RUN ln -s /home/user/config/general-security-headers.conf /etc/nginx/snippets/general-security-headers.conf

RUN chmod +x /home/user/config/start.sh

RUN mkdir -p /var/www/
RUN chown -R user:user /var/www/

## NGINX permissions
RUN mkdir /var/cache/nginx
RUN chown -R user:user /var/cache/nginx /var/log/nginx /var/lib/nginx /etc/nginx/conf.d
RUN touch /var/run/nginx.pid
RUN chown -R user:user /var/run/nginx.pid

COPY frontend/build/ /home/user/frontend/

RUN \
  SECRET_KEY="secret"\
  DATABASE_URL='psql://postgres:dummy@postgres:5432/postgres'\
  DEBUG="True"\
  CHANNELS_REDIS_URL="redis://redis:6379/20"\
  CACHE_URL="redis://redis:6379/1"\
  PUBLIC_IP="127.0.0.1"\
  /home/user/.venv/bin/python /home/user/backend/app/manage.py collectstatic

USER user

EXPOSE 8000

CMD /home/user/config/start.sh
