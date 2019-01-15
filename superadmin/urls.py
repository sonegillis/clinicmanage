"""clinicmanage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from .views import (
                    homePage, Clients, addClient, editClient, deleteClient, 
                    Administrators, addAdmin, editAdmin, deleteAdmin, Patients,
                    editInformation,
)
from mainapp.views import changePassword
from django.contrib import admin

urlpatterns = [
    url(r'^$', homePage, name="home"),
    url(r'^clients/$', Clients, name="clients"),
    url(r'^add-client/$', addClient, name="add-client"),
    url(r'^edit-client/(?P<client_id>\d+)/$', editClient, name="edit-client"),
    url(r'^delete-client/$', deleteClient, name="delete-client"),
    url(r'^admins/$', Administrators, name="admins"),
    url(r'^add-admin/$', addAdmin, name="add-admin"),
    url(r'^edit-admin/(?P<admin_id>\d+)/$', editAdmin, name="edit-admin"),
    url(r'^delete-admin/$', deleteAdmin, name="delete-admin"),
    url(r'^patients/$', Patients, name="patients"),
    url(r'^change-password/$', changePassword, name="change-password"),
    url(r'^edit-information/$', editInformation, name="edit-information"),
]
