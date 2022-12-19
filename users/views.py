from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .forms import LoginForm, UserProfileForm
from .models import UserProfile


def login_view(request):
    context = {}
    
    if request.user and request.user.is_authenticated():
        return HttpResponseRedirect(reverse('main-dashboard'))
    else:
        if request.method == 'POST':
            form = LoginForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                username = data.get('username')
                password = data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect(reverse('main-dashboard'))
                else:
                    context.update({
                        'message': 'failed login'
                    })
            else:
                context.update({
                    'errors': form.errors
                })

    return render(request, template_name='auth/login.html', context=context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


class UserList(LoginRequiredMixin, ListView):
    template_name = 'auth/list.html'
    model = UserProfile


class UserCreate(LoginRequiredMixin, CreateView):
    template_name = 'auth/create.html'
    model = UserProfile
    form_class = UserProfileForm


class UserDetail(LoginRequiredMixin, UpdateView):
    template_name = 'auth/detail.html'
    model = UserProfile
    form_class = UserProfileForm


class UserDelete(LoginRequiredMixin, DeleteView):
    model = UserProfile

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('user-list')

def menuover_login_validation(request):
   username= request.POST.get('username', "")
   password = request.POST.get('password', "")   
   user = authenticate(username=username, password=password)
   if user is not None:
       if user.is_active and (user.role.name == "Jefe Almacen" or user.role.name == "Responsable de Turno Almacen" or user.role.name == "Sistemas"):
           return HttpResponse('fine')
       else:
           return HttpResponse('inactive')
   else:
       return HttpResponse('bad')