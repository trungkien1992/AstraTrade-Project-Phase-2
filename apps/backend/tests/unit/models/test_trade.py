import sys
sys.path.append("/Users/admin/AstraTrade-Project")
from apps.backend.models.trade import Trade
from datetime import datetime

class TestTradeModel:
    def test_trade_profit_calculation(self):
        trade = Trade(
            entry_price=100,
            exit_price=150,
            amount=10
        )
        assert trade.profit == 500  # (150-100)*10
        assert trade.profit_percentage == 50.0