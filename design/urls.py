from django.urls import path
from . import views


app_name = 'design'

urlpatterns = [

    # Design views
    path('', views.design_view, name='design_view'),
    path('add_experiment/', views.experiment_add, name='experiment_add'),
    path('add_step/', views.step_add, name='step_add'),

    # Experiment views
    path('experiment<int:experiment_id>/', views.experiment_view, name='experiment_view'),
    path('experiment<int:experiment_id>/delete/', views.experiment_delete, name='experiment_delete'),
    path('experiment<int:experiment_id>/update/', views.experiment_update, name='experiment_update'),

]