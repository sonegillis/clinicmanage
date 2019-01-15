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
from django.conf.urls import url, include
from mainapp.views import homePage, verifyUsername, logoutView
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', homePage, name="home"),
    url(r'^verify-username/$', verifyUsername),
    url(r'^logout/$', logoutView, name="logout"),
    url(r'^developer/', admin.site.urls),
    url(r'^superadmin/', include('superadmin.urls', namespace='superadmin')),
    url(r'^custom-admin/', include('custom_admin.urls', namespace='custom-admin')),
    url(r'^doctor/', include('doctor.urls', namespace='doctor')),
    url(r'^nurse/', include('nurse.urls', namespace='nurse')),
    url(r'^labtech/', include('labtech.urls', namespace='labtech')),
    url(r'^pharmacy/', include('pharmacy.urls', namespace='pharmacy')),
    url(r'^cashier/', include('cashier.urls', namespace='cashier')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
