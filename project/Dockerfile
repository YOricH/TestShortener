FROM python:3.7-slim
MAINTAINER Alexey Slavin <yorich87@gmail.com>
COPY requirements.txt ./
RUN set -ex && RUN_DEPS="libpcre3 python3-dev default-libmysqlclient-dev" && BUILD_DEPS="build-essential libpcre3-dev libpq-dev" \
&& apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS $RUN_DEPS \
&& pip install --no-cache-dir -r requirements.txt \
&& apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
&& rm -rf /var/lib/apt/lists/*
COPY . .
EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=project.settings
ENV UWSGI_WSGI_FILE=project/wsgi.py
ENV UWSGI_HTTP=:8000 UWSGI_MASTER=1 UWSGI_HTTP_AUTO_CHUNKED=1 UWSGI_HTTP_KEEPALIVE=1 UWSGI_UID=root UWSGI_GID=root UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy
ENV UWSGI_WORKERS=2 UWSGI_THREADS=4

CMD ["/usr/local/bin/uwsgi", "--show-config"]


