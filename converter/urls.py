from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('convert/', views.convert_exml, name='convert_exml'),
    path('upload/', views.upload_exml_file, name='upload_exml_file'),
    path('examples/', views.example_exml, name='example_exml'),
    path('api/', views.api_documentation, name='api_documentation'),
]
