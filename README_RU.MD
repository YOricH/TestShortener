# Test Shortener
[Русский](./README_RU.MD)|[English](./README.MD)

Пример сервиса - сокращателя ссылок (как [bitly.com][6] или [tinyurl.com][8]). 
Пользователи определяются по сессии.
В качестве базы используется MySQL, но можно легко настроить использование 
любой другой СУБД, доступной Django. 

## Возможности
- Указание своего сокращения
- Список созданных текущим пользователем сокращений с пагинацией
- Кэширование сокращений в Redis
- Автоматическое удаление старых сокращений
- REST API
- Простая сборка при помощи Docker compose

## Используемые технологии
- [Django][1]
- [Django Rest Framework][2]
- [Redis][3]
- [Celery][4]
- [Docker compose][5]

## Системные требования
- Docker
- Docker Compose
- MySQL или другая СУБД, поддерживаемая Django 

## Установка

1). Загружаем из исходников (требуется GIT)
```sh
$ git clone https://github.com/yorich/TestShortener.git
$ cd TestShortener/project
```

2). При необходимости настраиваем переменные окружения и файл docker-compose.yml (см. раздел **Настройка**).

3). Запускаем через Docker compose:
```sh
$ docker-compose up
```
## Настройка
*Все настройки производятся через переменные окружения, либо через файл docker-compose.yml.*
- DATABASE_URL - строка подключения к базе данных. Обязательная настройка. Если планируется использовать НЕ MySQL, 
необходимо внесни соответсвующие изменения в файлы requirements.txt и Dockerfile.
- ALLOWED_HOSTS - список хостов/доменов, для которых может работать текущий сайт. Указываются строкой 
через запятую (например 'example.com,foo.com'). По умолчанию 'localhost,0.0.0.0,127.0.0.1'.
- SECRET_KEY - [смотри документацию.][9] 
- DEBUG - [смотри документацию.][10] По умолчанию **False**.  
- REDIS_CACHE_BASE - номер базы данных Redis для кэша. По умолчанию 0. 
- REDIS_CELERY_BASE - номер базы данных Redis для Celery. По умолчанию 1.
- REDIS_HOST - хост Redis. По умолчанию 'redis'. 
- REDIS_PORT - Порт Redis. По умолчанию 6379.
- BROKER_URL - строка подключения к базе Redis для Celery (брокер сообщений).
- CELERY_RESULT_BACKEND - строка подключения к базе Redis для Celery (результаты выполнения задач). 
- CACHE_LOCATION - строка подключения к базе Redis для кэширования.
- USE_CACHE - использовать кэш или нет. По умолчанию **True**.
- LOG_LEVEL - уровень логирования. По умолчанию **INFO**.
- LOG_FILE_NAME - имя файла логов. По умолчанию 'shortener.log'.
- PAGINATION_PAGE_SIZE - количество возвращаемых через REST API объектов за один раз. По умолчанию 20.  
- BASE_ENCODING - строка, которой кодируется исходная ссылка. По умолчанию Base56.
- SUBPART_HASH_LEN - длина используемого для кодирования участка хэша. Чем больше число, тем длиннее получившаяся ссылка. По умолчанию 11.
- SESSION_COOKIE_AGE - время жизни cookies сессии в секундах. По умолчанию 1209600 (две недели в секундах).
- DIRECTION_LIFETIME_SEC - время жизни сокращения в секундах. По умолчанию равно SESSION_COOKIE_AGE.
- CACHE_ON_CREATE - сохранять сокращение в кэше при создании. По умолчанию **True**.
- SCHEDULE_CLEAR_DATA_MINUTES - период запуска задания по удалению устаревших сокращений в минутах. По умолчанию 60. 
- LINES_ON_PAGE - количество строк сокращений, созданных пользователем. По умолчанию 10.
- LAST_TRY_NUM - количество попыток создания случайного сокращения в случае, если сокращение по хэшу совпадает с уже существующим. По умолчанию 10.

Остальные настройки являются стандартными для Django и вы можете [настроить][7] их под себя в файле **settings.py**.

## REST API
### Конечные точки

**/api/directions/** - сокращения ссылок. 

##### Доступные методы

GET, POST, HEAD, OPTIONS

**/api/userdirections/** - сокращения ссылок, привязанные к пользователям.

##### Доступные методы

GET, POST, HEAD, OPTIONS

Подробнее об API можно узнать, зайдя через браузер на **<you_shortener_host>/api/**.

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
