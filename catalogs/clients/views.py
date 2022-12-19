from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from .models import Client
from .forms import ClientForm, ClientUpdateForm,ResetPasswordForm
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages



class ClientList(LoginRequiredMixin, ListView):
    template_name = 'catalogs/client/list.html'
    model = Client


class ClientCreate(LoginRequiredMixin, CreateView):
    template_name = 'catalogs/client/create.html'
    model = Client
    form_class = ClientForm


class ClientDetail(LoginRequiredMixin, UpdateView):
    template_name = 'catalogs/client/detail.html'
    model = Client
    form_class = ClientUpdateForm


class ClientDelete(LoginRequiredMixin, DeleteView):
    model = Client

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('client-list')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.user,request.POST)
        if form.is_valid():
            request.user.set_password(request.POST['password'])
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.add_message(request, messages.INFO, 'Contrasena actualizada exitosamente')

            return HttpResponseRedirect(reverse('main-dashboard'))
    else:
        form = ResetPasswordForm(request.user,request.POST)
    return render(request, 'catalogs/client/change-password.html', {'form': form})