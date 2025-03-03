from django.urls import path
from .views import *

urlpatterns = [
    path('api/json/IBOV/', stocks_json, name='stocks_json'),
    path('api/fluxo/', FluxoJsonView.as_view(), name='fluxo_json'),  # Alterado aqui
    path('api/volatility-analysis/', VolatilityAnalysisView.as_view(), name='volatility_analysis'),
    path('api/top-volatility-stocks/', TopVolatilityStocksView.as_view(), name='top_volatility_stocks'),
    path('api/surface/', SurfaceView.as_view(), name='volatility_surface'),
    path('api/cointegration/', CointegrationView.as_view(), name='cointegration'),
    path('api/cointegration/currency', CurrencyCointegrationView.as_view(), name='cointegration_currency'),
    path('api/rrg/', RRGView.as_view(), name='rrg'),
]
