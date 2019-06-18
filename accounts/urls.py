from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [

    path('login/',
         auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/',
         views.logout_view, name='logout'),
    path('signup/',
         views.signup_view, name='signup'),

    path('profile/',
         views.profile_view, name='profile'),
    path('profile/edit/',
         views.edit_profile, name='edit_profile'),

    path('profile/password/',
         views.password_view, name='change_password'),

    path('password_reset/',
         views.PasswordResetView.as_view(), name='password_reset'),

    path('password_reset_done/',
         views.PasswordResetDoneView.as_view(), name='password_reset_done'),

    path('password_reset_confirm/<uidb64>_<token>/',
         views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    path('password_reset_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),


]