from django.urls import path
from . import views


app_name = 'db'

urlpatterns = [
    # path('', views.IndexView.as_view(), name='index'),
    path('', views.plate_list, name='index'),
    # path('', views.search_plate, name='index'),

    path('plate<int:plate_id>/', views.plate_view, name='plate'),
    path('export/plate<int:plate_id>/', views.plate_export, name='plate_export'),

    path('plate<int:plate_id>/<int:well_id>', views.well, name='well'),
    # path('plate<int:plate_id>/<int:well_id/<int:sample_id>', views.sample, name='sample'),

    path('add_data/', views.create_sample, name='add_data'),
    # path('add_data/file', views.upload_sample, name='add_file_data'),

    path('view_sample/', views.sample_list, name='view_sample'),
    path('view_sample/export', views.export_sample, name='export_sample'),
    path('view_sample/<int:sample_id>', views.sample, name='sample'),

    path('file_sharing/', views.file_sharing, name='file_sharing'),
    path('file_sharing/<int:file_id>', views.delete_file, name='delete_file'),

]