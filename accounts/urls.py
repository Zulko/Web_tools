from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [

    path('signup/', views.SignUp.as_view(), name='signup'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/password/', views.password_view, name='change_password'),

]