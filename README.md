# banking-api

Basic Banking API with features like.

* Create a new customer account with a name and an initial balance.
* Deposit funds into an account.
* Withdraw funds from an account.
* Transfer funds between two accounts.
* View the account balance and transaction history.

## Requirements
* Python-3.10
* PostgresSQL 16

## Getting Started
* git clone the repository ```git clone https://github.com/Roboid537/banking-api.git```
* Move to project directory ```cd banking-api```
* Create virtual environment and activate it (Mac/Linux).
    * ```python3 -m venv venv```
    * ```source venv/bin/activate```
* Create virtual environment and activate it (Windows).
    * ```python -m venv venv```
    * ```venv\Scripts\activate```
* Create database in postgres db and note credentials to update in .env.
* Copy `example.env` to `.env`:  ```cp example.env .env```
* Edit `.env` and add your variables.

* Install requirements ```pip install -r requirements.txt```

## Running Project
 * Create migrations ```python manage.py makemigrations```
 * Migrate ```python manage.py migrate```
 * Create superuser ```python manage.py createsuperuser``` fill the asked details
 * Run project ```python manage.py runserver```
 * Run tests ```python manage.py test```

## Test API's
* Run server and open url ```http://localhost:8000/swagger/```. All the apis are listed here for test.
* Create token
    * Open endpoint ```/token/``` enter credential used to create superuser and hit api. In response you will get access token.
    * Copy access token, on top of tha page there is a ```Authorize``` button click that and enter token in form   ```Bearer <token>```
    * You are all set to test the apis.
