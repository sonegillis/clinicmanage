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
2. Go to your web browser and type the url _localhost:8080_. You should see ![Dimebook homepage](https://raw.githubusercontent.com/sonegillis/clinicmanage/develop/assets/description-images/dimebook-home.png "Homepage")
   **NB**: Some of the information you see on the homepage like the images, email and phone number won't be there by default. They'll be visible when you sign in as a superuser and under the **_Home_** section, **_Edit Information_** subsection, you upload the images and input the email, phone number

3. Login with the superuser account you created
   - Do homepage configurations on the **_Home_** section, **_Edit Information_** subsection
   - Create clients (clinics) on the **_Clients_** section, **_Add Clients_** subsection
   - Create Administrators for the clients you created on the **_Administrators_** section, **_Add Administrators_** subsection
   - Logout

4. Login with admin account you created


## Contributors
   1. Mekolle Sone Gillis ( [LinkedIn](www.linkedin.com/in/mekolle-sone-gillis-ekeh-junior-7180bb162), [github](https://github.com/sonegillis/) )
