from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'accounts'

urlpatterns = [

    # path('login/',
    #      auth_views.LoginView.as_view(template_name='../templates/registration/login.html'), name='login'),
    # path('logout/',
    #      views.logout_view, name='logout'),

    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),


    path('signup/',
         views.SignUp.as_view(), name='signup'),

    path('profile/',
         views.profile_view, name='profile'),
    path('profile/edit/',
         views.edit_profile, name='edit_profile'),

    path('profile/password/',
         views.password_view, name='change_password'),



]