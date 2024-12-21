# drf-library-practice

## Project Overview

An API for managing library operations written on DRF

## Installing using GitHub
Create Telegram Bot and Group.
Use Telegram API for telegram_bot_token, telegram_chat_id

```shell
git clone https://github.com/Morphin20th/drf-library-practice
cd drf-library-practice
python3 -m venv venv
```

Linux/Mac:

```shell
source venv/bin/activate
pip install -r requirements.txt
```

Windows:

```shell
venv\Scripts\activate
pip install -r requirements.txt
```

.env:

```shell
set SECURITY_KEY=<key>
set TELEGRAM_TOKEN=<telegram_bot_token>
set TELEGRAM_CHAT_ID=<telegram_chat_id> 
python ./manage.py migrate
python ./manage.py runserver
```


## Getting access
- create user via /api/users/
- get access token via /api/users/token/


## Features

- **JWT authentication**
- **Documentation**: Swagger: /api/doc/swagger/
- **Admin panel**: /admin/
- **CRUD for Book Service**
- **CRUD for User Service**
- **Borrowing Service create, retrieve, return endpoints**
- **Filter borrowings by user ids, is_active states**
- **Sending notifications to Telegram Chat after creating borrowing**