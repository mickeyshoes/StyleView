from django.urls import path
from . import views

urlpatterns = [
    path('test_print', views.print_hello),
]