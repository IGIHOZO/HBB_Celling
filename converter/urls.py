from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('converter/', views.index, name='index'),
    path('convert/', views.convert_exml, name='convert_exml'),
    path('convert-csv/', views.convert_to_csv, name='convert_to_csv'),
    path('upload/', views.upload_exml_file, name='upload_exml_file'),
    path('examples/', views.example_exml, name='example_exml'),
    path('api/', views.api_documentation, name='api_documentation'),
    path('get-coordinates/', views.get_customer_coordinates, name='get_customer_coordinates'),
    path('get-all-customers/', views.get_all_customers, name='get_all_customers'),
    path('get-customers-with-coords/', views.get_customers_with_coords, name='get_customers_with_coords'),
    path('check-cells/', views.check_customer_cells, name='check_customer_cells'),
    path('suggest-nearest-cells/', views.suggest_nearest_cells, name='suggest_nearest_cells'),
    path('save-customer-cells/', views.save_customer_cells, name='save_customer_cells'),
    path('coordinates/', views.coordinates_page, name='coordinates_page'),
]
