from django.contrib import admin
from django.urls import path
from .import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.IndexView.as_view(),name='index'),
    path('product/<int:id>/', views.ProductDetailView.as_view(),name='detail'),
    path('success/',views.PaymentSuccessView.as_view(),name='success'),
    path('failed/',views.PaymentFailedView.as_view(),name='failed'),
    path('api/checkout-session/<int:id>/',views.CheckoutSessionView.as_view(),name='api_checkout_session'),
    path('createproduct/',views.CreateProductView.as_view(),name='createproduct'),
    path('editproduct/<int:id>/',views.ProductEditView.as_view(),name='editproduct'),
    path('delete/<int:id>/', views.ProductDeleteView.as_view(),name='delete'),
    path('dashboard',views.DashboardView.as_view(),name='dashboard'),
    path('register/',views.RegisterView.as_view(),name='register'),
    path('login/',auth_views.LoginView.as_view(template_name='myapp/login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='myapp/logout.html'),name='logout'), 
    path('invalid/',views.InvalidView.as_view(),name='invalid'),
    path('purchases/',views.MyPurchasesView.as_view(),name='purchases'),
    path('sales/',views.SalesView.as_view(),name='sales'),
]