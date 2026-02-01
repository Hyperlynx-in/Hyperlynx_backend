from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    path('framework-library/', views.FrameworkLibraryView.as_view(), name='framework_library'),
]
