# core/views.py
from django.shortcuts import render


def handler_404(request, exception):
    return render(request, 'pages/404.html', status=404)


def handler_403_csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def handler_500(request, reason=''):
    return render(request, 'pages/500.html', status=500)
