from django.contrib import admin
from .models import UserProfile, Client, Patient, Examination, Prescription, PrescriptionDetail
# Register your models here.

admin.site.register(UserProfile)

admin.site.register(Client)

admin.site.register(Patient)

admin.site.register(Examination)

admin.site.register(Prescription)

admin.site.register(PrescriptionDetail)
