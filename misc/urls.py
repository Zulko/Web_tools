from django.urls import path
from . import views


app_name = 'misc'

urlpatterns = [
    path('genbank/', views.genbank, name='genbank'),
    path('primer/', views.primer, name='primer'),
    path('normalization/', views.normalization, name='normalization'),
    path('nrc_script/', views.nrc_sequence, name='nrc_sequence'),
    path('echo_transfer/', views.echo_transfer_db, name='echo_transfer_db'),
]