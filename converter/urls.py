from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('hbb/', views.dashboard, name='dashboard_hbb'),
    path('hbb/converter/', views.index, name='index'),
    path('hbb/convert/', views.convert_exml, name='convert_exml'),
    path('hbb/convert-csv/', views.convert_to_csv, name='convert_to_csv'),
    path('hbb/upload/', views.upload_exml_file, name='upload_exml_file'),
    path('hbb/examples/', views.example_exml, name='example_exml'),
    path('hbb/api/', views.api_documentation, name='api_documentation'),
    path('hbb/get-coordinates/', views.get_customer_coordinates, name='get_customer_coordinates'),
    path('hbb/get-all-customers/', views.get_all_customers, name='get_all_customers'),
    path('hbb/get-customers-with-coords/', views.get_customers_with_coords, name='get_customers_with_coords'),
    path('hbb/check-cells/', views.check_customer_cells, name='check_customer_cells'),
    path('hbb/suggest-nearest-cells/', views.suggest_nearest_cells, name='suggest_nearest_cells'),
    path('hbb/save-customer-cells/', views.save_customer_cells, name='save_customer_cells'),
    path('hbb/registered-cell-distances/', views.registered_cell_distances, name='registered_cell_distances'),
    path('hbb/coordinates/', views.coordinates_page, name='coordinates_page'),
]
