
from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index),
    path('search/',views.result),
    path('',views.start),
    path('result2/',views.result2),
    path('result3/',views.result3)

]