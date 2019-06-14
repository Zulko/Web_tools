from . import views
from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

app_name = 'accounts'

urlpatterns = [

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path('profile/password/', views.password_view, name='change_password'),

    path('password-reset/',
         PasswordResetView.as_view(template_name='accounts/password_reset.html',
                                   email_template_name="accounts/password_reset_email.html",
                                   success_url=reverse_lazy('accounts:password_reset_done'),
                                   ), name='reset_password'
         ),

    path('password-reset/done/',
         PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),

    path('password-reset/confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),

    path('password-reset/complete/',
         PasswordResetCompleteView.as_view(), name='password_reset_complete'),




]