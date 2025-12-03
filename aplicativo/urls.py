from django.urls import path
from . import views


app_name = 'aplicativo'


urlpatterns = [
    path('', views.index, name='index'),
]
