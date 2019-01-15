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
from custom_admin.views import ( 
                    Patients, addPatient, editPatient,
                    invoice, newInvoice, generateInvoice,
                    invoiceHistory, invoiceHistorySearch,
)
from mainapp.views import changePassword

from django.contrib import admin

urlpatterns = [
    url(r'^patients/$', Patients, name="patients"),
    url(r'^add-patient/$', addPatient, name="add-patient"),
    url(r'^edit-patient/(?P<patient_id>[A-Z0-9]*)/$', editPatient, name="edit-patient"),
    url(r'^invoice/$', invoice, name="invoice"),
    url(r'^new-invoice/(?P<patient_id>[A-Z0-9]*)/$', newInvoice, name="new-invoice"),
    url(r'^search-invoice-history/$', invoiceHistorySearch, name="search-invoice-history"),
    url(r'^generate-invoice/(?P<patient_id>[A-Z0-9]*)/$', generateInvoice, name="generate-invoice"),
    url(r'^invoice-history/(?P<transaction_id>[0-9]*)/$', invoiceHistory, name="invoice-history"),
    url(r'^change-password/$', changePassword, name="change-password"),
]