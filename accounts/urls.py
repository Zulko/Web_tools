from . import views
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path('profile/password/', views.password_view, name='change_password'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='../templates/registration/password_reset_form.html',
        email_template_name="../templates/registration/password_reset_email.html",
        success_url=reverse_lazy('accounts:password_reset_done'),
    ), name='password_reset'),

    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='../templates/registration/password_reset_done.html'),
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='../templates/registration/password_reset_confirm.html',
        success_url=reverse_lazy('accounts:password_reset_complete')),
         name='password_reset_confirm'),

    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='../templates/registration/password_reset_complete.html'),
         name='password_reset_complete'),


]