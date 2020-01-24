from django.urls import path
from . import views


app_name = 'misc'

urlpatterns = [
    path('genbank/', views.genbank_view, name='genbank'),
    path('primer/', views.primer_view, name='primer'),
    path('normalization/', views.normalization_view, name='normalization'),
    path('echo_transfer_db/', views.echo_transfer_db_view, name='echo_transfer_db'),
]