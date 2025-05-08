"""
URL configuration for empleados project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
#---------#
from django.contrib.auth import views as auth_views # Para vistas de login/logout
from applications.dashboard.views import dashboard_view # Importar la vista del dashboard


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='home'),
    path('stock/', include('applications.stock.urls', namespace='stock')),
    path('sales/', include('applications.sales.urls', namespace='sales')),
    path('closures/', include('applications.closures.urls', namespace='closures')),
]
