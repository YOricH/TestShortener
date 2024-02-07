FROM python:3.11-alpine
MAINTAINER Alexey Slavin <yorich87@gmail.com>

RUN \
    apk update && apk --no-cache add libpq-dev && \
    apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
    pip install --no-cache-dir pip pipenv gunicorn psycopg2 hiredis -U && \
    apk --purge del .build-deps
WORKDIR /app
COPY Pipfile* /app
RUN pipenv install --ignore-pipfile --deploy --system
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY . /app
ENTRYPOINT ["/app/entrypoint.sh"]