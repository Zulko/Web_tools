from django.urls import path
from . import views


app_name = 'logbook'

urlpatterns = [

    # LogBook views
    path('', views.logbook_view, name='index'),
    path('book_<int:machine_id>', views.book_view, name='book'),
    path('book_<int:machine_id>', views.book_add, name='book_add'),

    # LogBook entry views
    path('book_<int:machine_id>/entry_<int:entry_id>', views.book_entry_view, name='book_entry'),
    path('delete/book_<int:machine_id>/entry_<int:entry_id>', views.book_entry_delete, name='book_entry_delete'),
    path('update/book_<int:machine_id>/entry_<int:entry_id>', views.book_entry_update, name='book_entry_update'),


]