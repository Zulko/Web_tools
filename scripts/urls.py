from django.urls import path
from . import views


app_name = 'scripts'

urlpatterns = [
    path('spotting/', views.spotting_view, name='spotting'),
    path('combinatorial/', views.combinatorial_view, name='combinatorial'),
    path('dnacauldron/', views.dnacauldron_view, name='dnacauldron'),
    path('moclo/', views.moclo_view, name='moclo'),
    path('moclo_db/', views.moclo_db_view, name='moclodb'),
    path('pcr_db/', views.pcr_db_view, name='pcrdb'),
]