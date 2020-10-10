FROM ubuntu:18.04

##### We require some dev packages to install python requirements
RUN apt-get -y update && apt-get install --no-install-recommends -y \
  python3.8 \
  python3.8-dev \
  python3 \
  python3-dev \
  python3-venv \
  python3-pip \
  python3-setuptools \
  libssl-dev \
  gcc \
  nginx \
  && rm -rf /var/lib/apt/lists/*

RUN groupadd user && useradd --create-home --home-dir /home/user -g user user

WORKDIR /home/user/app/backend

##### Installing pip wheel virtualenv circus
RUN python3.8 -m pip install -U pip
RUN python3.8 -m pip install pip wheel virtualenv circus pip-tools

##### Creating virtualenv at /home/user/venv
RUN virtualenv -p python3.8 /home/user/venv

COPY backend/requirements.in ./

RUN pip-compile requirements.in > requirements.txt
RUN /home/user/venv/bin/pip install -r requirements.txt

COPY backend/manage.py /home/user/app/backend/manage.py
COPY backend/projectx/ /home/user/app/backend/projectx/
COPY backend/templates/ /home/user/app/backend/templates/
COPY backend/users/ /home/user/app/backend/users/

RUN chown -R user:user /home/user/app/backend/

##### Adding configuration files ######
RUN rm /etc/nginx/sites-enabled/default
COPY backend/nginx.conf /etc/nginx/nginx.conf
COPY backend/backend-nginx.conf /etc/nginx/sites-enabled/backend-nginx.conf
COPY backend/general-security-headers.conf /etc/nginx/snippets/general-security-headers.conf
COPY backend/uwsgi.ini /home/user/config/uwsgi.ini
COPY backend/circus.ini /home/user/config/circus.ini
COPY backend/start.sh /home/user/start.sh
RUN chmod +x /home/user/start.sh

RUN mkdir -p /var/www/
RUN chown -R user:user /var/www/
RUN usermod -a -G adm user
RUN chmod g+w /var/log/nginx/error.log

## NGINX permissions
RUN mkdir /var/cache/nginx
RUN chown -R user:user /var/cache/nginx 
RUN chown -R user:user /var/log/nginx
RUN chown -R user:user /var/lib/nginx
RUN chown -R user:user /etc/nginx/conf.d
RUN touch /var/run/nginx.pid
RUN chown -R user:user /var/run/nginx.pid

RUN /home/user/venv/bin/pip install django-extensions

USER user

CMD /home/user/start.sh