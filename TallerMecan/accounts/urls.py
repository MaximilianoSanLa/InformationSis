from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('inventario/', views.inventario_view, name='inventario'),
    path('manejar-inventario/', views.manejar_inventario_view, name='manejar_inventario'),
    path('delete-item/<int:item_id>/', views.delete_item, name='delete_item'),
    path('delete-stock/<int:stock_id>/', views.delete_stock, name='delete_stock'),
    path("warranties/", views.warranty_view, name="garantias"), 
    path("reports/", views.earnings_and_reports_view, name="earnings_reports"),
    path("factura/", views.generar_factura_view, name="generar_factura"),
]
