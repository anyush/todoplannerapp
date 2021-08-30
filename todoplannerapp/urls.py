"""todoplannerapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from mainapp import views, forms
from todoplannerapp import settings

urlpatterns = [
    path('', views.homepage, name=''),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html',
                                                         authentication_form=forms.CustomAuthForm),
         name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    path('projects/<int:project_id>/', views.project_page, name='project_page'),
    path('projects/<int:project_id>/about/', views.project_about),
    path('projects/create/', views.project_creation, name='create_project'),
    path('admin/', admin.site.urls),
]
