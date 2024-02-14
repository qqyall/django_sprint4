from django.conf import settings
from django.contrib import admin
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView
from django.urls import include, path, reverse_lazy
from django.views.generic.edit import CreateView

handler404 = 'pages.views.handler_404'
handler404 = 'pages.views.handler_403_csrf_failure'
handler500 = 'pages.views.handler_500'

urlpatterns = [
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
    path(
        'auth/login/',
        LoginView.as_view(
            template_name='registration/login.html',
            form_class=AuthenticationForm,
        ),
        name='login',
    ),
    path('auth/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
