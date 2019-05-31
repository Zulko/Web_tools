from django.urls import path
from . import views


app_name = 'scripts'

urlpatterns = [
    path('spotting/', views.spotting, name='spotting'),
    path('combinatorial/', views.combinatorial, name='combinatorial'),
    path('assembly/', views.assembly, name='assembly'),
    path('moclo/', views.moclo, name='moclo'),
    path('moclo_db/', views.moclo_db, name='moclodb'),
]