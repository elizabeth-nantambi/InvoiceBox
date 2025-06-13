from django.urls import path
from .views import (
    CustomLoginView, CustomLogoutView,
    provider_dashboard, purchaser_dashboard,
    CreateInvoiceView, InvoiceDetailView, MakePaymentView, CreateUserView, profile_view, home_view, provider_analytics, purchaser_analytics
)

urlpatterns = [
    path('', home_view, name='home'),  # Redirect to provider dashboard as home
    
    path('register/', CreateUserView.as_view(), name= 'register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', profile_view, name='profile_view'),
    path('provider/analytics/', provider_analytics, name='provider_analytics'),
    path('purchaser/analytics/', purchaser_analytics, name='purchaser_analytics'),
    path('provider/dashboard/', provider_dashboard, name='provider_dashboard'),
    path('purchaser/dashboard/', purchaser_dashboard, name='purchaser_dashboard'),
    path('invoice/create/', CreateInvoiceView.as_view(), name='create_invoice'),
    path('invoice/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoice/<int:pk>/pay/', MakePaymentView.as_view(), name='make_payment'),
]