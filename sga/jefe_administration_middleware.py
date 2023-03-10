import re

from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth import logout


JAFAADMINISTRATION_URLS = [re.compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'JAFAADMINISTRATION_LOGIN_URLS'):
    JAFAADMINISTRATION_URLS += [re.compile(url) for url in settings.JAFAADMINISTRATION_LOGIN_URLS]

class JafaAdministrationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user')
        path = request.path_info.lstrip('/')
        url_is_exempt = any(url.match(path) for url in JAFAADMINISTRATION_URLS)

        if path == reverse('logout').lstrip('/'):
            logout(request)        
        if request.user.is_authenticated() and request.user.role and request.user.role.name in ['Jefe Administracion'] and url_is_exempt:
            return None
        elif (request.user.is_authenticated() and request.user.role and request.user.role.name in ['Jefe Administracion']) and not url_is_exempt:
            return redirect(settings.LOGIN_REDIRECT_URL)
        elif url_is_exempt:
            return None