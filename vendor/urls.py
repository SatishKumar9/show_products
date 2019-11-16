from django.urls import path, include
from vendor import views

app_name = 'vendor'

urlpatterns = [
    path('home/', views.list_categories, name='home'),
    # path('home/<int:pk>/', views.itemsview, name='items'),
    path('home/<int:pk>/', views.itemsview, name='items'),
    path('add/', views.add_products_all, name='add_products'),
    path('add_product_existing/', views.add_product_existing, name='add_product_existing'),
    path('add_product_existing/<int:cat_id>/<int:p_id>/', views.add_existing_prod, name='add_existing_prod'),
    path('add_product_new/', views.add_product_new, name='add_product_new'),
    path('view/', views.view_products, name='view_products'),
    path('modify/<int:id>/', views.modify_products, name='modify_products'),
    path('show-orders/', views.view_orders, name='view-orders'),
    path('delete_product/<int:id>', views.delete_product, name='delete_product'),
    path('authentication/', include('actor_authentication.urls')),

]
