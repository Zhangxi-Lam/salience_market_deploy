from otree_markets.output import DefaultJSONMarketOutputGenerator


class SalienceMarketJSONMarketOutputGenerator(DefaultJSONMarketOutputGenerator):
    """
    Class to output the market data in JSON.
    """

    def trade_to_output_dict(self, trade, start_time):
        '''
        Returns the data of a trade (transaction)
        '''
        return {
            'timestamp': (trade.timestamp - start_time).total_seconds(),
            'taking_order_id': trade.taking_order.id,
            'making_order_id': trade.making_orders.first().id,
            'price': trade.making_orders.first().price,
            'volume': trade.making_orders.first().volume
        }

    def get_group_data(self, group):
        '''
        Returns all transactions of the group.
        '''
        start_time = group.get_start_time()

        exchange_data = []
        exchange_query = group.exchanges.all().prefetch_related('orders', 'trades')
        for exchange in exchange_query:
            orders = [self.order_to_output_dict(
                e, start_time) for e in exchange.orders.all()]
            trades = [self.trade_to_output_dict(
                e, start_time) for e in exchange.trades.all()]
            exchange_data.append({
                'asset_name': exchange.asset_name,
                'orders': orders,
                'trades': trades,
            })
        if not exchange_data:
            return None
        return {
            'session_code': self.session.code,
            'round_number': group.round_number,
            'id_in_subsession': group.id_in_subsession,
            'exchange_data': exchange_data,
        }


output_generators = [
    SalienceMarketJSONMarketOutputGenerator]
