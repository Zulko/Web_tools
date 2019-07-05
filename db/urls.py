from django.urls import path
from . import views


app_name = 'db'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    # path('', views.index, name='index',),
    path('plate<int:plate_id>/', views.plate, name='plate'),
    path('plate<int:plate_id>/<int:well_id>', views.well, name='well'),
    # path('plate<int:plate_id>/<int:well_id/<int:sample_id>', views.sample, name='sample'),

    # path('add_data', views.add_data, name='add_data',),
    path('add_data', views.create_sample, name='add_data',),
    path('view_sample', views.sample_list, name='view_sample',),
    path('view_sample/sample<int:sample_id>', views.sample_list, name='sample'),


    path('file_sharing/', views.file_sharing, name='file_sharing'),
    path('file_sharing/<int:file_id>', views.delete_file, name='delete_file'),

]