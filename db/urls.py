from django.urls import path
from . import views


app_name = 'db'

urlpatterns = [

    # Plate views
    path('', views.plate_list, name='index'),
    # path('inventory_list/', views.plate_list_inventory, name='inventory_plates'),
    # path('reagent_list/', views.plate_list_reagents, name='reagents_plates'),
    # path('process_list/', views.plate_list_process, name='process_plates'),
    path('plate<int:plate_id>/', views.plate_view, name='plate'),
    path('add_plate/', views.plate_add, name='plate_add'),
    path('add_plate_file/', views.plate_add_file, name='plate_file_add'),
    path('export/plate<int:plate_id>/', views.plate_export, name='plate_export'),
    path('print/plate<int:plate_id>/', views.plate_print, name='plate_print'),
    path('update/plate<int:plate_id>/', views.plate_update, name='plate_update'),
    path('delete/plate<int:plate_id>/', views.plate_delete, name='plate_delete'),

    # Wells views
    path('delete/plate<int:plate_id>/<int:well_id>', views.well_delete, name='well_delete'),
    path('plate<int:plate_id>/<int:well_id>', views.well, name='well'),
    path('add_well/<int:plate_id>', views.well_add, name='well_add'),
    path('update/plate<int:plate_id>/<int:well_id>', views.well_update, name='well_update'),

    # Sample views
    path('view_sample/', views.samples_list, name='samples_list'),
    path('view_sample/<int:sample_id>', views.sample, name='sample'),
    path('add_sample/', views.add_sample, name='sample_add'),
    path('add_sample_file/', views.add_file_sample, name='sample_file_add'),
    path('export_sample/export', views.sample_export, name='sample_export'),
    path('delete/sample<int:sample_id>/', views.sample_delete, name='sample_delete'),
    path('update/sample<int:sample_id>/', views.sample_update, name='sample_update'),
    # path('view_sample/table', views.myModel_asJson, name='my_ajax_url'),

    # File views
    path('file_sharing/', views.file_sharing, name='file_sharing'),
    path('file_sharing/<int:file_id>', views.delete_file, name='file_delete'),

    # Machine views
    path('view_machine/', views.machine_list, name='machine_list'),
    path('view_machine/<int:machine_id>', views.machine, name='machine'),
    path('add_machine/', views.machine_add, name='machine_add'),
    path('update_machine/<int:machine_id>', views.machine_update, name='machine_update'),
    path('delete_machine<int:machine_id>/', views.machine_delete, name='machine_delete'),

    # Project views
    path('view_project/', views.project_list, name='project_list'),
    path('view_project/<int:project_id>', views.project, name='project'),
    path('add_project/', views.project_add, name='project_add'),
    path('update_project/<int:project_id>', views.project_update, name='project_update'),
    path('delete/project<int:project_id>/', views.project_delete, name='project_delete'),

]