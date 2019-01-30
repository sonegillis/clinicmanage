from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from mainapp.models import Client, UserProfile, Patient, SuperAdministratorInformation
from django.core.files.storage import FileSystemStorage
import glob, os
import json
from django.conf import settings

# Create your views here.

def homePage(request):
    userprofile = User.objects.filter(username=request.user)[0]
    template_name = "superadmin-homepage.html"
    context = {
        "title" : "Superadmin | home",
        "active" : "home",
        "userprofile" : userprofile
    }
    return render(request, template_name, context)

@login_required
def Clients(request):
    template_name = "clients.html"
    clients = Client.objects.all()
    userprofile = User.objects.filter(username=request.user)[0]
    context = {
        "title" : "Superadmin | clients",
        "active" : "clients",
        "clients" : clients,
        "userprofile" : userprofile,
    }
    return render(request, template_name, context)

@login_required
def addClient(request):
    userprofile = User.objects.filter(username=request.user)[0]
    if request.method == "GET":
        template_name = "add-client.html"
        context = {
                "title" : "Superadmin | add client",
                "active" : "clients",
                "userprofile" : userprofile
        }
        return render(request, template_name, context)
        
    if request.method == "POST":
        clinic_logo = request.FILES.get('clinic_logo', None)
        client =  Client (
                    name = request.POST["client_name"],
                    address = request.POST["address"],
                    tel = request.POST["tel"],
                    email = request.POST["email"]
                )
        client.save()
        if clinic_logo:
            fs = FileSystemStorage(location="media/clinic_logo", base_url="clinic-logo/")
            picname = fs.save("clinic_"+str(client.id)+"_pic_"+clinic_logo.name, clinic_logo)
            uploaded_pic_url = fs.url(picname)
        else:
            uploaded_pic_url = None
        client.update(logo = uploaded_pic_url)
        response = json.dumps(
            {
                "client_name" : request.POST["client_name"],
                "msg" : "added",
                "url" : "/superadmin/clients/"
            }
        )
        return HttpResponse(response)

@login_required
def editClient(request, client_id):
    userprofile = User.objects.filter(username=request.user)[0]
    client = Client.objects.filter(id=client_id)[0]
    if request.method == "GET":
        template_name = "edit-client.html"
        context = {
            "title" : "Superadmin | edit client",
            "active" : "clients",
            "client" : client,
            "userprofile" : userprofile
        }
        return render(request, template_name, context)
    
    if request.method == "POST":
        
        clinic_logo = request.FILES.get('clinic_logo', None)
        if clinic_logo:
            fs = FileSystemStorage(location="media/clinic-logo", base_url="clinic-logo/")
            for filename in glob.glob(settings.MEDIA_ROOT+"/clinic-logo/"+"clinic_"+str(client.id)+"_pic_*"):
                os.remove(filename)
            picname = fs.save(clinic_logo.name, clinic_logo)
            uploaded_pic_url = fs.url(picname)
        else:
            uploaded_pic_url = None
        
        client.name = request.POST["client_name"]
        client.address = request.POST["address"]
        client.tel = request.POST["tel"]
        client.email = request.POST["email"]
        client.logo = uploaded_pic_url

        client.save()

        response = {
                    "client_name" : request.POST["client_name"],
                    "msg" : "editted",
                    "url" : "/superadmin/clients/"
                }
        response = json.dumps(response)
            
        return HttpResponse(response)

@login_required
def deleteClient(request):
    clients_to_delete = request.POST.getlist("clients_to_delete[]")
    for client in clients_to_delete:
        Client.objects.filter(id=int(client)).delete()
    return HttpResponseRedirect(reverse("superadmin:clients"))

@login_required
def Administrators(request):
    template_name = "admins.html"
    userprofile = User.objects.filter(username=request.user)[0]
    admins = UserProfile.objects.filter(designation="admin")
    context = {
        "title" : "Superadmin | admins",
        "active" : "admins",
        "admins" : admins,
        "userprofile" : userprofile,
    }
    return render(request, template_name, context)

@login_required
def addAdmin(request):
    if request.method == "GET":
        template_name = "add-admin.html"
        userprofile = User.objects.filter(username=request.user)[0]
        clients = Client.objects.all()
        context = {
                "title" : "Superadmin | add admin",
                "active" : "admins",
                "clients" : clients,
                "userprofile" : userprofile
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
            picname = fs.save("user_"+str(user[0].id)+"_pic_"+profile_pic.name, profile_pic)
            uploaded_pic_url = fs.url(picname)
        else:
            uploaded_pic_url = None
        UserProfile(
            user = user,
            client_id = request.POST["client"],
            designation = "admin",
            tel = request.POST["tel"],
            profile_pic = uploaded_pic_url,
        ).save()
        response = json.dumps(
            {
                "first_name" : request.POST["first_name"],
                "msg" : "added",
                "url" : "/superadmin/admins/"
            }
        )
        return HttpResponse(response)

@login_required
def editAdmin(request, admin_id):
    userprofile = User.objects.filter(username=request.user)[0]
    if request.method == "GET":
        template_name = "edit-admin.html"
        user = User.objects.filter(id=admin_id)[0]
        admin = UserProfile.objects.filter(user=user)[0]
        clients = Client.objects.all()
        context = {
            "title" : "Superadmin | edit admint",
            "active" : "admins",
            "admin" : admin,
            "clients" : clients,
            "userprofile" : userprofile,
        }
        return render(request, template_name, context)
    
    if request.method == "POST":
        user = User.objects.filter(id=admin_id)
        user.update(
            first_name = request.POST["first_name"],
            last_name = request.POST["last_name"],
            email = request.POST["email"],
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
        UserProfile.objects.filter(user=user).update(
            client_id = request.POST["client"],
            designation = "admin",
            tel = request.POST["tel"],
            profile_pic = uploaded_pic_url,
        )
        response = json.dumps(
            {
                "first_name" : request.POST["first_name"],
                "msg" : "editted",
                "url" : "/superadmin/admins/"
            }
        )
        return HttpResponse(response)

@login_required
def deleteAdmin(request):
    admins_to_delete = request.POST.getlist("users_to_delete[]")
    for admin in admins_to_delete:
        User.objects.filter(id=int(admin)).delete()

    return HttpResponseRedirect(reverse("superadmin:admins"))

@login_required
def Patients(request):
    userprofile = User.objects.filter(username=request.user)[0]
    patients = Patient.objects.all()
    if request.method == "GET":
        template_name = "patients.html"
        context = {
            "title" : "Superadmin | patients",
            "active" : "patients",
            "userprofile" : userprofile,
            "patients" : patients
        }
        return render(request, template_name, context)

@login_required
def editInformation(request):
    if not request.user.is_superuser:
        return HttpResponse("You do not have permission to access this page!! This account will be reported")

    userprofile = User.objects.filter(id=request.user.id)[0]

    try:
        superadmin = SuperAdministratorInformation.objects.get(id=1)
    except:
        superadmin = None

    if request.method == "GET":
        template_name = "superadmin-edit-information.html"
        context = {
            "title" : "SuperAdmin | edit information",
            "active" : "home",
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-hospital",
            "main_nav" : "Home",
            "sub_nav" : "Edit Information",
            "superadmin" : superadmin,
        }
        return render(request, template_name, context)

    if request.method == "POST":
        image1, image2, image3, image4, image5, image6 = [None] * 6
        uploaded_pic_url1, uploaded_pic_url2, uploaded_pic_url3, uploaded_pic_url4, uploaded_pic_url5, uploaded_pic_url6 = [None] * 6

        image1 = request.FILES.get('image1', None)
        image2 = request.FILES.get('image2', None)
        image3 = request.FILES.get('image3', None)
        image4 = request.FILES.get('image4', None)
        image5 = request.FILES.get('image5', None)
        image6 = request.FILES.get('image6', None)

        fs = FileSystemStorage(location="media/homepage-pics", base_url="homepage-pics/")
        if image1:
            picname = fs.save("homepage_image1_pic_"+image1.name, image1)
            uploaded_pic_url1 = fs.url(picname)
        else:
            uploaded_pic_url1 = None
        
        if image2:
            picname = fs.save("homepage_image2_pic_"+image2.name, image2)
            uploaded_pic_url2 = fs.url(picname)
        else:
            uploaded_pic_url2= None
        
        if image3:
            picname = fs.save("homepage_image3_pic_"+image3.name, image3)
            uploaded_pic_url3 = fs.url(picname)
        else:
            uploaded_pic_url3 = None

        if image4:
            picname = fs.save("homepage_image4_pic_"+image4.name, image4)
            uploaded_pic_url4 = fs.url(picname)
        else:
            uploaded_pic_url4 = None

        if image5:
            picname = fs.save("homepage_image5_pic_"+image5.name, image5)
            uploaded_pic_url5 = fs.url(picname)
        else:
            uploaded_pic_url5 = None

        if image6:
            picname = fs.save("homepage_image6_pic_"+image6.name, image6)
            uploaded_pic_url6 = fs.url(picname)
        else:
            uploaded_pic_url6 = None
        
        try:
            superadmin = SuperAdministratorInformation.objects.filter(id=1)[0]
            superadmin.email = request.POST["email"]
            superadmin.tel = request.POST["tel"]

            if image1:
                for filename in glob.glob(settings.MEDIA_ROOT+"/homepage-pics/homepage_image1_pic_*"):
                    os.remove(filename)
                picname = fs.save("homepage_image1_pic_"+image1.name, image1)
                superadmin.image1 = fs.url(picname)

            if image2:
                for filename in glob.glob(settings.MEDIA_ROOT+"/homepage-pics/homepage_image2_pic_*"):
                    os.remove(filename)
                picname = fs.save("homepage_image2_pic_"+image2.name, image2)
                superadmin.image2 = fs.url(picname)

            if image3:
                for filename in glob.glob(settings.MEDIA_ROOT+"/homepage-pics/homepage_image3_pic_*"):
                    os.remove(filename)
                picname = fs.save("homepage_image3_pic_"+image3.name, image3)
                superadmin.image3 = fs.url(picname)

            if image4:
                for filename in glob.glob(settings.MEDIA_ROOT+"/homepage-pics/homepage_image4_pic_*"):
                    os.remove(filename)
                picname = fs.save("homepage_image4_pic_"+image4.name, image4)
                superadmin.image4 = fs.url(picname)

            if image5:
                for filename in glob.glob(settings.MEDIA_ROOT+"/homepage-pics/homepage_image5_pic_*"):
                    os.remove(filename)
                picname = fs.save("homepage_image5_pic_"+image5.name, image5)
                superadmin.image5 = fs.url(picname)

            if image6:
                for filename in glob.glob(settings.MEDIA_ROOT+"/homepage-pics/homepage_image6_pic_*"):
                    os.remove(filename)
                picname = fs.save("homepage_image6_pic_"+image6.name, image6)
                superadmin.image6 = uploaded_pic_url6

            superadmin.save()
        except:
            SuperAdministratorInformation(
                email = request.POST["email"],
                tel = request.POST["tel"],
                image1 = uploaded_pic_url1,
                image2 = uploaded_pic_url2,
                image3 = uploaded_pic_url3,
                image4 = uploaded_pic_url4,
                image5 = uploaded_pic_url5,
                image6 = uploaded_pic_url6
            ).save()
        
        return HttpResponse("")