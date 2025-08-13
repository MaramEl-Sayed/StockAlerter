from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Stock
from .services import fetch_stock_price, validate_stock_symbol, update_single_stock_price
from .serializers import StockSerializer


class StockListView(ListAPIView):
    """View for listing all stocks"""
    queryset = Stock.objects.filter(is_active=True).order_by('symbol')
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]

class StockDetailView(RetrieveAPIView):
    """View for retrieving specific stock details"""
    queryset = Stock.objects.filter(is_active=True)
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

class UpdateStockPriceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        symbol = request.data.get("symbol")

        if not symbol:
            return Response({"error": "Symbol is required"}, status=400)

        # Validate symbol format
        is_valid, message = validate_stock_symbol(symbol)
        if not is_valid:
            return Response({"error": message}, status=400)

        try:
            # Use the update function that handles the database update
            result = update_single_stock_price(symbol)
            if result and not result.startswith("Error:"):
                return Response({
                    "message": f"Price updated successfully for {symbol}",
                    "status": "success"
                }, status=200)
            else:
                return Response({
                    "error": result or f"Failed to update price for {symbol}"
                }, status=500)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
