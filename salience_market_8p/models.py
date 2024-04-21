import random
from django.forms import IntegerField
from otree.api import (
    models, BaseConstants
)
from otree_markets import models as markets_models
from .configmanager import ConfigManager
import time


class Constants(BaseConstants):
    name_in_url = 'salience_market_8p'
    players_per_group = 8
    # Otree requires this to be set. But it is not used.
    num_rounds = 100
    # Seed for the state random selection.
    random_seed = time.time()

    # list of capital letters A..Z
    asset_names = [chr(i) for i in range(65, 91)]

    # the columns of the config CSV and their types
    # this dict is used by ConfigManager
    config_fields = {
        'round_number': int,
        'period_length': int,
        'num_assets': int,
        'num_states': int,
        'asseta_endowments': str,
        'assetb_endowments': str,
        'cash_endowment': int,
        'practice': bool,
        'x': int,
        'G': int,
        'L': int,
        'p1': float,
        'p2': float,
        'p3': float,
        'state_independent': bool,
        'salient_payoff': bool,
    }


class Subsession(markets_models.Subsession):

    period_length = models.IntegerField()
    num_assets = models.IntegerField()
    num_states = models.IntegerField()
    asseta_endowments = models.StringField()
    assetb_endowments = models.StringField()
    cash_endowment = models.IntegerField()
    practice = models.BooleanField()
    x = models.IntegerField()
    G = models.IntegerField()
    L = models.IntegerField()
    p1 = models.FloatField()
    p2 = models.FloatField()
    p3 = models.FloatField()
    state_independent = models.BooleanField()
    state_a = models.IntegerField()
    state_b = models.IntegerField()
    salient_payoff = models.BooleanField()
    final_selected_round = models.IntegerField(initial=-1)
    num_rounds = models.IntegerField()

    def asset_names(self):
        return Constants.asset_names[:self.num_assets]

    def creating_session(self):
        config_addr = 'salience_market_8p/configs/' + \
            self.session.config['config_file']
        config_manager = ConfigManager(config_addr)
        self.num_rounds = config_manager.num_rounds
        if self.round_number > self.num_rounds:
            return
        #self.group_randomly()
        self.set_properties(config_manager.get_round_dict(
            self.round_number, Constants.config_fields))
        return super().creating_session()

    def set_properties(self, round_dict):
        '''
        Set params for the round using round_dict
        '''
        self.period_length = round_dict['period_length']
        self.num_assets = round_dict['num_assets']
        self.num_states = round_dict['num_states']
        self.asseta_endowments = round_dict['asseta_endowments']
        self.assetb_endowments = round_dict['assetb_endowments']
        self.cash_endowment = round_dict['cash_endowment']
        self.practice = round_dict['practice']
        self.x = round_dict['x']
        self.G = round_dict['G']
        self.L = round_dict['L']
        self.p1 = round_dict['p1']
        self.p2 = round_dict['p2']
        self.p3 = round_dict['p3']
        self.state_independent = round_dict['state_independent']
        self.salient_payoff = round_dict['salient_payoff']

        # Use the current system time as the seed
        random.seed()
        r1 = random.random()
        r2 = random.random() if self.state_independent else r1
        self.state_a = self.get_state(r1)
        self.state_b = self.get_state(r2)

    def get_state(self, r):
        if r < self.p1:
            return 1
        elif r - self.p1 < self.p2:
            return 2
        else:
            return 3

    def get_asset_return(self, asset):
        if asset == 'A':
            if self.state_a == 1:
                return self.x + self.G
            elif self.state_a == 2:
                return self.x
            else:
                return self.x - self.L
        else:
            if self.state_b == 1:
                return self.x - self.G
            elif self.state_b == 2:
                return self.x
            else:
                return self.x + self.L

    def get_selected_round(self):
        '''
        Randomly select one non-practice round to compute the final payoff.
        '''
        if self.final_selected_round >= 0:
            return self.final_selected_round

        valid_rounds = 0
        for subsession in self.in_all_rounds():
            if not subsession.practice:
                valid_rounds += 1

        random.seed(Constants.random_seed)
        if valid_rounds < 1:
            raise ValueError("input CSV doesn't have non-practice round")
        selected_round = random.randint(1, valid_rounds)

        experiment_round_count = 0
        for i, subsession in enumerate(self.in_all_rounds()):
            if not subsession.practice:
                experiment_round_count += 1
            if experiment_round_count == selected_round:
                self.final_selected_round = i + 1
                break
        return self.final_selected_round


class Group(markets_models.Group):
    def period_length(self):
        return self.subsession.period_length

    def _on_enter_event(self, event):
        '''
        Triggered when the user enter an order. Checks if the order is valid.
        '''
        enter_msg = event.value
        if enter_msg['price'] < 0:
            self._send_error(enter_msg['pcode'],
                             'Cannot enter negative bid/ask')
            return
        asset_name = enter_msg['asset_name']

        exchange = self.exchanges.get(asset_name=asset_name)
        if enter_msg['is_bid']:
            best_ask = exchange._get_best_ask()
            if best_ask and best_ask.pcode == enter_msg['pcode'] and enter_msg['price'] >= best_ask.price:
                self._send_error(
                    enter_msg['pcode'], 'Cannot enter a bid that crosses your own ask')
                return
        else:
            best_bid = exchange._get_best_bid()
            if best_bid and best_bid.pcode == enter_msg['pcode'] and enter_msg['price'] <= best_bid.price:
                self._send_error(
                    enter_msg['pcode'], 'Cannot enter an ask that crosses your own bid')
                return
        return super()._on_enter_event(event)


class Player(markets_models.Player):
    question_1 = models.IntegerField(
        label="为购买额外一单位资产A，你最多愿意支付多少钱？")
    question_2 = models.IntegerField(
        label="为出售额外一单位资产A，你最少愿意接受多少钱？")
    question_3 = models.IntegerField(
        label="为购买额外一单位资产B，你最多愿意支付多少钱？")
    question_4 = models.IntegerField(
        label="为出售额外一单位资产A，你最少愿意接受多少钱？")

    name = models.StringField(label='姓名')
    gender = models.StringField(
        choices=[['男', '男'], ['女', '女'], ['其他', '其他']],
        label='性别',
        # widget=widgets.RadioSelect,
    )
    phone_id = models.IntegerField(
        label='手机号', min=0000000, max=9999999)
    part_id = models.StringField(
        label='座位号')
    venmo_id = models.StringField(label='支付宝账号ID')
    comments = models.LongStringField(
        label='实验的哪些部分让你感到困惑？请列举')
    strategy = models.LongStringField(
        label='请简单介绍你在市场资产交易游戏中的交易策略')

    total_payoff = models.CurrencyField()

    def asset_endowment(self):
        asset_names = self.subsession.asset_names()
        pid = self.id_in_group
        endowments_a = [int(e) for e in self.subsession.asseta_endowments.split(' ') if e]
        endowments_b = [int(e) for e in self.subsession.assetb_endowments.split(' ') if e]
        assert Constants.players_per_group == len(
            endowments_a), 'invalid config. number of players and asset length must match'
        if len(asset_names) > 1:
            endowments = [endowments_a[pid-1], endowments_b[pid-1]]
        else:
            endowments = [endowments_a[pid-1]]
        assert len(asset_names) == len(
            endowments), 'invalid config. num_assets and asset_endowments must match'
        return dict(zip(asset_names, endowments))

    def cash_endowment(self):
        return self.subsession.cash_endowment

    def compute_payoff(self):
        if self.subsession.num_assets > 1:
            self.payoff = self.settled_assets['A'] * self.subsession.get_asset_return(
                'A') + self.settled_assets['B'] * self.subsession.get_asset_return('B') + self.settled_cash
        else:
            self.payoff = self.settled_assets['A'] * self.subsession.get_asset_return(
                'A') + self.settled_cash
        return self.payoff
