from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('upload/', views.upload_csv, name='upload_csv'),
]