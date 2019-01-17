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
                    homePage, Workers, addWorker, editWorker, deleteWorker, 
                    Patients, addPatient, editPatient, medicalHistory,
                    newExamination, oldExamination, examination,
                    newPrescription, oldPrescription, prescription,
                    newLabTest, oldLabTest, labTest, changeWorkerPassword,
                    giveDrugSearch, giveDrug, editInformation,
                    invoice, newInvoice, generateInvoice,
                    invoiceHistory, invoiceHistorySearch,
)
from mainapp.views import changePassword

from django.contrib import admin

urlpatterns = [
    url(r'^$', homePage, name="home"),
    url(r'^worker-change-password/(?P<worker_id>\d+)/$', changeWorkerPassword, name="worker-change-password"),
    url(r'^workers/$', Workers, name="workers"),
    url(r'^add-worker/$', addWorker, name="add-worker"),
    url(r'^edit-worker/(?P<worker_id>\d+)/$', editWorker, name="edit-worker"),
    url(r'^delete-worker/$', deleteWorker, name="delete-worker"),
    url(r'^patients/$', Patients, name="patients"),
    url(r'^add-patient/$', addPatient, name="add-patient"),
    url(r'^edit-patient/(?P<patient_id>[A-Z0-9]*)/$', editPatient, name="edit-patient"),
    url(r'^examination/(?P<examination>.*)/$', examination, name="examination"),
    url(r'^new-examination/(?P<patient_id>[A-Z0-9]*)/$', newExamination, name="new-examination"),
    url(r'^old-examination/(?P<patient_id>[A-Z0-9]*)/$', oldExamination, name="old-examination"),
    url(r'^prescription/(?P<prescription>.*)/$', prescription, name="prescription"),
    url(r'^new-prescription/(?P<patient_id>[A-Z0-9]*)/$', newPrescription, name="new-prescription"),
    url(r'^old-prescription/(?P<patient_id>[A-Z0-9]*)/$', oldPrescription, name="old-prescription"),
    url(r'^lab-test/(?P<labtest>.*)/$', labTest, name="lab-test"),
    url(r'^new-lab-test/(?P<patient_id>[A-Z0-9]*)/$', newLabTest, name="new-lab-test"),
    url(r'^old-lab-test/(?P<patient_id>[A-Z0-9]*)/$', oldLabTest, name="old-lab-test"),
    url(r'^medical-history/(?P<patient_id>[A-Z0-9]*)/$', medicalHistory, name="medical-history"),
    url(r'^invoice/$', invoice, name="invoice"),
    url(r'^new-invoice/(?P<patient_id>[A-Z0-9]*)/$', newInvoice, name="new-invoice"),
    url(r'^search-invoice-history/$', invoiceHistorySearch, name="search-invoice-history"),
    url(r'^generate-invoice/(?P<patient_id>[A-Z0-9]*)/$', generateInvoice, name="generate-invoice"),
    url(r'^invoice-history/(?P<patient_id>[A-Z0-9]*)/$', invoiceHistory, name="invoice-history"),
    url(r'^give-drug-search/$', giveDrugSearch, name="give-drug-search"),
    url(r'^give-drug/(?P<patient_id>[A-Z0-9]*)/$', giveDrug, name="give-drug"),
    url(r'^edit-information/$', editInformation, name="edit-information"),
    url(r'^change-password/$', changePassword, name="change-password"),
]