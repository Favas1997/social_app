# Django Social App

## Overview

This project is a social networking application built with Django. It allows users to create profiles, connect with friends, The app leverages a PostgreSQL database and includes user authentication and an intuitive interface.

## Features

- User registration and authentication (sign up, login, logout)
- User profiles with customizable information
- Friend requests and user connections
- RESTful API for data access and manipulation
- Admin interface for managing users and content

## Prerequisites

- [Python](https://www.python.org/) (3.8 or higher)
- [Django](https://www.djangoproject.com/) (4.x)
- [PostgreSQL](https://www.postgresql.org/) (or another supported database)
- [Docker](https://www.docker.com/) (optional, for containerization)
- [Docker Compose](https://docs.docker.com/compose/) (optional, for container orchestration)

## Getting Started

### Clone the Repository

To get a copy of the project up and running on your local machine, follow these steps:

```bash
git clone 
cd social-app
```


### Docker Setup

To build and start the containers:

```bash
docker-compose up --build
```

To run migrations in Docker:

```bash
docker-compose run web python manage.py migrate
```

To create a superuser in Docker:

```bash
docker-compose run web python manage.py createsuperuser
```

To stop the Docker containers:
```bash
docker-compose down
```

### Accessing the application

- [Base url](http://localhost:8000/)
- [Admin](http://localhost:8000/admin/)
- [swagger](http://localhost:8000/swagger/)
- [doc](http://localhost:8000/redoc/)

