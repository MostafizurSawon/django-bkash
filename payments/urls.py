from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('ping/', views.ping, name='ping'),
    path('shop/', views.shop, name='shop'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/clear/', views.clear_cart, name='cart_clear'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('tester/', views.tester, name='tester'),

    path('checkout/', views.checkout, name='checkout'),
    path('callback/', views.callback, name='callback'),
]
