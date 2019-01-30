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
                    Patients, addPatient, editPatient, medicalHistory,
                    newExamination, oldExamination, examination,
                    newPrescription, oldPrescription, prescription,
                    clinicStatistics
)
from mainapp.views import changePassword

from django.contrib import admin

urlpatterns = [
    url(r'^patients/$', Patients, name="patients"),
    url(r'^add-patient/$', addPatient, name="add-patient"),
    url(r'^edit-patient/(?P<patient_id>[A-Z0-9]*)/$', editPatient, name="edit-patient"),
    url(r'^examination/(?P<examination>.*)/$', examination, name="examination"),
    url(r'^new-examination/(?P<patient_id>[A-Z0-9]*)/$', newExamination, name="new-examination"),
    url(r'^old-examination/(?P<patient_id>[A-Z0-9]*)/$', oldExamination, name="old-examination"),
    url(r'^prescription/(?P<prescription>.*)/$', prescription, name="prescription"),
    url(r'^new-prescription/(?P<patient_id>[A-Z0-9]*)/$', newPrescription, name="new-prescription"),
    url(r'^old-prescription/(?P<patient_id>[A-Z0-9]*)/$', oldPrescription, name="old-prescription"),
    url(r'^medical-history/(?P<patient_id>[A-Z0-9]*)/$', medicalHistory, name="medical-history"),
    url(r'^clinic-statistics/$', clinicStatistics, name="clinic-statistics"),
    url(r'^change-password/$', changePassword, name="change-password"),
]