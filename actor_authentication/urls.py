from django.urls import path, re_path
from actor_authentication import views

app_name = "actor_authentication"

urlpatterns = [
    path('login/', views.login_all, name='login_all'),
    path('logout/', views.logout_all, name='logout'),
    path('signup/', views.signup_all, name='signup_all'),
    path('customer_signup/', views.customer_signup, name='customer_signup'),
    path('vendor_signup/', views.vendor_signup, name='vendor_signup'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate,
            name='activate'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
