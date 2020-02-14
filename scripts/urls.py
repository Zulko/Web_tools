from django.urls import path
from . import views


app_name = 'scripts'

urlpatterns = [
    path('spotting/', views.spotting_view, name='spotting'),
    path('dnacauldron/', views.dnacauldron_view, name='dnacauldron'),
    path('moclo_db/', views.moclo_db_view, name='moclodb'),
    path('moclo/', views.moclo_view, name='moclo'),
    path('pcr_db/', views.pcr_db_view, name='pcrdb'),
    path('echo_transfer_db/', views.echo_transfer_db_view, name='echo_transfer_db'),
    path('echo_transfer/', views.echo_transfer_view, name='echo_transfer'),
]