from django.urls import path, re_path
from . import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('query', views.query, name='query'),
    re_path(r'^[0-9]+$', views.gid, name='gid'),
]
