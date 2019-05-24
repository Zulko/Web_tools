from django.urls import path
from . import views


app_name = 'misc'

urlpatterns = [
    path('genbank/', views.genbank, name='genbank'),
    path('primer/', views.primer, name='primer'),
]