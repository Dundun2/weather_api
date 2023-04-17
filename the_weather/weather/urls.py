
from django.urls import path
from . import views

urlpatterns = [
    path('search/',views.result),
    path('',views.start),
]