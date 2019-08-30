from django.urls import path
from . import views


app_name = 'design'

urlpatterns = [

    # Experiment views
    path('', views.design_view, name='design_view'),
    path('add_experiment/', views.experiment_add, name='experiment_add'),
    path('add_step/', views.step_add, name='step_add'),

]