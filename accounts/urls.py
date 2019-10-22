from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [

    path('signup/', views.SignUp.as_view(), name='signup'),
    path('profile/', views.profile_view, name='profile'),
    path('news/', views.create_news, name='news'),
    path('viewnews/', views.view_news, name='viewnews'),
    path('news/delete<int:new_id>', views.delete_news, name='delete_news'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/password/', views.password_view, name='change_password'),

]