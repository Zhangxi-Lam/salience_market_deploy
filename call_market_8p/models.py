import random
from otree.api import (
    models, BaseConstants, BaseGroup, widgets, BaseSubsession, BaseGroup, BasePlayer
)
from otree.models import subsession
from .configmanager import ConfigManager
import csv
import time
import statistics


class Constants(BaseConstants):
    name_in_url = 'call_market_8p'
    players_per_group = 8
    num_rounds = 50
    random_seed = time.time()

    # list of capital letters A..Z
    asset_names = [chr(i) for i in range(65, 91)]

    # import config files
    # the columns of the config CSV and their types
    # this dict is used by ConfigManager
    config_fields = {
        'round_number': int,
        'num_assets': int,
        'num_states': int,
        'asseta_endowments': int,
        'assetb_endowments': int,
        'cash_endowment': int,
        'practice': bool,
        'x': int,
        'G': int,
        'L': int,
        'p1': float,
        'p2': float,
        'p3': float,
        'state_independent': bool,
    }


class Subsession(BaseSubsession):

    num_assets = models.IntegerField()
    num_states = models.IntegerField()
    asseta_endowments = models.IntegerField()
    assetb_endowments = models.IntegerField()
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
        config_addr = 'call_market_8p/configs/' + \
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


class Group(BaseGroup):

    market_price_a = models.FloatField()
    market_price_b = models.FloatField()
    market_size_a = models.IntegerField()
    market_size_b = models.IntegerField()

    def get_market_info(self):
        players = self.get_players()
        # the market price is the median of all the bids and asks
        total_price_a = [p.asset_a_bid for p in players] + [p.asset_a_ask for p in players]
        self.market_price_a = statistics.median(total_price_a)
        total_price_b = [p.asset_b_bid for p in players] + [p.asset_b_ask for p in players]
        self.market_price_b = statistics.median(total_price_b)
        # calculate the market demand and supply based on the market price
        demand_a = len([p.asset_a_bid for p in players if p.asset_a_bid >= self.market_price_a])
        supply_a = len([p.asset_a_ask for p in players if p.asset_a_ask <= self.market_price_a])
        self.market_size_a = min(demand_a, supply_a)
        demand_b = len([p.asset_b_bid for p in players if p.asset_b_bid >= self.market_price_b])
        supply_b = len([p.asset_b_ask for p in players if p.asset_b_ask <= self.market_price_b])
        self.market_size_b = min(demand_b, supply_b)

    def set_payoffs(self):
        # get all players object
        players = self.get_players()
        num = Constants.players_per_group
        # get the market price, demand and supply
        self.get_market_info()
        a_demand = self.market_size_a
        a_supply = self.market_size_a
        b_demand = self.market_size_b
        b_supply = self.market_size_b
        ra = self.market_price_a
        rb = self.market_price_b
        # initialize the endowment for all players
        for p in players:
            p.final_asseta = self.subsession.asseta_endowments
            p.final_assetb = self.subsession.assetb_endowments
            p.final_cash = self.subsession.cash_endowment
        # update the assets and cash endowments for each player without considering the equal case
        for p in players:
            if ra < p.asset_a_bid:
                a_supply -= 1
                p.final_asseta += 1
                p.final_cash -= ra
            if ra > p.asset_a_ask:
                a_demand -= 1
                p.final_asseta -= 1
                p.final_cash += ra
            if rb < p.asset_b_bid:
                b_supply -= 1
                p.final_assetb += 1
                p.final_cash -= rb
            if rb > p.asset_b_ask:
                b_demand -= 1
                p.final_assetb -= 1
                p.final_cash += rb
        # randomize the player list, update the assets and cash endowments for each player considering bid=p or ask=p
        # for asset A
        random.shuffle(players)
        for p in players:
            if ra == p.asset_a_bid and a_supply > 0:
                a_supply -= 1
                p.final_asseta += 1
                p.final_cash -= ra
            if ra == p.asset_a_ask and a_demand > 0:
                a_demand -= 1
                p.final_asseta -= 1
                p.final_cash += ra
        # randomize the player list, update the assets and cash endowments for each player considering bid=p or ask=p
        # for asset B
        random.shuffle(players)
        for p in players:
            if rb == p.asset_b_bid and b_supply > 0:
                b_supply -= 1
                p.final_assetb += 1
                p.final_cash -= rb
            if rb == p.asset_b_ask and b_demand > 0:
                b_demand -= 1
                p.final_assetb -= 1
                p.final_cash += rb
        # calculate the player payoff and update the asset holding
        for p in players:
            p.payoff = p.final_asseta * self.subsession.get_asset_return('A') + p.final_assetb * self.subsession.get_asset_return('B') + p.final_cash
            #player.final_asseta = endows[p-1][0]
            #player.final_assetb = endows[p-1][1]
            #player.final_cash = endows[p-1][2]


class Player(BasePlayer):

    question_1 = models.IntegerField(
        label="为购买额外一单位资产A，你最多愿意支付多少钱？")
    question_2 = models.IntegerField(
        label="为出售额外一单位资产A，你最少愿意接受多少钱？")
    question_3 = models.IntegerField(
        label="为购买额外一单位资产B，你最多愿意支付多少钱？")
    question_4 = models.IntegerField(
        label="为出售额外一单位资产B，你最少愿意接受多少钱？")
    question_5 = models.IntegerField(
        choices=[1, 2, 3, 4, 5, 6, 7],
        label="你认为资产A的投资风险有多大？（7为极大风险，1为无风险）",
        #widget=widgets.RadioSelectHorizontal
    )
    question_6 = models.IntegerField(
        choices=[1, 2, 3, 4, 5, 6, 7],
        label="你认为资产B的投资风险有多大？（7为极大风险，1为无风险）",
        #widget=widgets.RadioSelectHorizontal
    )

    name = models.StringField(label='姓名')
    gender = models.StringField(
        choices=[['Male', '男'], ['Female', '女'], ['Other', '其他']],
        label='性别',
        #widget=widgets.RadioSelectHorizontal
    )
    phone_id = models.StringField(
        label='手机号')
    part_id = models.StringField(
        label='座位号')
    venmo_id = models.StringField(label='支付宝账号ID')
    comments = models.LongStringField(
        label='实验的哪些部分让你感到困惑？请列举')
    strategy = models.LongStringField(
        label='请简单介绍你在市场资产交易游戏中的交易策略')

    # bid and ask fields
    asset_a_bid = models.FloatField(label='你对资产A的进价是多少？')
    asset_a_ask = models.FloatField(label='你对资产A的出价是多少？')
    asset_b_bid = models.FloatField(label='你对资产B的进价是多少？')
    asset_b_ask = models.FloatField(label='你对资产B的出价是多少？')

    final_asseta = models.IntegerField()
    final_assetb = models.IntegerField()
    final_cash = models.FloatField()

    total_payoff = models.CurrencyField()

    def asset_a_bid_max(self):
        return self.subsession.x + self.subsession.G

    def asset_a_bid_min(self):
        return self.subsession.x - self.subsession.L

    def asset_a_ask_max(self):
        return self.subsession.x + self.subsession.G

    def asset_a_ask_min(self):
        return self.subsession.x - self.subsession.L

    def asset_b_bid_max(self):
        return self.subsession.x + self.subsession.L

    def asset_b_bid_min(self):
        return self.subsession.x - self.subsession.G

    def asset_b_ask_max(self):
        return self.subsession.x + self.subsession.L

    def asset_b_ask_min(self):
        return self.subsession.x - self.subsession.G

    def asset_number(self):
        return self.subsession.num_assets

    # payment
    # def get_endowments(self):
    #     endows = [self.subsession.asseta_endowments, self.subsession.assetb_endowments, self.subsession.cash_endowment]
    #     ra = self.group.market_price_a
    #     if ra <= self.asset_a_bid:
    #         endows[0] = endows[0] + 1
    #         endows[2] = endows[2] - ra
    #     elif ra >= self.asset_a_ask:
    #         endows[0] = endows[0] - 1
    #         endows[2] = endows[2] + ra
    #     if self.subsession.num_assets > 1:
    #         rb = self.group.market_price_b
    #         if rb <= self.asset_b_bid:
    #             endows[1] = endows[1] + 1
    #             endows[2] = endows[2] - rb
    #         elif rb >= self.asset_b_ask:
    #             endows[1] = endows[1] - 1
    #             endows[2] = endows[2] + rb
    #     return endows
    #
    # def compute_payoff(self):
    #     endows = self.get_endowments()
    #     if self.subsession.num_assets > 1:
    #         self.payoff = endows[0] * self.subsession.get_asset_return('A') + endows[1] * self.subsession.get_asset_return('B') + endows[2]
    #     else:
    #         self.payoff = endows[0] * self.subsession.get_asset_return('A') + endows[2]
    #     return self.payoff

    # page parameter
