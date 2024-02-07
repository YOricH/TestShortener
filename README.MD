# Test Shortener
[Русский](./README_RU.MD)|[English](./README.MD)

Example of a service - abbreviation of links (like [bitly.com][6] or [tinyurl.com][8]). 
Users are defined by session.
PostgreSQL is used as a base, but you can easily configure it to
any other available Django.
## Features
- Specifying your aliases
- List of aliases created by the current user with pagination
- caching aliases in Redis
- Auto deletion of old aliases
- REST API
- Easy building with Docker compose or Kubernetes
## Used technologies
- [Python][14]
- [Django][1]
- [Django Rest Framework][2]
- [Redis][3]
- [Celery][4]
- [Gunicorn][11]
- [Bash][13]
- [Make][15]
- [Docker][12]
- [Docker compose][5]
- [Kubernetes][16]
- [Minikube][17]
## Requirements
*It is recommended to use a Unix-like system. The application is tested on Manjaro and Ubuntu.*
### To run without containerization
- Python >= 3.11
- pipenv >= 2022.10
- PostgreSQL >= 14
- Redis >= 7
### To run on Docker Compose
- GNU Make >= 4
- Docker >= 20
- Docker Compose >= 2
### To run on Kubernetes
*The build is tested and tuned for Minikube* 
- GNU Make >= 4
- Minikube >= 1.27
## Installation
Download from source (requires [GIT](https://git-scm.com/))
```sh
$ git clone https://github.com/yorich/TestShortener.git
$ cd TestShortener
```
### Without containerization
1. Install dependencies:
```sh
$ pipenv shell
$ pipenv install --ignore-pipfile
```
2. [Create an empty database PostgreSQL.](https://www.postgresql.org/docs/current/sql-createdatabase.html)
3. If necessary, set environment variables. Or create a .env file in the root of the project where specify them. 
You can use the .env.dist file as an example.
4. Create tables in the specified database:
```sh
$ python manage.py migrate
```
5. If everything is successful, run the test server on the local system:
```sh
$ python manage.py runserver 8000
```
### Docker Compose
1. If necessary, configure the environment variables in the .env.compose file.
2. Run with Make:
```sh
$ make compose.run
```
3. To stop use the command
```sh
$ make compose.stop
```
4. To remove containers, related networks and volumes:
```sh
$ make compose.clear
```
*Downloaded images are not deleted.*
### Minikube
1. If necessary, configure the environment variables in the .env.compose file.
2. Run with Make:
```sh
$ make kube.run
```
3. To stop and delete all created objects:
```sh
$ make kube.clear
```
## Settings
*All settings are made through the environment variables, or through the .env file (.env.compose if you use containers).*
- DATABASE_URI - database connection string. Mandatory variable.
- ALLOWED_HOSTS - list of hosts / domains for which the current site can operate. Denoted by a comma separated string 
(example: 'example.com,foo.com'). Default: **'localhost,0.0.0.0,127.0.0.1'**.
- SECRET_KEY - [see the documentation.][9] 
- DEBUG - [see the documentation.][10] Default: **False**.  
- CACHE_URL - Redis connection string for cache. Mandatory variable.
- BROKER_URL - connection string to the Redis base for Celery (message broker). Mandatory variable.
- RESULT_BACKEND - connection string to the Redis base for Celery (task results). Mandatory variable.
- USE_CACHE - use cache or not. Default: **True**.
- LOG_LEVEL - logging level. Default: **INFO**.
- USE_LOG_FILE - use log files or not. Default: **False**.
- LOG_FILE_NAME - log file name. Default: **'shortener.log'**.
- PAGINATION_PAGE_SIZE - the number of objects returned through the REST API at one time. Default: **20**.  
- BASE_ENCODING - the string that encodes the original link. Default: **Base56**.
- SUBPART_HASH_LEN - the length of the hash used to encode the section. The higher the number, the longer the resulting link. Default: **11**.
- SESSION_COOKIE_AGE - lifetime of session cookies in seconds. Default: **1209600** (two weeks in seconds).
- DIRECTION_LIFETIME_SEC - alias lifetime in seconds. By default, is equal to **SESSION_COOKIE_AGE**.
- CACHE_ON_CREATE - save an alias in cache when creating. Default: **True**.
- SCHEDULE_CLEAR_DATA_MINUTES - the period of the task to remove obsolete aliases in minutes. Default: **60**. 
- LINES_ON_PAGE - the number of lines of aliases created by the user per page. Default: **PAGINATION_PAGE_SIZE**.
- LAST_TRY_NUM - the number of attempts to create a random alias in the case that the alias by hash coincides with the existing one. Default: **10**.

The rest of the settings are standard for Django and you can [set it][7] how you want in **settings.py** file.

## REST API
### End points
**/api/directions/** - short aliases for links.
##### Available methods
GET, POST, HEAD, OPTIONS

**/api/userdirections/** - short links, associated with users. You can only work with objects belonging to the current user (defined through the session).
##### Available methods
GET, POST, HEAD, OPTIONS

More details can be found by logging in through the browser to **<you_shortener_host>/api/**.

[1]: https://www.djangoproject.com/
[2]: https://www.django-rest-framework.org/
[3]: https://redis.io/
[4]: http://www.celeryproject.org/
[5]: https://docs.docker.com/compose/
[6]: https://bitly.com/
[7]: https://docs.djangoproject.com/en/4.1/topics/settings/
[8]: https://tinyurl.com/
[9]: https://docs.djangoproject.com/en/4.1/ref/settings/#std:setting-SECRET_KEY
[10]: https://docs.djangoproject.com/en/4.1/ref/settings/#std:setting-DEBUG
[11]: https://gunicorn.org/
[12]: https://www.docker.com/
[13]: https://www.gnu.org/software/bash/
[14]: https://www.python.org/
[15]: https://www.gnu.org/software/make/
[16]: https://kubernetes.io/
[17]: https://minikube.sigs.k8s.io/docs/