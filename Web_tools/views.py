from django.http import HttpRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm, UserCreationForm



# TODO: Automatically remove files from media
# @login_required(login_url="accounts:login")
def home(request):
    return render(request, 'home.html', {'domain': HttpRequest.get_host(request)})


# @login_required(login_url="/accounts/login/")
def about(request):
    return render(request, 'about.html')


def under_construction(request):
    return render(request, 'under_construction.html')


# class LoginRequiredMiddleware(object):
#     def process_view(self, request, view_func, view_args, view_kwargs):
#         if not getattr(view_func, "accounts:login", True):
#             return None
#         return login_required(view_func)(request, *view_args, **view_kwargs)

class PasswordResetView(auth_views.PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')
    # subject_template_name = 'accounts/emails/password-reset-subject.txt'
    email_template_name = 'registration/password_reset_email.html'


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('password_reset_complete')
    form_valid_message = "Your password was changed!"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)