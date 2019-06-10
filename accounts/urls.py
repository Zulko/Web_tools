from django.urls import path
from . import views
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit', views.edit_profile, name='edit_profile'),

    path('reset_password/', PasswordResetView.as_view(), name='password_reset'),
    path('reset_password/', PasswordResetDoneView.as_view(), name='password_reset_done'),

    path('change_password/', views.password_view, name='password_change'),

]