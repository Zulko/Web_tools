from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic

from accounts.forms import EditProfileForm, AddNewsForm
from .models import News


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'


@login_required()
def profile_view(request):
    args = {'user': request.user}
    return render(request, 'accounts/profile.html', args)

@login_required()
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


@login_required()
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


def view_news(request):
    all_news = News.objects.all()

    context = {
        'user': request.user,
        'all_news': all_news,
    }
    return render(request, 'accounts/view_news.html', context)


@login_required()
def create_news(request):
    all_news = News.objects.all()
    formAddNews = AddNewsForm(initial={'author': request.user})
    if request.method == "POST":
        formAddNews = AddNewsForm(request.POST, initial={'author': request.user})
        if formAddNews.is_valid():
            user = formAddNews.save()
            return redirect('home')

    context = {
        'user': request.user,
        'form': formAddNews,
        'all_news': all_news,
    }
    return render(request, 'accounts/news.html', context)


@login_required()
def delete_news(request, new_id):
    if request.method == "POST":
        new = get_object_or_404(News, id=new_id)
        new.delete()
    return redirect('accounts:news')