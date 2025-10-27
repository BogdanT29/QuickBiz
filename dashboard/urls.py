from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('setup/', views.setup_business, name='setup_business'),
    path('', views.dashboard_view, name='dashboard'),
    
]