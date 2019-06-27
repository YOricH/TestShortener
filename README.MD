# Test Shortener
[Русский](./README_RU.MD)|[English](./README.MD)

Example of service - abbreviation of links (like [bitly.com][6] or [tinyurl.com][8]). 
Users are defined by session.
MySQL is used as a base, but you can easily configure it to
any other available Django. 

## Features
- Specifying your aliases
- List of aliases created by the current user with pagination
- caching aliases in Redis
- Auto deletion of old aliases
- REST API
- Easy building with Docker compose

## Used technologies
- [Django][1]
- [Django Rest Framework][2]
- [Redis][3]
- [Celery][4]
- [Docker compose][5]

## Requirements
- Docker
- Docker Compose
- MySQL or another DBMS supported by Django

## Installation

1). Installation from source (requires GIT)
```sh
$ git clone https://github.com/yorich/TestShortener.git
$ cd TestShortener/project
```

2). If necessary, set up the environment variables and the docker-compose.yml file (see section **Settings**).

3). Start up with Docker compose:
```sh
$ docker-compose up
```
## Settings
*All settings are made through the environment variables, or through the docker-compose.yml file.*
- DATABASE_URL - database connection string. Mandatory variable. If you plan to use NOT MySQL,
You need to make the appropriate changes to the requirements.txt and Dockerfile files.
- ALLOWED_HOSTS - list of hosts / domains for which the current site can operate. Denoted by a comma separated string 
(example: 'example.com,foo.com'). Default: 'localhost,0.0.0.0,127.0.0.1'.
- SECRET_KEY - [see the documentation.][9] 
- DEBUG - [see the documentation.][10] Default: **False**.  
- REDIS_CACHE_BASE - Redis database number for the cache. Default: 0. 
- REDIS_CELERY_BASE - Redis database number for Celery. Default: 1.
- REDIS_HOST - Redis host. Default: 'redis'. 
- REDIS_PORT - Redis port. Default: 6379.
- BROKER_URL - connection string to the Redis base for Celery (message broker).
- CELERY_RESULT_BACKEND - connection string to the Redis base for Celery (task results). 
- CACHE_LOCATION - Redis connection string for caching
- USE_CACHE - use cache or not. Default: **True**.
- LOG_LEVEL - logging level. Default: **INFO**.
- LOG_FILE_NAME - log file name. Default: 'shortener.log'.
- PAGINATION_PAGE_SIZE - the number of objects returned through the REST API at one time. Default: 20.  
- BASE_ENCODING - the string that encodes the original link. Default: Base56.
- SUBPART_HASH_LEN - the length of the hash used to encode the section. The higher the number, the longer the resulting link. Default: 11.
- SESSION_COOKIE_AGE - lifetime of session cookies in seconds. Default: 1209600 (two weeks in seconds).
- DIRECTION_LIFETIME_SEC - alias lifetime in seconds. By default is equal to SESSION_COOKIE_AGE.
- CACHE_ON_CREATE - save alias in cache when creating. Default: **True**.
- SCHEDULE_CLEAR_DATA_MINUTES - the period of the task to remove obsolete aliases in minutes. Default: 60. 
- LINES_ON_PAGE - the number of lines of aliases created by the user. Default: 10.
- LAST_TRY_NUM - the number of attempts to create a random alias in the case that the alias by hash coincides with the existing one. Default: 10.

The rest of the settings are standard for Django and you can [set it][7] how you want in **settings.py** file.

## REST API

### End points

**/api/directions/** - short aliases for links. 

##### Available methods

GET, POST, HEAD, OPTIONS

**/api/userdirections/** - short links, associated with users.

##### Available methods

GET, POST, HEAD, OPTIONS

More details can be found by logging in through the browser to **<you_shortener_host>/api/**.

 [1]: https://www.djangoproject.com/
 [2]: https://www.django-rest-framework.org/
 [3]: https://redis.io/
 [4]: http://www.celeryproject.org/
 [5]: https://docs.docker.com/compose/
 [6]: https://bitly.com/
 [7]: https://docs.djangoproject.com/en/2.2/topics/settings/
 [8]: https://tinyurl.com/
 [9]: https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-SECRET_KEY
 [10]: https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-DEBUG
