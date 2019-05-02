from django.urls import path
from . import views


app_name = 'db'

urlpatterns = [
    path('', views.index, name='index',),
    path('<int:plate_id>/', views.plate, name='plate'),
    path('<int:plate_id>/<int:well_id>', views.well, name='well'),
]