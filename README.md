# DIMEBOOK
A web application called **Dimebook** that manages the medical and financial activites in clinics and smaller hospitals. It is hosted on [www.dimebook.net](https://www.dimebook.net)

## Preliquites
* git and github
* Python3
* Django 1.11.2
* Web Browser
* HTML5
* CSS3
* JavaScript
* virtualenv

## Getting started
1. Open the terminal
   - Create a virtual environment for the project inside any directory of your choice by running
      ```bash
        $ virtualenv -p python3 clinicmanage_env
        $ cd clinicmanage_env
        $ source bin/activate
   - Navigate to any directory where you want to keep the project and Run
      ```bash
        $ git clone https://github.com/sonegillis/clinicmanage.git
      ```
   - Navigate to the project folder and install requirements with pip
      ```bash
        $ cd clinicmanage
        $ pip install -r requirements.txt
      ```
   - Make migrations and apply them
      ```bash
        $ python3 manage.py makemigrations
        $ python3 manage.py migrate
      ```
   - Create a superuser and start the django production server on desired port
      ```bash
        $ python3 manage.py createsuperuser
        $ python3 manage.py runserver 0.0.0.0:8080
      ```
2. Go to your web browser and type the url _localhost:8080_
