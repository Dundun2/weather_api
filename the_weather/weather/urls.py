
from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index),
    path('search/',views.mapToGrid),
    path('',views.start)
]