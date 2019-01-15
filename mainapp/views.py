from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile, Patient, SuperAdministratorInformation
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.utils.crypto import get_random_string
from django.contrib.auth import(
    authenticate,
    login,
    logout
)
import time, re

# Create your views here.

def homePage(request):
    if request.user.is_authenticated():
        if request.user.is_superuser:
            return HttpResponseRedirect(reverse("superadmin:home"))
        designation = UserProfile.objects.filter(user=request.user)[0].designation
        if designation == "admin":
            return HttpResponseRedirect(reverse("custom-admin:home"))
        if designation == "doctor":
            return HttpResponseRedirect(reverse("doctor:examination", args=("new",)))
        if designation == "nurse":
            return HttpResponseRedirect(reverse("nurse:examination", args=("new",)))
        if designation == "labtech":
            return HttpResponseRedirect(reverse("labtech:lab-test", args=("new",)))
        if designation == "pharmacist":
            return HttpResponseRedirect(reverse("pharmacy:prescription", args=("new",)))
        if designation == "cashier":
            return HttpResponseRedirect(reverse("cashier:invoice"))

    template_name = "homepage.html"
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        # authenticate user
        user = authenticate(request, username=username, password=password)

        # no authentication is none
        # verify that the authentication is done if only the user belongs to that pharmacy as an admin or normal user
        if user is not None:
            login(request, user)
            # if user is a superuser then he is the superadmin
            if user.is_superuser:
                return HttpResponseRedirect(reverse('superadmin:home'))
            else:
                user_profile = UserProfile.objects.filter(Q(user=user))[0] # normal user verification
                if user_profile.designation == "admin":
                    return HttpResponseRedirect(reverse('custom-admin:home'))
                if user_profile.designation == "doctor":
                    return HttpResponseRedirect(reverse('doctor:examination', args=("new",)))
                if user_profile.designation == "nurse":
                    return HttpResponseRedirect(reverse('nurse:examination', args=("new",)))
                if user_profile.designation == "pharmacist":
                    return HttpResponseRedirect(reverse('pharmacy:prescription', args=("new",)))
                if user_profile.designation == "labtech":
                    return HttpResponseRedirect(reverse('labtech:lab-test', args=("new",)))

            return HttpResponseRedirect(reverse("home"))
            
        else:
            context = {
                "error" :   "Username or Password incorrect"
            }
            return render(request, template_name, context)
    
    if request.method == "GET":
        try:
            superadmin = SuperAdministratorInformation.objects.get(id=1)
        except:
            superadmin = None
        return render(request, template_name, {"superadmin" : superadmin})

def loginView(request, pharmacy_link):
    if request.method == "GET":
        context = {}
        if request.user.is_authenticated():
            # checking if user is an administrator or a sales person
            qs1 = Administrators.objects.filter(Q(pharmacy=qs[0]) & Q(user=request.user))

            if qs1.exists():     # user is an admin
                today = date.today()
                # get the total sales made that day
                price = Sales.objects.filter(Q(pharmacy=qs[0]) & Q(date__date=today)).aggregate(Sum('price'))
                if price["price__sum"]:
                    price = price["price__sum"]
                else:
                    price = 0
                template_name = "pharmacy_admin_home.html"

                context["user"] = qs1[0]
                context["active"] = "dashboard"
                context["daily_sales"] = price
                context["notifications"] = getNotifications(request.user)
            else:
                qs1 = UserProfiles.objects.filter(Q(pharmacy=qs[0]) & Q(user=request.user))
                
                if qs1.exists():
                    context["user"] = qs1[0] # user is a normal user
                    # get if the user is sales agent or a stock manager
                    user_type = qs1[0].user_type
                    if user_type == "sales_agent":
                        context["user_type"] = user_type
                        context["active"] = "sales"
                        context["notifications"] = getNotifications(request.user)
                        template_name = "pharmacy_user_home.html"

                    if user_type == "stock_manager":
                        context["user_type"] = "stock_manager"
                        context["active"] = "stock"
                        context["notifications"] = getNotifications(request.user)
                        template_name = "pharmacy_stockmanager_home.html"

                else:
                    logout(request)
                    return HttpResponseRedirect("/"+pharmacy_link+"/")

            context["pharmacy"] = qs[0]
            context["pharmacy_link"] = "/"+pharmacy_link+"/logout/"
            return render(request, template_name, context)
        else:
            template_name = "login.html"
            context = {
                "pharmacy": qs[0]
            }
            return render(request, template_name, context)

def logoutView(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


@login_required
def verifyUsername(request):
    qs = User.objects.filter(username=request.POST["username"])
    if qs.exists():
        return HttpResponse("false")
    return HttpResponse("true")

"""
    This function will keep on generate
    a 10 char alphanumeric string until
    it doesn't find that ID in the Patient table
    This will be the patient Dimebook ID
"""

def generateUniquePatientID():
    time.sleep(1)
    while(True):
        unique_id = get_random_string(length=6).upper()
        patient = Patient.objects.filter(patient_id=unique_id)
        if patient.exists():
            continue
        else:
            break
    return unique_id

def extractDrugAndDose(prescriptions):
    prescriptions = prescriptions.split("\r\n")
    extracted_prescription = []
    for prescription in prescriptions:
        if prescription != "":
            matchObj = re.match(r'(.*) \((.*)\)', prescription, re.M|re.I)
            extracted_prescription.append([matchObj.group(1), matchObj.group(2)])
    return extracted_prescription

@login_required    
def changePassword(request):
    if request.user.is_superuser:
        userprofile = User.objects.filter(username=request.user)[0]
        base_template = "superadmin-base.html"
        base_url = "superadmin:home"
        title = "Superadmin | Change Password"
    else:
        userprofile = UserProfile.objects.filter(user=request.user)[0]
        if userprofile.designation == "admin":
            base_template = "admin-base.html"
            base_url = "custom-admin:home"
            title = "Admin | Change Password"

        if userprofile.designation == "doctor":
            base_template = "doctor-base.html"
            base_url = "doctor:examination, new"
            title = "Doctor | Change Password"
        
        if userprofile.designation == "nurse":
            base_template = "nurse-base.html"
            base_url = "nurse:examination, new"
            title = "Nurse | Change Password"
        
        if userprofile.designation == "labtech":
            base_template = "labtech-base.html"
            base_url = "labtech:lab-test, new"
            title = "Labtech | Change Password"
        
        if userprofile.designation == "pharmacist":
            base_template = "pharmacy-base.html"
            base_url = "pharmacy:prescription, new"
            title = "Pharmacy | Change Password"

    if request.method == "GET":
        template_name = "change-password.html"        
        context = {
            'base_template' : base_template,
            'title' : title,
            "userprofile" : userprofile,
            "nav_icon" : "fas fa-lock",
            "main_nav" : "Password",
            "sub_nav" : "Change Password",
            "client" : getClient(request.user)
        }
        return render(request, template_name, context)

    if request.method == "POST":
        user = User.objects.get(username=request.user)
        user.set_password(request.POST["password1"])
        user.save()
        logout(request)
        return HttpResponse()

def getClient(user):
    return UserProfile.objects.filter(user=user)[0].client
