from django.http import HttpRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# TODO: Automatically remove files from media
# @login_required(login_url="accounts:login")
def home(request):
    return render(request, 'home.html', {'domain': HttpRequest.get_host(request)})


# @login_required(login_url="/accounts/login/")
def about(request):
    return render(request, 'about.html')


def under_construction(request):
    return render(request, 'under_construction.html')


class LoginRequiredMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if not getattr(view_func, "accounts:login", True):
            return None
        return login_required(view_func)(request, *view_args, **view_kwargs)