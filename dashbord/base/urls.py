from django.urls import path
from .views import *


urlpatterns = [
    path('', home_view, name = "home"),
    path('result/', result, name= 'result_page')
]
