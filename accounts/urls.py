from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import PasswordResetView

from . import views

app_name = 'accounts'

urlpatterns = [

    # path('login/',
    #      auth_views.LoginView.as_view(template_name='../templates/registration/login.html'), name='login'),
    # path('logout/',
    #      views.logout_view, name='logout'),
    path('signup/',
         views.SignUp.as_view(), name='signup'),

    path('profile/',
         views.profile_view, name='profile'),
    path('profile/edit/',
         views.edit_profile, name='edit_profile'),

    path('profile/password/',
         views.password_view, name='change_password'),
    #
    # path('password_reset/',
    #      views.PasswordResetView.as_view(), name='password_reset'),
    #
    # path('password_reset_done/',
    #      views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    #
    # path('reset/<uidb64>/<token>/',
    #      views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    #
    # path('reset/done/',
    #      auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


]