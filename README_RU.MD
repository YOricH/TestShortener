# Test Shortener
[Русский](./README_RU.MD)|[English](./README.MD)

Пример сервиса - сокращателя ссылок (как [bitly.com][6] или [tinyurl.com][8]). 
Пользователи определяются по сессии.
В качестве базы используется PostgreSQL, но можно легко настроить приложение под использование 
любой другой СУБД, доступной Django.
## Возможности
- Указание своего сокращения
- Список созданных текущим пользователем сокращений с пагинацией
- Кэширование сокращений в Redis
- Автоматическое удаление старых сокращений
- REST API
- Простая сборка при помощи Docker compose или Kubernetes
## Используемые технологии
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
## Системные требования
*Желательно использовать Unix-like систему. Работа приложения проверена на Manjaro и Ubuntu.*
### Для запуска без контейнеризации
- Python >= 3.11
- pipenv >= 2022.10
- PostgreSQL >= 14
- Redis >= 7
### Для запуска через Docker Compose
- GNU Make >= 4
- Docker >= 20
- Docker Compose >= 2
### Для запуска через Kubernetes
*Сборка проверена и настроена для Minikube* 
- GNU Make >= 4
- Minikube >= 1.27
## Установка
Загружаем из исходников (требуется [GIT](https://git-scm.com/)):
```sh
$ git clone https://github.com/yorich/TestShortener.git
$ cd TestShortener
```
### Без контейнеризации
1. Устанавливаем зависимости:
```sh
$ pipenv shell
$ pipenv install --ignore-pipfile
```
2. [Создаем пустую базу данных PostgreSQL.](https://postgrespro.ru/docs/postgresql/15/manage-ag-createdb)
3. При необходимости настраиваем переменные окружения. Либо в корне проекта создаем файл .env, где их указываем. 
Как пример можно использовать файл .env.dist.
4. Создаем таблицы в указанной БД:
```sh
$ python manage.py migrate
```
5. Если все успешно, запускаем тестовый сервер на локальной машине:
```sh
$ python manage.py runserver 8000
```
### Docker Compose
1. При необходимости настраиваем переменные окружения в файле .env.compose.
2. Запускаем через утилиту Make:
```sh
$ make compose.run
```
3. Для остановки используем команду
```sh
$ make compose.stop
```
4. Для удаления контейнеров, связанных сетей и volumes:
```sh
$ make compose.clear
```
*Скачанные при установке образы не удаляются.*
### Minikube
1. При необходимости настраиваем переменные окружения в файле .env.compose.
2. Запускаем через утилиту Make:
```sh
$ make kube.run
```
3. Останавливаем и удаляем все созданные объекты:
```sh
$ make kube.clear
```
## Настройка
*Все настройки производятся через переменные окружения, либо через файл .env (или .env.compose для контейнеров).*
- DATABASE_URI - строка подключения к базе данных. Обязательная настройка.
- ALLOWED_HOSTS - список хостов/доменов, для которых может работать текущий сайт. Указываются строкой 
через запятую (например 'example.com,foo.com'). По умолчанию **'localhost,0.0.0.0,127.0.0.1'**.
- SECRET_KEY - [смотри документацию.][9] 
- DEBUG - [смотри документацию.][10] По умолчанию **False**.  
- CACHE_URL - строка подключения к базе Redis для кэша. Обязательная настройка.
- BROKER_URL - строка подключения к базе Redis для Celery (брокер сообщений). Обязательная настройка.
- RESULT_BACKEND - строка подключения к базе Redis для Celery (результаты выполнения задач). Обязательная настройка.
- USE_CACHE - использовать кэш или нет. По умолчанию **True**.
- LOG_LEVEL - уровень логирования. По умолчанию **INFO**.
- USE_LOG_FILE - использовать логирование в файл или нет. По умолчанию **False**.
- LOG_FILE_NAME - имя файла логов. По умолчанию **'shortener.log'**.
- PAGINATION_PAGE_SIZE - количество возвращаемых через REST API объектов за один раз. По умолчанию **20**.  
- BASE_ENCODING - строка, которой кодируется исходная ссылка. По умолчанию **Base56**.
- SUBPART_HASH_LEN - длина используемого для кодирования участка хэша. Чем больше число, тем длиннее получившаяся ссылка. По умолчанию **11**.
- SESSION_COOKIE_AGE - время жизни cookies сессии в секундах. По умолчанию **1209600** (две недели в секундах).
- DIRECTION_LIFETIME_SEC - время жизни сокращения в секундах. По умолчанию равно **SESSION_COOKIE_AGE**.
- CACHE_ON_CREATE - сохранять сокращение в кэше при создании. По умолчанию **True**.
- SCHEDULE_CLEAR_DATA_MINUTES - период запуска задания по удалению устаревших сокращений в минутах. По умолчанию **60**. 
- LINES_ON_PAGE - количество строк пользовательских сокращений на одной странице при работе через браузер. По умолчанию равно **PAGINATION_PAGE_SIZE**.
- LAST_TRY_NUM - количество попыток создания случайного сокращения в случае, если сокращение по хэшу совпадает с уже существующим. По умолчанию **10**.

Остальные настройки являются стандартными для Django. Вы можете [настроить][7] их под себя в файле **settings.py**.

## REST API
### Конечные точки
**/api/directions/** - сокращения ссылок. 
##### Доступные методы
GET, POST, HEAD, OPTIONS

**/api/userdirections/** - сокращения ссылок, привязанные к пользователям. 
Можно работать только с объектами, принадлежащими текущему пользователю (определяется через сессию).
##### Доступные методы
GET, POST, HEAD, OPTIONS

Подробнее об API можно узнать, зайдя через браузер на **<you_shortener_host>/api/**.

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