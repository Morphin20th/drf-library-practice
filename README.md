# drf-library-practice

## Project Overview

An API for managing library operations written on DRF

## Installing using GitHub

```shell
git clone https://github.com/Morphin20th/drf-library-practice
cd drf-library-practice
python3 -m venv venv
```

Linux/Mac:

```shell
source venv/bin/activate
```

Windows:

```shell
venv\Scripts\activate
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