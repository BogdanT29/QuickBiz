"""
URL configuration for quickbiz_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls), # Admin
    path('', views.homepage, name='homepage'),  # Homepage
    path('about/', views.about, name='about'), # About page
    path('dashboard/', include('dashboard.urls')), # Main application dashboard                        #
    path('users/', include('users.urls')), # User registration and profile management
    path('accounts/', include('allauth.urls')),  # Google OAuth2
    path('', include('businesses.urls')),
]
