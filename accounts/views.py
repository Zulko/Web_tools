from django.shortcuts import render, redirect

from django.urls import reverse_lazy

from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

from django.views import generic

from accounts.forms import RegistrationForm, EditProfileForm


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

# @login_required
# def signup_view(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('accounts:login')
#     else:
#         # Create a empty form and return the page
#         form = RegistrationForm()
#     return render(request, 'accounts/signup.html', {'form': form})
#
#
# def login_view(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             return redirect('home')
#     else:
#         form = AuthenticationForm()
#     return render(request, 'accounts/../templates/registration/login.html', {'form': form})
#
#
# def logout_view(request):
#     if request.method == "POST":
#         logout(request)
#         return redirect('home')


@login_required
def profile_view(request):
    args = {'user': request.user}
    return render(request, 'accounts/profile.html', args)


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('accounts:profile')
    else:
        form = EditProfileForm(instance=request.user)
        args = {'form':form}
        return render(request, 'accounts/edit_profile.html', args)


@login_required
def password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user=request.user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
    return render(request, 'accounts/change_password.html', args)





