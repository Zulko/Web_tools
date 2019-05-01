from django.urls import path
from . import views

app_name = 'db'

urlpatterns = [
    # /db/
    path('', views.index, name='index'),

    # /db/
    path('(<int:plate_id>/', views.plate, name='plate'),
]