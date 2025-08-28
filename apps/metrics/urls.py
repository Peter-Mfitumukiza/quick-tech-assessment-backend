from django.urls import path
from . import views

app_name = 'metrics'

urlpatterns = [
    path('summary/', views.metrics_summary, name='metrics_summary'),
]