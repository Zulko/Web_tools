from django.urls import path
from . import views


app_name = 'logbook'

urlpatterns = [

    # LogBook views
    path('', views.logbook_view, name='index'),
    path('book_<int:machine_id>', views.book_view, name='book'),
    path('book_<int:machine_id>', views.book_add, name='book_add'),


]