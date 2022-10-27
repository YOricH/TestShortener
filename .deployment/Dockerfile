FROM python:3.10-alpine
MAINTAINER Alexey Slavin <yorich87@gmail.com>

RUN apk update && apk add libpq
RUN apk add --virtual .build-deps gcc python3-dev musl-dev postgresql-dev
RUN pip install --no-cache-dir pip pipenv gunicorn psycopg2 hiredis -U
RUN apk del .build-deps
WORKDIR /app
COPY Pipfile* /app
RUN pipenv install --ignore-pipfile --deploy --system
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY . /app
ENTRYPOINT ["/app/entrypoint.sh"]