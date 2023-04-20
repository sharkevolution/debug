# Django Simple Chat Application

Простой чат, создан с использованием: 

1. Django 4.0
2. Django REST Framework 3.13.1
3. Simple JWT 5.2.2
4. Channel Layers 3.0.4
5. База sqlite3

![изображение](https://user-images.githubusercontent.com/24756805/233348320-b7b60702-4c23-44a2-aed0-137c2822073f.png)
------

Пользователь может создавать комнаты и добавлять участников, а также общаться один на один или со своими друзьями.

## Installing and Running Python 3.10
	
Вы можете скачать установщик *[Python][1]* со страницы *[Download Python][2]* официального сайта. Я буду использовать версию 3.10.

[1]:https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
[2]:https://www.python.org/downloads/release/python-31011/

После этого откройте PowerShell или CMD и перейдите в локальный каталог, в который вы хотите клонировать репозиторий

#### Клонируйте через HTTPS

    $ git clone https://github.com/sharkevolution/debug.git

#### Перейдите в каталог `debug`, обновите `pip` менеджер пакетов

    $ python -m pip install --upgrade pip

#### Cоздайте виртуальное окружение

    $ %LocalAppData%\Programs\Python\Python310\python.exe -m venv %cd%\venv
  
#### Структура после создания

    debug
    	projects
	venv
	.gitignore
	README.md
	requirements.txt
	
#### Установите пакеты и зависимости

    $ pip install -r requirements.txt

#### Выполните следующие команды, чтобы создать нужные таблицы в базе данных `sqlite3`

    $ python manage.py makemigrations
    $ python manage.py migrate

#### Создание суперпользователя

Для создания суперпользователя вызовите следующую команду из той же папки, где расположен `manage.py`. Вас попросят ввести имя пользователя, адрес электронной почты и надёжный пароль.

    $ python3 manage.py createsuperuser
    
После выполнения этой команды новый суперпользователь будет добавлен в базу данных. Теперь перезапустите сервер, чтобы можно было протестировать вход на сайт:

#### Запуск отладочного сервера

     $ python manage.py runserver
     
Команда запустит приложение будет доступно на вашем локальном хосте http://127.0.0.1:8000/

#### Войдите в чат используя логин и пароль администратора или пройдите регистрацию для обычного пользователя

![изображение](https://user-images.githubusercontent.com/24756805/233366602-5d6427a2-0550-420a-8166-e7526bb2e9bf.png)

#### Страница создания комнат 

![изображение](https://user-images.githubusercontent.com/24756805/233367632-2165d5e9-15d7-47b7-a7d5-d0d8763479e7.png)
------

Для тестирования откройте два разных браузера, залогинтесь под разными пользователями. 
Введите новое название комнаты для создания или войдите в одну из существующих для переписки.

![изображение](https://user-images.githubusercontent.com/24756805/233374563-e2a55a36-2fc0-44fb-9a9c-5ef265c23d00.png)
------

#### Реализованные функции:

1. Частная переписка между 2 участниками, если в комнате только два участника все сообщения будут частными. Если в комнате 1 или более 2 участников все сообщения становяться общими и доставлены всем для прочтения. при необходимсти отправки частного сообщения, нажмите на имя пользователя в разделе "участники группы" сообщение с приставкой `/pm ` будет доставлено только указанному пользователю. 


3. Новые и непрочитанные сообщения
4. Уведомление о прочтении сообщения
5. Отображение текущего статуса пользователя (активен/неактивен)
6. Добавление и исключение пользователей из комнаты

#### Реализованный API:

|Метод	|URL-адрес                                    |
|-------|---------------------------------------------|
|POST	|http://127.0.0.1:8000/api/v1/token/          |
|POST	|http://127.0.0.1:8000/api/v1/users/create/   |
|GET	|http://127.0.0.1:8000/api/v1/rooms/          |
|GET	|http://127.0.0.1:8000/api/v1/rooms/2/        |
|GET	|http://127.0.0.1:8000/api/v1/roomcontent/2/  |
|GET	|http://127.0.0.1:8000/api/v1/users/          |
|GET	|http://127.0.0.1:8000/api/v1/users/1         |
|GET	|http://127.0.0.1:8000/api/v1/users/unread/3/ |
|POST	|http://localhost:8000/api/v1/usersend/       |
|POST	|http://127.0.0.1:8000/api/v1/roomcreate/     |




