# airport-api

Django project for managing airport written on DRF


## Installation 

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

A step by step series of examples that tell you how to get a development env running

### Installing using GitHub
Ensure Python 3.7+ is installed. Follow these steps:

```shell
git clone https://github.com/katryana/airport-api
cd airport_service
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt
```
You should:
* Create a .env file in the project root, similar to .env.sample, and fill in your data.
* Initialize and run migrations:

```shell
python manage.py makemigrations
python manage.py migrate
```
* Run server:

```shell
python manage.py runserver
```
### Installing using Docker
Ensure Docker is installed. Follow these steps:

```shell
docker-compose build
docker-compose up
```

## Filling out the data

Use ``` python manage.py loaddata airport_db_data.json``` to add data

To test admin features use these credentials:

username: ``` staff@airport.com ``` 
password: ```n5d5ved7```
public
You can sign up to the site to see the difference between staff and ordinary users

## Running the tests

To run tests use this command ```python manage.py test ```

## Features

* JWT authenticated
* Admin panel /admin/
* Documentation is located at /api/doc/swagger/
* Managing orders and tickets

Unauthenticated User can:
* register account
* see flights

Authenticated User can:
* manage accounts
* see airplanes, airplane types, airports, routes, order history
* create orders with tickets

Admin User can:
* create airplanes, airplane types, flights, routes
* update airplanes, flights

## Demo

Here you can find images of list of some endpoints

![airport_endpoint_1.png](..%2F..%2FPictures%2FScreenshots%2Fairport_endpoint_1.png)
![airport_endpoint_2.png](..%2F..%2FPictures%2FScreenshots%2Fairport_endpoint_2.png)
![airport_endpoint_3.png](..%2F..%2FPictures%2FScreenshots%2Fairport_endpoint_3.png)
