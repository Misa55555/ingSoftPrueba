# applications/closures/urls.py
from django.urls import path
from . import views

app_name = 'closures'

urlpatterns = [
    path('', views.perform_closure_view, name='perform_closure'),
    # --- NUEVAS URLs ---
    path('history/', views.closure_history_view, name='closure_history'),
    path('detail/<int:closure_id>/', views.closure_detail_view, name='closure_detail'),
]