from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
import os

# Create your models here.

designation = (
    ("admin", "admin"),
    ("doctor", "doctor"),
    ("nurse", "nurse"),
    ("labtech", "labtech"),
    ("pharmacist", "pharmacist"),
    ("cashier", "cashier")
)

gender = (
    ("f", "female"),
    ("m", "male"),
)

bloodgroup = (
    ("O-", "O-"),
    ("O+", "O+"),
    ("A-", "A-"),
    ("A+", "A+"),
    ("B-", "B-"),
    ("B-", "B-"),
    ("AB-", "AB-"),
    ("AB+", "AB+"),
)

class Client(models.Model):
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=30)
    tel = models.CharField(max_length=30)
    logo = models.ImageField(upload_to="clinic-logo/", null=True)
    email = models.EmailField()

    def __str__(self):
        return self.name

"""
    The designations include admin, doctor, nurse, labtech, pharmacist
"""

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    designation = models.CharField(max_length=30, choices=designation)
    tel = models.CharField(max_length=30)
    profile_pic = models.ImageField(upload_to="profile-pics/", null=True)

class Patient(models.Model):
    patient_id = models.CharField(max_length=7, primary_key=True, unique=True)
    cni = models.CharField(max_length=20, null=True)
    client = models.ForeignKey(Client, null=True)
    name = models.CharField(max_length=150)
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=gender)
    tel = models.CharField(max_length=15)
    address = models.CharField(max_length=50)
    email = models.EmailField(null=True)
    bloodgroup = models.CharField(max_length=5, choices=bloodgroup)
    diabetes = models.CharField(max_length=100, null=True)
    immuno_depressants = models.CharField(max_length=100, null=True)
    special_cases = models.CharField(max_length=100, null=True)
    notes = models.CharField(max_length=150, null=True)
    registered_by = models.ForeignKey(User, null=True)
    guardian_name = models.CharField(max_length=150, null=True)
    guardian_tel = models.CharField(max_length=25, null=True)
    registered_date = models.DateTimeField(auto_now_add=True, null=True)

class Examination(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    examination_date = models.DateTimeField(auto_now_add=True)
    examined_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    weight = models.IntegerField(null=True)
    temperature = models.FloatField(null=True)
    blood_pressure = models.CharField(max_length=20, null=True)
    symptoms = models.TextField(max_length=300, null=True)
    vaccines = models.TextField(max_length=300, null=True)
    allergies = models.TextField(max_length=300, null=True)
    diagnoses = models.TextField(max_length=300, null=True)
    notes = models.TextField(max_length=300, null=True)

class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    prescription_date = models.DateTimeField(auto_now_add=True)
    prescribed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    has_paid = models.BooleanField(default=False)


class PrescriptionDetail(models.Model):
    prescription = models.ForeignKey(Prescription)
    drug = models.CharField(max_length=300)
    dose = models.CharField(max_length=300)
    drug_alternative = models.CharField(max_length=300, null=True)
    dose_alternative = models.CharField(max_length=300, null=True)
    sold_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
class LabTest(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    labtest_date = models.DateTimeField(auto_now_add=True)
    done_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    has_paid = models.BooleanField(default=False)

class LabTestDetail(models.Model):
    labtest = models.ForeignKey(LabTest)
    labtest_name = models.CharField(max_length=50)
    labtest_price = models.CharField(max_length=50, null=True)
    labtest_result = models.CharField(max_length=50)

class SuperAdministratorInformation(models.Model):
    email = models.EmailField(null=True)
    tel = models.CharField(max_length=25)
    image1 = models.ImageField(upload_to="homepage-pics/", null=True)
    image2 = models.ImageField(upload_to="homepage-pics/", null=True)
    image3 = models.ImageField(upload_to="homepage-pics/", null=True)
    image4 = models.ImageField(upload_to="homepage-pics/", null=True)
    image5 = models.ImageField(upload_to="homepage-pics/", null=True)
    image6 = models.ImageField(upload_to="homepage-pics/", null=True)

class HospitalisationPayment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    hosp_days = models.CharField(max_length=50)
    unit_price = models.CharField(max_length=50)
    total = models.CharField(max_length=50)

class InvoiceStatistics(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, null=True)
    prescription = models.ForeignKey(Prescription, null=True)
    labtest = models.ForeignKey(LabTest, null=True)
    hospitalisation = models.ForeignKey(HospitalisationPayment)
    total = models.CharField(max_length=50)
    final_amount = models.CharField(max_length=50)
    given_amount = models.CharField(max_length=50)
    discount = models.CharField(max_length=50)
    balance = models.CharField(max_length=50)

    
    