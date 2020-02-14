from django.urls import path
from . import views


app_name = 'misc'

urlpatterns = [
    path('genbank/', views.genbank_view, name='genbank'),
    path('primer/', views.primer_view, name='primer'),
    path('normalization/', views.normalization_view, name='normalization'),
    path('combinatorial/', views.combinatorial_view, name='combinatorial'),
    path('dot_plate/', views.dot_plate_view, name='dot_plate'),
]