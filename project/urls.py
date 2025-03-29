from django.contrib import admin
from django.conf.urls.static import static 
from django.conf import settings
from django.urls import path,include
from . import views  # Import your views module
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('send_money/', views.send_moneyss, name='send_moneyss'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path("split_bill/", views.split_bill, name="split_bill"),
    path("topup/",views.topup,name="topup"),
    path("transaction/",views.transaction,name="transaction"),
    path("profile/",views.profile,name="profile"),
    path('scan_qr/', views.scan_qr_code, name='scan_qr'),
    path('qr_page/', views.scan_qr_page, name='qr_page'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('transaction_history/', views.transaction_history, name='transaction_history'),


    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
