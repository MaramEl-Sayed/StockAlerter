from django.urls import path
from .views import UpdateStockPriceView, StockListView, StockDetailView

app_name = 'stocks'

urlpatterns = [
    path('stocks/', StockListView.as_view(), name='stock-list'),
    path('stocks/<int:pk>/', StockDetailView.as_view(), name='stock-detail'),
    path('update-price/', UpdateStockPriceView.as_view(), name='update-price'),
]
