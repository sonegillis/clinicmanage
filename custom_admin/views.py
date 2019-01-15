from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.template.loader import render_to_string
from mainapp.models import UserProfile, Patient, Examination, Prescription, PrescriptionDetail, LabTest, LabTestDetail, Client, HospitalisationPayment, InvoiceStatistics
from mainapp.views import generateUniquePatientID, extractDrugAndDose, getClient
from django.core.files.storage import FileSystemStorage
import json
import re
from django.utils import timezone
import datetime
import glob, os
from django.conf import settings

# Create your views here.

def homePage(request):
    template_name = "admin-homepage.html"
    userprofile = UserProfile.objects.filter(user=request.user)[0]
    context = {
        "title" : "Admin | home",
        "active" : "home",
        "userprofile" : userprofile,
        "nav_icon" : "fas fa-hospital",
        "main_nav" : "Home",
        "sub_nav" : "Administrator Dashboard",
        "client" : getClient(request.user),
    }
    return render(request, template_name, context)

@login_required
def Workers(request):
    if getWorkerDesignation(request.user) != "admin":
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    template_name = "workers.html"
    client = getClientId(request.user)
    workers = UserProfile.objects.filter(client=client)
    userprofile = UserProfile.objects.filter(user=request.user)[0]
    context = {
        "title" : "Admin | workers",
        "active" : "workers",
        "workers" : workers,
        "userprofile" : userprofile,
        "nav_icon" : "fas fa-users",
        "main-nav" : "Workers",
        "main_nav" : "Workers",
        "sub_nav" : "All Workers",
        "client" : getClient(request.user),
    }
    return render(request, template_name, context)

@login_required
def addWorker(request):
    if getWorkerDesignation(request.user) != "admin":
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "add-worker.html"
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        context = {
                "title" : "Admin | add worker",
                "active" : "workers",
                "userprofile" : userprofile,
                "nav_icon" : "fas fa-users",
                "main_nav" : "Workers",
                "sub_nav" : "Add Worker",
                "client" : getClient(request.user),
        }
        return render(request, template_name, context)

    if request.method == "POST":
        user = User.objects.create_user(
            username = request.POST["username"],
            password = request.POST["password1"],
            first_name = request.POST["first_name"],
            last_name = request.POST["last_name"],
            email = request.POST["email"],
        )
        profile_pic = request.FILES.get('profile_pic', None)
        if profile_pic:
            fs = FileSystemStorage(location="media/profile-pics", base_url="profile-pics/")
            picname = fs.save(profile_pic.name, profile_pic)
            uploaded_pic_url = fs.url(picname)
        else:
            uploaded_pic_url = None
        client = getClientId(request.user)
        UserProfile(
            user = user,
            client_id = client,
            designation = request.POST["designation"],
            tel = request.POST["tel"],
            profile_pic = uploaded_pic_url,
        ).save()
        response = json.dumps(
            {
                "first_name" : request.POST["first_name"],
                "msg" : "added",
                "url" : "/custom-admin/workers/"
            }
        )
        return HttpResponse(response)

@login_required
def editWorker(request, worker_id):
    if getWorkerDesignation(request.user) != "admin":
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "edit-worker.html"
        user = User.objects.filter(id=worker_id)[0]
        worker = UserProfile.objects.filter(user=user)[0]
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        context = {
            "title" : "Admin | add client",
            "active" : "workers",
            "worker" : worker,
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-users",
            "main_nav" : "Workers",
            "sub_nav" : "Edit Worker",
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)

    if request.method == "POST":
        user = User.objects.filter(id=worker_id)
        user.update(
            first_name = request.POST["first_name"],
            last_name = request.POST["last_name"],
            email = request.POST["email"]
        )
        profile_pic = request.FILES.get('profile_pic', None)
        if profile_pic:
            fs = FileSystemStorage(location="media/profile-pics", base_url="profile-pics/")
            for filename in glob.glob(settings.MEDIA_ROOT+"/profile-pics/"+"user_"+str(user[0].id)+"_pic_*"):
                os.remove(filename)
            picname = fs.save("user_"+str(user[0].id)+"_pic_"+profile_pic.name, profile_pic)
            uploaded_pic_url = fs.url(picname)

        else:
            uploaded_pic_url = None
        client = getClientId(request.user)
        UserProfile.objects.filter(user=user).update(
            client_id = client,
            designation = request.POST["designation"],
            tel = request.POST["tel"],
            profile_pic = uploaded_pic_url,
        )
        response = json.dumps(
            {
                "first_name" : request.POST["first_name"],
                "msg" : "editted",
                "url" : "/custom-admin/workers/"
            }
        )
        return HttpResponse(response)

@login_required
def deleteWorker(request):
    if getWorkerDesignation(request.user) != "admin":
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    workers_to_delete = request.POST.getlist("workers_to_delete[]")
    for worker in workers_to_delete:
        User.objects.filter(id=int(worker)).delete()

    return HttpResponseRedirect(reverse("custom-admin:workers"))

@login_required
def Patients(request):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        title = "Admin | patients"
        edit_patient_url = "custom-admin:edit-patient"
    elif designation == "doctor":
        base_template = "doctor-base.html"
        title = "Doctor | patients"
        edit_patient_url = "doctor:edit-patient"
    elif designation == "nurse":
        base_template = "nurse-base.html"
        title = "Nurse | patients"
        edit_patient_url = "nurse:edit-patient"
    elif designation == "labtech":
        base_template = "labtech-base.html"
        title = "Labtech | patients"
        edit_patient_url = "labtech:edit-patient"
    elif designation == "pharmacist":
        base_template = "pharmacy-base.html"
        title = "Pharmacy | patients"
        edit_patient_url = "pharmacy:edit-patient"
    elif designation == "cashier":
        base_template = "cashier-base.html"
        title = "Cashier | patients"
        edit_patient_url = "cashier:edit-patient"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")
        
    if request.method == "GET":
        client = getClientId(request.user)
        template_name = "admin-patients.html"
        patients = Patient.objects.filter(client=client)
        userprofile = UserProfile.objects.filter(user=request.user)[0]

        context = {
            "title" : title,
            "active" : "patients",
            "patients" : patients,
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-bed",
            "main_nav" : "Patients",
            "sub_nav" : "All Patients",
            "edit_patient_url" : edit_patient_url,
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)

@login_required
def addPatient(request):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        title = "Admin | add patient"
        edit_patient_url = "custom-admin:edit-patient"
        response_url = "/custom-admin/add-patient/"
        response_url_w_add_visit = "/custom-admin/new-examination/"
    elif designation == "doctor":
        base_template = "doctor-base.html"
        title = "Doctor | add patient"
        edit_patient_url = "doctor:edit-patient"
        response_url = "/doctor/add-patient/"
        response_url_w_add_visit = "/doctor/new-examination/"
    elif designation == "nurse":
        base_template = "nurse-base.html"
        title = "Nurse | add patient"
        edit_patient_url = "nurse:edit-patient"
        response_url = "/nurse/add-patient/"
        response_url_w_add_visit = "/nurse/new-examination/"
    elif designation == "labtech":
        base_template = "labtech-base.html"
        title = "Labtech | add patient"
        edit_patient_url = "labtech:edit-patient"
        response_url = "/labtech/add-patient/"
        response_url_w_add_visit = "/labtech/new-lab-test/"
    elif designation == "pharmacist":
        base_template = "pharmacy-base.html"
        title = "Pharmacy | add patient"
        edit_patient_url = "pharmacy:edit-patient"
        response_url = "/pharmacy/add-patient/"
        response_url_w_add_visit ="/pharmacy/new-prescription/"
    elif designation == "cashier":
        base_template = "cashier-base.html"
        title = "Cashier | add patient"
        edit_patient_url = "cashier:add-patient"
        response_url = "/cashier/add-patient/"
        response_url_w_add_visit = None
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "admin-add-patient.html"
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        context = {
                "title" : title,
                "active" : "patients",
                "userprofile" : userprofile,
                "nav_icon" : "fas fa-bed",
                "main_nav" : "Patients",
                "sub_nav" : "Add Patient",
                "edit_patient_url" : edit_patient_url,
                "base_template" : base_template,
                "client" : getClient(request.user),
        }
        return render(request, template_name, context)

    if request.method == "POST":
        unique_id = generateUniquePatientID()
        client = getClientId(request.user)
        patient = Patient(
            client_id = client,
            patient_id = unique_id,
            cni = request.POST["cni"],
            name = request.POST["name"],
            birth_date = request.POST["birth_date"],
            gender = request.POST["gender"],
            tel = request.POST["tel"],
            address = request.POST["address"],
            email = request.POST.get("email", None),
            bloodgroup = request.POST.get("bloodgroup", None),
            diabetes = request.POST.get("diabetes", None),
            immuno_depressants = request.POST.get("immuno_depressants"),
            special_cases = request.POST.get("special_cases"),
            notes = request.POST.get("notes", None),
            registered_by = request.user,
            guardian_name = request.POST.get("guardian_name", None),
            guardian_tel = request.POST.get("guardian_tel", None)
        ).save()
        add_visit = request.POST.get("add_visit", None)
        response = json.dumps(
            {
                "patient_id" : unique_id,
                "response_url" : response_url_w_add_visit+unique_id+"/" if add_visit and response_url_w_add_visit else response_url
            }
        )
        return HttpResponse(response)

@login_required
def editPatient(request, patient_id):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        title = "Admin | edit patient"
        response_redirect_url = "/custom-admin/patients/"
        response_redirect_url_w_add_visit = "/custom-admin/new-examination/"+patient_id+"/"
    elif designation == "doctor":
        base_template = "doctor-base.html"
        title = "Doctor | edit patient"
        response_redirect_url = "/doctor/patients/"
        response_redirect_url_w_add_visit = "/doctor/new-examination/"+patient_id+"/"
    elif designation == "nurse":
        base_template = "nurse-base.html"
        title = "Nurse | edit patient"
        response_redirect_url = "/nurse/patients/"
        response_redirect_url_w_add_visit = "/nurse/new-examination/"+patient_id+"/"
    elif designation == "labtech":
        base_template = "labtech-base.html"
        title = "Labtech | edit patient"
        response_redirect_url = "/labtech/patients/"
        response_redirect_url_w_add_visit = "/labtech/new-lab-test/"+patient_id+"/"
    elif designation == "pharmacist":
        base_template = "pharmacy-base.html"
        title = "Pharmacy | edit patient"
        response_redirect_url = "/pharmacy/patients/"
        response_redirect_url_w_add_visit = "/pharmacy/new-prescription/"+patient_id+"/"
    elif designation == "cashier":
        base_template = "cashier-base.html"
        title = "Cashier | edit patient"
        response_redirect_url = "/cashier/patients/"
        response_redirect_url_w_add_visit = None
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "admin-edit-patient.html"
        patient = Patient.objects.filter(patient_id=patient_id)[0]
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        context = {
            "title" : title,
            "active" : "patients",
            "patient" : patient,
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-bed",
            "main_nav" : "Patients",
            "sub_nav" : "Edit Patients",
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)
    if request.method == "POST":
        Patient.objects.filter(patient_id=patient_id).update(
            name = request.POST["name"],
            birth_date = request.POST["birth_date"],
            cni = request.POST["cni"],
            gender = request.POST["gender"],
            tel = request.POST["tel"],
            address = request.POST["address"],
            email = request.POST.get("email", None),
            bloodgroup = request.POST.get("bloodgroup", None),
            notes = request.POST.get("notes", None),
            registered_by = request.user,
            guardian_name = request.POST.get("guardian_name", None),
            guardian_tel = request.POST.get("guardian_tel", None)
        )
        add_visit = request.POST.get("add_visit", None)
        return HttpResponse(response_redirect_url_w_add_visit) if add_visit and response_redirect_url_w_add_visit else HttpResponse(response_redirect_url)

# @param examination tells the type of examination the user wants to see
#   that is if its either the previous or the medical history
@login_required
def examination(request, examination):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        title = "Admin | examination"
        response_url = "custom-admin"
    elif designation == "doctor":
        base_template = "doctor-base.html"
        title = "Doctor | examination"
        response_url = "doctor"
    elif designation == "nurse":
        base_template = "nurse-base.html"
        title = "Nurse | examination"
        response_url = "nurse"
    elif designation == "labtech":
        if examination != "medical-history":
            return HttpResponse("You do not have permission to access this page!! This account will be reported")
        base_template = "labtech-base.html"
        title = "Labtech | examination"
        response_url = "labtech"
    elif designation == "pharmacist":
        if examination != "medical-history":
            return HttpResponse("You do not have permission to access this page!! This account will be reported")
        base_template = "pharmacy-base.html"
        title = "Pharmacy | examination"
        response_url = "pharmacy"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "examination.html"
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        context = {
            "title" : title,
            "active" : "examination",
            "userprofile" : userprofile,
            "nav_icon" : "far fa-file-alt",
            "main_nav" : "Examination",
            "sub_nav" : "Search Patient By Dimebook ID or CNI",
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)
    if request.method == "POST":
        patient = Patient.objects.filter(Q(patient_id=request.POST["patient_id"].upper()) | Q(cni=request.POST["patient_id"]))
        if patient.exists():
            response = json.dumps(
                            {
                                "patient_id" : patient[0].patient_id,
                                "examination" : examination,
                                "response_url" : response_url
                            }
                        )
            return HttpResponse(response)
        else:
            response = json.dumps(
                {
                    "patient_id" : request.POST["patient_id"].upper(),
                    "examination" : examination,
                    "response_url" : response_url
                }
            )
            return HttpResponse(response, status=404)

@login_required
def newExamination(request, patient_id):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        response_redirect_url = "custom-admin"
        title = "Admin | new examination"
    elif designation == "doctor":
        base_template = "doctor-base.html"
        response_redirect_url = "doctor"
        title = "Doctor | new examination"
    elif designation == "nurse":
        base_template = "nurse-base.html"
        response_redirect_url = "nurse"
        title = "Nurse | new examination"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    patient = Patient.objects.filter(Q(patient_id=patient_id) | Q(cni=patient_id))[0]
    if request.method == "GET":
        template_name = "new-examination.html"
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        context = {
            "title" : title,
            "active" : "examination",
            "patient" : patient,
            "userprofile" : userprofile,
            "nav_icon" : "far fa-file-alt",
            "main_nav" : "Examination",
            "sub_nav" : "New Examination",
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)
    if request.method == "POST":
        examination = Examination(
            patient = patient,
            examined_by = request.user,
            weight = request.POST["weight"],
            temperature = request.POST["temperature"],
            blood_pressure = request.POST["blood-pressure"],
            symptoms = request.POST['symptoms'],
            vaccines = request.POST["vaccines"],
            allergies = request.POST["allergies"],
            diagnoses = request.POST["diagnoses"],
            notes = request.POST["notes"]
        ).save()
        return HttpResponse(response_redirect_url)

@login_required
def oldExamination(request, patient_id):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        title = "Admin | old examination"
    elif designation == "doctor":
        base_template = "doctor-base.html"
        title = "Doctor | old examination"
    elif designation == "nurse":
        base_template = "nurse-base.html"
        title = "Nurse | old examination"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "old-examination.html"
        patient = Patient.objects.filter(Q(patient_id=patient_id) | Q(cni=patient_id))[0]
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        try:
            examination = Examination.objects.filter(patient=patient).latest("examination_date")
        except:
            examination = None
        context = {
            "title" : title,
            "active" : "examination",
            "patient" : patient,
            "examination" : examination,
            "userprofile" : userprofile,
            "nav_icon" : "far fa-file-alt",
            "main_nav" : "Examination",
            "sub_nav" : "Old Examination",
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)
    if request.method == "POST":
        pass

# @param examination tells the type of examination the user wants to see
#   that is if its either the previous or the medical history
@login_required
def prescription(request, prescription):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        title = "Nurse | prescription"
        response_url = "custom-admin"
    elif designation == "doctor":
        base_template = "doctor-base.html"
        title = "Nurse | prescription"
        response_url = "doctor"
    elif designation == "nurse":
        base_template = "nurse-base.html"
        title = "Nurse | prescription"
        response_url = "nurse"
    elif designation == "pharmacist":
        base_template = "pharmacy-base.html"
        title = "Pharmacy | prescription"
        response_url = "pharmacy"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "prescription.html"
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        context = {
            "title" : title,
            "active" : "prescription",
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-capsules",
            "main_nav" : "Prescription",
            "sub_nav" : "Search Patient By Dimebook ID or CNI",
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)
    if request.method == "POST":
        patient = Patient.objects.filter(Q(patient_id=request.POST["patient_id"].upper()) | Q(cni=request.POST["patient_id"]))
        if patient.exists():
            response = json.dumps(
                            {
                                "patient_id" : patient[0].patient_id,
                                "prescription" : prescription,
                                "response_url" : response_url
                            }
                        )
            return HttpResponse(response)
        else:
            response = json.dumps(
                {
                    "patient_id" : request.POST["patient_id"].upper(),
                    "prescription" : prescription,
                    "response_url" : response_url
                }
            )
            return HttpResponse(response, status=404)

@login_required
def newPrescription(request, patient_id):
    patient = Patient.objects.filter(patient_id=patient_id)[0]
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        response_redirect_url = "custom-admin"
        title = "Admin | new prescription"
    elif designation == "doctor":
        base_template = "doctor-base.html"
        response_redirect_url = "doctor"
        title = "Doctor | new prescription"
    elif designation == "nurse":
        base_template = "nurse-base.html"
        response_redirect_url = "nurse"
        title = "Nurse | new prescription"
    elif designation == "pharmacist":
        base_template = "pharmacy-base.html"
        response_redirect_url = "pharmacy"
        title = "Pharmacy | new prescription"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    patient = Patient.objects.filter(Q(patient_id=patient_id) | Q(cni=patient_id))[0]
    if request.method == "GET":
        template_name = "new-prescription.html"
        try:
            examination = Examination.objects.filter(patient=patient).latest("examination_date")
        except:
            examination = None
        try:
            labtest = LabTest.objects.filter(patient=patient).latest("labtest_date")
            labtest_details = LabTestDetail.objects.filter(labtest=labtest)
        except:
            labtest = None
            labtest_details = None
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        context = {
            "title" : title,
            "active" : "prescription",
            "patient" : patient,
            "examination" : examination,
            "labtest" : labtest,
            "labtest_details" : labtest_details,
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-capsules",
            "main_nav" : "Prescription",
            "sub_nav" : "New Prescription",
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)
    if request.method == "POST":
        prescription = Prescription(
                        patient = patient,
                        prescribed_by = request.user,
                    )
        prescription.save()
        extracted_prescription = extractDrugAndDose(request.POST["prescription"])

        for drug_dosage in extracted_prescription:
            PrescriptionDetail(
                prescription = prescription,
                drug = drug_dosage[0],
                dose = drug_dosage[1],
            ).save()

        return HttpResponse(response_redirect_url)

@login_required
def oldPrescription(request, patient_id):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        title = "Admin | old prescription"
    elif designation == "doctor":
        base_template = "doctor-base.html"
        title = "Doctor | old prescription"
    elif designation == "nurse":
        base_template = "nurse-base.html"
        title = "Nurse | old prescription"
    elif designation == "pharmacist":
        base_template = "pharmacy-base.html"
        title = "Pharmacy | old prescription"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "old-prescription.html"
        patient = Patient.objects.filter(Q(patient_id=patient_id) | Q(cni=patient_id))[0]
        try:
            prescription = Prescription.objects.filter(patient=patient).latest("prescription_date")
            prescription_details = PrescriptionDetail.objects.filter(prescription=prescription)
        except:
            prescription = None
            prescription_details = None
        userprofile = UserProfile.objects.filter(user=request.user)[0]

        context = {
            "title" : title,
            "active" : "prescription",
            "patient" : patient,
            "prescription" : prescription,
            "prescription_details" : prescription_details,
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-capsules",
            "main_nav" : "Prescription",
            "sub_nav" : "Old Prescription",
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)
    if request.method == "POST":
        pass

@login_required
def labTest(request, labtest):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        title = "Admin | Lab Test"
        response_url = "custom-admin"
    elif designation == "labtech":
        base_template = "labtech-base.html"
        title = "Labtech | Lab Test"
        response_url = "labtech"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "lab-test.html"
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        context = {
            "title" : title,
            "active" : "labtest",
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-flask",
            "main_nav" : "Laboratory Test",
            "sub_nav" : "Search Patient By Dimebook ID or CNI",
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)
    if request.method == "POST":
        patient = Patient.objects.filter(Q(patient_id=request.POST["patient_id"].upper()) | Q(cni=request.POST["patient_id"]))
        if patient.exists():
            response = json.dumps(
                            {
                                "patient_id" : patient[0].patient_id,
                                "labtest" : labtest,
                                "response_url" : response_url,
                            }
                        )
            return HttpResponse(response)
        else:
            response = json.dumps(
                {
                    "patient_id" : request.POST["patient_id"].upper(),
                    "labtest" : labtest,
                    "response_url" : response_url,
                }
            )
            return HttpResponse(response, status=404)

@login_required
def newLabTest(request, patient_id):
    patient = Patient.objects.filter(patient_id=patient_id)[0]
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        response_redirect_url = "custom-admin"
        title = "Admin | new Lab Test"
    elif designation == "labtech":
        base_template = "labtech-base.html"
        response_redirect_url = "labtech"
        title = "Labtech | new Lab Test"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "new-lab-test.html"
        try:
            examination = Examination.objects.filter(patient=patient).latest("examination_date")
        except:
            examination = None
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        context = {
            "title" : title,
            "active" : "labtest",
            "patient" : patient,
            "examination" : examination,
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-flask",
            "main_nav" : "Laboratory Test",
            "sub_nav" : "New Lab Test",
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)
    if request.method == "POST":
        labtest = LabTest(
                        patient = patient,
                        done_by = request.user,
                    )
        labtest.save()
        extracted_labtest = extractDrugAndDose(request.POST["labtest"])

        for lab_test in extracted_labtest:
            LabTestDetail(
                labtest = labtest,
                labtest_name = lab_test[0],
                labtest_result = lab_test[1],
            ).save()

        return HttpResponse(response_redirect_url)

@login_required
def oldLabTest(request, patient_id):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        title = "Admin | old Lab Test"
    elif designation == "labtech":
        base_template = "labtech-base.html"
        title = "Labtech | old Lab Test"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "old-lab-test.html"
        patient = Patient.objects.filter(Q(patient_id=patient_id) | Q(cni=patient_id))[0]
        try:
            labtest = LabTest.objects.filter(patient=patient).latest("labtest_date")
            labtest_details = LabTestDetail.objects.filter(labtest=labtest)
        except:
            labtest = None
            labtest_details = None
        userprofile = UserProfile.objects.filter(user=request.user)[0]

        context = {
            "title" : title,
            "active" : "labtest",
            "patient" : patient,
            "labtest" : labtest,
            "labtest_details" : labtest_details,
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-flask",
            "main_nav" : "Laboratory Test",
            "sub_nav" : "Old Lab Test",
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)
    if request.method == "POST":
        pass

def medicalHistory(request, patient_id):
    patient = Patient.objects.filter(patient_id=patient_id)[0]
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        response_redirect_url = "custom-admin"
        title = "Admin | Medical History"
        active = "examination"
        main_nav = "Examination"
        nav_icon = "far fa-file-alt"
    elif designation == "doctor":
        base_template = "doctor-base.html"
        response_redirect_url = "doctor"
        title = "Doctor | Medical History"
        active = "examination"
        main_nav = "Examination"
        nav_icon = "far fa-file-alt"
    elif designation == "nurse":
        base_template = "nurse-base.html"
        response_redirect_url = "nurse"
        title = "Nurse | Medical History"
        active = "examination"
        main_nav = "Examination"
        nav_icon = "far fa-file-alt"
    elif designation == "pharmacist":
        base_template = "pharmacy-base.html"
        response_redirect_url = "pharmacy"
        title = "Pharmacy | Medical History"
        active = "prescription"
        main_nav = "Prescription"
        nav_icon = "fas fa-capsules"
    elif designation == "labtech":
        base_template = "labtech-base.html"
        response_redirect_url = "labtech"
        title = "Labtech | Medical History"
        active = "labtest"
        main_nav = "Laboratory"
        nav_icon = "fas fa-flask"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "medical-history.html"
        try:
            examination = Examination.objects.filter(patient=patient).order_by("-examination_date")
        except:
            examination = None
        try:
            labtest = LabTest.objects.filter(patient=patient).order_by("-labtest_date")
            labtest_details = LabTestDetail.objects.filter(labtest=labtest)
        except:
            labtest = None
            labtest_details = None
        try:
            prescription = Prescription.objects.filter(patient=patient).order_by("-prescription_date")
        except:
            prescription = None

        userprofile = UserProfile.objects.filter(user=request.user)[0]
        client = Client.objects.filter(id=getClient(request.user).id)[0]
        clinic_logo = ""

        if client.logo:
            clinic_logo = client.logo.url

        context = {
            "title" : title,
            "active" : active,
            "patient" : patient,
            "userprofile" : userprofile,
            "nav_icon" : nav_icon,
            "main_nav" : main_nav,
            "sub_nav" : "Medical History",
            "base_template" : base_template,
            "client" : client,
            "clinic_logo" : clinic_logo,
        }
        return render(request, template_name, context)
    if request.method == "POST":
        start_date = timezone.datetime.strptime(request.POST["start"], '%B %d, %Y')
        end_date = timezone.datetime.strptime(request.POST["end"], '%B %d, %Y') + timezone.timedelta(days=1)
        examinations = Examination.objects.filter(Q(patient=patient) & Q(examination_date__range=[start_date, end_date])).order_by("-examination_date")
        prescriptions = Prescription.objects.filter(Q(patient=patient) & Q(prescription_date__range=[start_date, end_date])).order_by("-prescription_date")
        examination_list = []
        prescription_list = []
        checked_dates = []

        for examination in examinations:
            if examination.examination_date in checked_dates:
                continue
            prescription = Prescription.objects.filter(Q(patient=patient) & Q(prescription_date__date=examination.examination_date))
            examination_list.append(Examination.objects.filter(Q(patient=patient) & Q(examination_date__date=examination.examination_date)))
            prescription_list.append(prescription)
            checked_dates.append(examination.examination_date)

        html = ""
        medical_record = zip(examination_list, prescription_list)
        columns = ["DATE", "DIAGNOSTICS", "DOCTOR", "PRESCRIPTIONS", "NOTES/ATTACHMENTS"]
        rows = []
        for examinations, prescriptions in medical_record:
            sub_row = ["", "", "", "", "", ""]
            sub_row[0] = examinations[0].examination_date
            sub_row[2] = examinations[0].examined_by.first_name + " " + examinations[0].examined_by.last_name
            for examination in examinations:
                sub_row[1] += examination.symptoms
                sub_row[4] += examination.notes
            for prescription in prescriptions:
                if prescription:
                    prescription_details = PrescriptionDetail.objects.filter(prescription=prescription)
                    for prescription_detail in prescription_details:
                        sub_row[3] += (prescription_detail.drug + "(" + prescription_detail.dose + ")")
            rows.append(sub_row)

        response = json.dumps({"columns" : columns,"rows" : rows}, indent=4, default=str)
        return HttpResponse(response)

@login_required
def giveDrugSearch(request):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        response_redirect_url = "custom-admin"
        title = "Admin | Search Patient"
    elif designation == "pharmacist":
        base_template = "pharmacy-base.html"
        response_redirect_url = "pharmacy"
        title = "Pharmacy | Search Patient"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "pharmacy-search.html"
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        context = {
            "title" : title,
            "active" : "pharmacy",
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-tablets",
            "main_nav" : "Pharmacy",
            "sub_nav" : "Search Patient By Dimebook ID",
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)
    if request.method == "POST":
        patient = Patient.objects.filter(Q(patient_id=request.POST["patient_id"].upper()) | Q(cni=request.POST["patient_id"]))
        if patient.exists():
            response =  json.dumps(
                            {
                                "patient_id" : request.POST["patient_id"].upper(),
                                "response_redirect_url" : response_redirect_url,
                            }
                        )
            return HttpResponse(response)
        else:
            return HttpResponse(request.POST["patient_id"].upper(), status=404)

@login_required
def giveDrug(request, patient_id):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        response_redirect_url = "custom-admin"
        title = "Admin | Give Drugs"
    elif designation == "pharmacist":
        base_template = "pharmacy-base.html"
        response_redirect_url = "pharmacy"
        title = "Pharmacy | Give Drugs"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "give-drug.html"
        patient = Patient.objects.filter(Q(patient_id=patient_id) | Q(cni=patient_id))[0]
        try:
            prescription = Prescription.objects.filter(patient=patient).latest("prescription_date")
            prescription_details = PrescriptionDetail.objects.filter(prescription=prescription)
        except Exception as e:
            print(e)
            prescription = None
            prescription_details = None
        userprofile = UserProfile.objects.filter(user=request.user)[0]

        context = {
            "title" : title,
            "active" : "pharmacy",
            "patient" : patient,
            "prescription" : prescription,
            "prescription_details" : prescription_details,
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-tablets",
            "main_nav" : "Pharmacy",
            "sub_nav" : "Prescribe Drugs",
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)
    if request.method == "POST":
        for key in request.POST:
            if "drug" in key:
                prescription_id = key.split('_')[0]
                PrescriptionDetail.objects.filter(id=int(prescription_id)).update(
                    drug_alternative = request.POST[prescription_id+"_drug"],
                    dose_alternative = request.POST[prescription_id+"_dose"],
                    has_bought = True,
                    sold_by = request.user,
                )
        response =  json.dumps(
                            {
                                "patient_id" : patient_id,
                                "response_redirect_url" : response_redirect_url
                            }
                        )
        return HttpResponse(response)
@login_required
def invoice(request):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        response_redirect_url = "custom-admin"
        title = "Admin | Invoice"
    elif designation == "cashier":
        base_template = "cashier"
        response_redirect_url = "cashier"
        title = "Cashier | Invoice"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")
    
    if request.method == "GET":
        template_name = "search-invoice.html"
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        context = {
            "title" : title,
            "active" : "cashier",
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-dollar-sign",
            "main_nav" : "Invoice",
            "sub_nav" : "Search Patient By Dimebook ID or CNI",
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)
    
    if request.method == "POST":
        patient = Patient.objects.filter(Q(patient_id=request.POST["patient_id"].upper()) | Q(cni=request.POST["patient_id"]))
        if patient.exists():
            return HttpResponse(
                json.dumps(
                    {
                        "patient_id" : request.POST["patient_id"].upper(),
                        "response_redirect_url" : response_redirect_url
                    }
                )
            )
        else:
            return HttpResponse(request.POST["patient_id"].upper(), status=404)

@login_required
def newInvoice(request, patient_id):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        response_redirect_url = "custom-admin"
        title = "Admin | New Invoice"
    elif designation == "cashier":
        base_template = "cashier"
        response_redirect_url = "cashier"
        title = "Cashier | New Invoice"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "invoice.html"
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        patient = Patient.objects.filter(Q(patient_id=patient_id) | Q(cni=patient_id))

        prescription = Prescription.objects.filter(Q(patient=patient[0]) & Q(prescription_date__date=datetime.date.today()) & Q(has_paid=False))
        prescription_detail = None

        if prescription.exists():
            prescription = prescription.latest('prescription_date')
            prescription_detail = PrescriptionDetail.objects.filter(prescription=prescription)
        else:
            prescription = None

        labtest = LabTest.objects.filter(Q(patient=patient[0]) & Q(labtest_date__date=datetime.date.today()) & Q(has_paid=False))
        labtest_detail = None

        if labtest.exists():
            labtest = labtest.latest('labtest_date')
            labtest_detail = LabTestDetail.objects.filter(labtest=labtest)
        else:
            labtest = None

        context = {
            "title" : title,
            "active" : "cashier",
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-dollar-sign",
            "main_nav" : "New Invoice",
            "sub_nav" : "",
            "prescription_detail" : prescription_detail,
            "labtest_detail" : labtest_detail,
            "base_template" : base_template,
            "client" : getClient(request.user),
            "prescription" : prescription,
            "labtest" : labtest,
            "patient_id" : patient_id,
        }

        return render(request, template_name, context)

    if request.method == "POST":
        pass

@login_required
def invoiceHistorySearch(request):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        response_redirect_url = "custom-admin"
        title = "Admin | Search Invoice History"
    elif designation == "cashier":
        base_template = "cashier-base.html"
        response_redirect_url = "cashier"
        title = "Cashier | Search Invoice History"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "search-invoice-history.html"
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        context = {
            "title" : title,
            "active" : "cashier",
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-dollar-sign",
            "main_nav" : "Invoice History",
            "sub_nav" : "Search By Transaction ID",
            "base_template" : base_template,
            "client" : getClient(request.user),
        }
        return render(request, template_name, context)
    
    if request.method == "POST":
        transaction_id = request.POST["transaction_id"]
        invoice_stats = InvoiceStatistics.objects.filter(id=int(transaction_id.strip('0')))

        if invoice_stats.exists():
            return HttpResponse(
                json.dumps(
                    {
                        'transaction_id' : transaction_id,
                        'response_redirect_url' : response_redirect_url,
                    }
                )
            )
        else:
            print("Invoice statistics does not exist")
            return HttpResponse(
                json.dumps(
                    {
                        'transaction_id' : transaction_id
                    }
                ), status=404
            )

@login_required
def generateInvoice(request, patient_id):
    print(request.POST)

    userprofile = UserProfile.objects.filter(user=request.user)[0]
    client = Client.objects.filter(id=userprofile.client.id)[0]

    invoice_data = json.loads(request.POST['invoice_data'])
    prescriptions = invoice_data['prescription'].strip('@').split("@")
    prescriptions.remove('/')
    labtests = invoice_data['labtest'].strip('@').split('@')
    hospitalisation = invoice_data['hospitalisation'].split('@')
    
    prescription_html = ""
    for prescription in prescriptions:
        drug_html = "<td><font size=\"1\">{}</font></td>".format(prescription.strip('/').split('/')[3])
        quantity_html = "<td><font size=\"1\">{}</font></td>".format(prescription.strip('/').split('/')[0])
        unit_price_html = "<td><font size=\"1\">{}</font></td>".format(prescription.strip('/').split('/')[1])
        price_html = "<td><font size=\"1\">{}</font></td>".format(prescription.strip('/').split('/')[2])
        prescription_html += "<tr>" + drug_html + unit_price_html + quantity_html + price_html + "</tr>"

    labtest_html = ""
    for labtest in labtests:
        test_html = "<td><font size=\"1\">{}</font></td>".format(labtest.strip('/').split('/')[0])
        price_html = "<td><font size=\"1\">{}</font></td>".format(labtest.strip('/').split('/')[1])
        labtest_html += "<tr>" + test_html + price_html + "</tr>"

    hospitalisation_html = ""
    hosp_days_html = "<td><font size=\"1\">{}</font></td>".format(hospitalisation[0])
    unit_price_html = "<td><font size=\"1\">{}</font></td>".format(hospitalisation[1])
    price_html = "<td><font size=\"1\">{}</font></td>".format(hospitalisation[2])
    hospitalisation_html += "<tr>" + hosp_days_html + unit_price_html + price_html + "</tr>"

    
    patient = Patient.objects.filter(Q(patient_id=patient_id) | Q(cni=patient_id))[0]


    context = {
        "final_amount" : invoice_data['final_amount'],
        "given_amount" : invoice_data['given_amount'],
        "total" : invoice_data['total'],
        "discount" : invoice_data['discount'],
        "balance" : invoice_data['balance'],
        "prescription_html" : prescription_html,
        "labtest_html" : labtest_html,
        "hospitalisation_html" : hospitalisation_html,
        "client" : client,
        "date" : datetime.datetime.today()
    }
    prescription_id = invoice_data['prescription_id']
    hospitalisation =  HospitalisationPayment(
                        patient = patient,
                        hosp_days = hospitalisation[0],
                        unit_price = hospitalisation[1],
                        total = hospitalisation[2]
                    )
    hospitalisation.save()
    if len(prescription_id):
        prescription = Prescription.objects.filter(id=int(prescription_id))
        prescription.update(has_paid=True)
    labtest_id = invoice_data['labtest_id']
    if len(labtest_id):
        labtest = LabTest.objects.filter(id=int(labtest_id))
        labtest.update(has_paid=True)

    invoice_stats = InvoiceStatistics(
                        patient = patient,
                        prescription = prescription[0],
                        labtest = labtest[0],
                        hospitalisation = hospitalisation,
                        total = invoice_data['total'],
                        discount = invoice_data['discount'],
                        balance = invoice_data['balance'],
                        given_amount = invoice_data['given_amount'],
                        final_amount = invoice_data['final_amount']
                    )
    invoice_stats.save()
    context["sales_id"] = str(invoice_stats.id).zfill(5)

    template_name = "invoice-receipt.html"
    template = render_to_string(template_name, context)
    return HttpResponse(template)

@login_required
def invoiceHistory(request, transaction_id):
    designation = getWorkerDesignation(request.user)
    if designation == "admin":
        base_template = "admin-base.html"
        response_redirect_url = "custom-admin"
        title = "Admin | Invoice History"
    elif designation == "cashier":
        base_template = "cashier-base.html"
        response_redirect_url = "cashier"
        title = "Cashier | Invoice History"
    else:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    invoice_stats = InvoiceStatistics.objects.filter(id=int(transaction_id.strip('0')))[0]
    if request.method == 'GET':
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        patient = Patient.objects.filter(patient_id=invoice_stats.patient.patient_id)[0]
        template_name = "invoice-history.html"
        context =   {
                        "title" : title,
                        "active" : "cashier",
                        "userprofile" : userprofile,
                        "nav_icon" : "fas fa-dollar-sign",
                        "main_nav" : "Invoice History",
                        "sub_nav" : patient.name,
                        "base_template" : base_template,
                        "client" : getClient(request.user),
                        'total' : invoice_stats.total,
                        'final_amount' : invoice_stats.final_amount,
                        'given_amount' : invoice_stats.given_amount,
                        'discount' : invoice_stats.discount,
                        'balance' : invoice_stats.balance
                    }
        return render(request, template_name, context)
            

@login_required
def editInformation(request):
    if getWorkerDesignation(request.user) != "admin":
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    userprofile = UserProfile.objects.filter(user=request.user)[0]
    client = Client.objects.filter(id=userprofile.client.id)[0]

    if request.method == "GET":
        template_name = "admin-edit-information.html"
        context = {
            "title" : "Admin | edit information",
            "active" : "home",
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-hospital",
            "main_nav" : "Home",
            "sub_nav" : "Edit Information",
            "client" : client,
        }
        return render(request, template_name, context)

    if request.method == "POST":
        clinic_logo = None
        try:
            clinic_logo = request.FILES['clinic_logo']
            fs = FileSystemStorage(location="media/clinic-logo", base_url="clinic-logo/")
            for filename in glob.glob(settings.MEDIA_ROOT+"/clinic-logo/"+"clinic_"+str(client.id)+"_logo_*"):
                os.remove(filename)
            picname = fs.save("clinic_"+str(client.id)+"_logo_"+clinic_logo.name, clinic_logo)
            uploaded_pic_url = fs.url(picname)
        except Exception as e:
            pass

        client = Client.objects.filter(id=getClientId(request.user))[0]

        client.name = request.POST["client_name"]
        client.address = request.POST["address"]
        client.tel = request.POST["tel"]
        client.email = request.POST["email"]

        if clinic_logo:
            client.logo = uploaded_pic_url
        client.save()
        return HttpResponse("")

def getClientId(user):
    userprofile = UserProfile.objects.filter(user=user)[0]
    return userprofile.client.id

def getWorkerDesignation(user):
    userprofile = UserProfile.objects.filter(user=user)[0]
    return userprofile.designation

def changeWorkerPassword(request, worker_id):
    userprofile = UserProfile.objects.filter(user_id=worker_id)[0]

    if getWorkerDesignation(request.user) != "admin":
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    if request.method == "GET":
        template_name = "change-password.html"
        base_template = "admin-base.html"
        context = {
            'base_template' : base_template,
            'title' : "Admin | change worker password",
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-lock",
            "main_nav" : "Password",
            "sub_nav" : "Change Password",
            "change_worker_password" : True,
            "client" : getClient(request.user),
            "worker" : userprofile,
        }
        return render(request, template_name, context)

    if request.method == "POST":
        user = User.objects.get(username=userprofile.user)
        user.set_password(request.POST["password1"])
        user.save()
        return HttpResponse("change_worker_password")