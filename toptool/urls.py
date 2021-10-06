from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import path

from protokolle.views import show_public_protokoll

urlpatterns = [
    # admin
    path('admin/', admin.site.urls),

    # login, logout
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),

    # localization
    path('i18n/', include('django.conf.urls.i18n')),

    # apps
    path('profile/', include('userprofile.urls')),
    path('', include('meetingtypes.urls')),
    path('<str:mt_pk>/', include('meetings.urls')),
    path('<str:mt_pk>/', include('tops.urls')),
    path('<str:mt_pk>/', include('protokolle.urls')),
    path('<str:mt_pk>/', include('persons.urls')),

    # public protokoll url (for shibboleth)
    path('protokolle/<str:mt_pk>/<uuid:meeting_pk>/<str:filetype>/', show_public_protokoll, name="protokollpublic"),

    # redirect root
    path('', lambda x: redirect('ownmts', permanent=True)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
