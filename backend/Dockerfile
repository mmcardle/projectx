FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1

##### We require some dev packages to install python requirements
RUN apt-get -y update && apt-get install --no-install-recommends -y \
  python3.11 \
  python3.11-dev \
  python3 \
  python3-dev \
  python3-venv \
  python3-pip \
  python3-setuptools \
  python-is-python3 \
  libssl-dev \
  libffi-dev \
  gcc \
  nginx \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

RUN groupadd user && useradd --create-home --home-dir /home/user -g user user

WORKDIR /home/user/

##### Installing base python dependancies
RUN python3.11 -m pip install -U pip
RUN python3.11 -m pip install circus poetry

COPY pyproject.toml /home/user/
COPY poetry.toml /home/user/
COPY poetry.lock /home/user/

ENV LANG en_GB.utf8
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry install --no-dev

COPY backend/manage.py ./manage.py
RUN chown user:user /home/user/manage.py

COPY backend/projectx/ ./projectx/
RUN chown -R user:user /home/user/projectx/

##### Adding configuration files ######
COPY backend/config/circus.ini /home/user/config/
COPY backend/config/nginx.conf /home/user/config/
COPY backend/config/backend-nginx.conf /home/user/config/
COPY backend/config/general-security-headers.conf /home/user/config/
RUN rm /etc/nginx/sites-enabled/default /etc/nginx/nginx.conf
RUN ln -s /home/user/config/nginx.conf /etc/nginx/nginx.conf
RUN ln -s /home/user/config/backend-nginx.conf /etc/nginx/sites-enabled/backend-nginx.conf
RUN ln -s /home/user/config/general-security-headers.conf /etc/nginx/snippets/general-security-headers.conf

RUN mkdir -p /var/www/
RUN chown -R user:user /var/www/

## NGINX permissions
RUN mkdir /var/cache/nginx
RUN chown -R user:user /var/cache/nginx /var/log/nginx /var/lib/nginx /etc/nginx/conf.d
RUN touch /var/run/nginx.pid
RUN chown -R user:user /var/run/nginx.pid

COPY frontend/dist/ /home/user/frontend/

RUN \
  SECRET_KEY="secret"\
  DATABASE_URL='psql://postgres:dummy@postgres:5432/postgres'\
  DEBUG="True"\
  CHANNELS_REDIS_URL="redis://redis:6379/20"\
  CACHE_URL="redis://redis:6379/1"\
  PUBLIC_IP="127.0.0.1"\
  poetry run python manage.py collectstatic

# Adding Entry Point
COPY backend/config/start.sh /home/user/config/
RUN chmod +x /home/user/config/start.sh
RUN chown user:user /home/user/config/start.sh

USER user

EXPOSE 8000

CMD /home/user/config/start.sh
