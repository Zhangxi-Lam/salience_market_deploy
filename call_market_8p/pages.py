from .models import Constants, Subsession
from ._builtin import Page, WaitPage
from otree.api import Currency


class WelcomePage(Page):
    def is_displayed(self):
        return self.round_number == 1


class Instruction(Page):
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return {
            'state_independent': self.subsession.state_independent,
            'num_states': self.subsession.num_states,
            'num_assets': self.subsession.num_assets
        }


class WaitStart(WaitPage):
    body_text = 'Waiting for all players to be ready'
    wait_for_all_groups = True

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds


class Market(Page):
    timeout_seconds = 100
    form_model = 'player'
    form_fields = ['asset_a_bid','asset_a_ask','asset_b_bid','asset_b_ask']

    @staticmethod
    def error_message(values):
        if values['asset_a_bid'] > values['asset_a_ask']:
            return '对资产A，你的进价必须不高于你的出价。'
        elif values['asset_b_bid'] > values['asset_b_ask']:
            return '对资产B，你的进价必须不高于你的出价。'

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds

    def vars_for_template(self):
        return {
            'round_number': self.round_number,
            'number_of_player': len(self.group.get_players()),
            'p1': self.subsession.p1 * 100,
            'p2': self.subsession.p2 * 100,
            'p3': self.subsession.p3 * 100,
            'asset_a_return_1': self.subsession.x + self.subsession.G,
            'asset_a_return_2': self.subsession.x,
            'asset_a_return_3': self.subsession.x - self.subsession.L,
            'asset_b_return_1': self.subsession.x - self.subsession.G,
            'asset_b_return_2': self.subsession.x,
            'asset_b_return_3': self.subsession.x + self.subsession.L,
            'num_states': self.subsession.num_states,
            'num_assets': self.subsession.num_assets,
            'is_practice': self.subsession.practice,
            'state_independent': self.subsession.state_independent,
            'asseta_endowments': self.subsession.asseta_endowments,
            'assetb_endowments': self.subsession.assetb_endowments,
            'cash_endowments': self.subsession.cash_endowment
        }


class ResultWait(WaitPage):
    body_text = 'Waiting for all players to submit decisions'

    def after_all_players_arrive(self):
        self.group.set_payoffs()

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds


class RoundResults(Page):
    timeout_seconds = 50

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds

    def vars_for_template(self):
        players = self.group.get_players()
        # sort the bids and asks in orders
        total_a_bid = sorted([p.asset_a_bid for p in players], reverse=True)
        total_a_ask = sorted([p.asset_a_ask for p in players])
        total_b_bid = sorted([p.asset_b_bid for p in players], reverse=True)
        total_b_ask = sorted([p.asset_b_ask for p in players])
        return {
            'state_a': self.subsession.state_a,
            'state_b': self.subsession.state_b,
            'asset_a_unit': self.player.final_asseta,
            'asset_a_return': self.subsession.get_asset_return('A'),
            'asset_a_total_return': self.player.final_asseta * self.subsession.get_asset_return('A'),
            'asset_b_unit': self.player.final_assetb,
            'asset_b_return': self.subsession.get_asset_return('B'),
            'asset_b_total_return': self.player.final_assetb * self.subsession.get_asset_return('B'),
            'settled_cash': self.player.final_cash,
            'payoff': self.player.payoff,
            'state_independent': self.subsession.state_independent,
            'num_assets': self.subsession.num_assets,
            'market_a': self.group.market_price_a,
            'market_b': self.group.market_price_b,
            'total_a_bid': total_a_bid,
            'total_a_ask': total_a_ask,
            'total_b_bid': total_b_bid,
            'total_b_ask': total_b_ask
        }


class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds

    def vars_for_template(self):
        r = self.subsession.get_selected_round()
        player = self.player.in_round(r)

        # Calculate the total payoff by summing up the payoffs from both apps
        player.total_payoff = player.payoff/14 + Currency(self.participant.vars['mpl_payoff']*4) + 10

        return {
            'selected_round': r,
            'mpl_payoff': self.participant.vars['mpl_payoff'],
            'salience_payoff': player.payoff,
            'total_payoff': player.total_payoff
        }



class Questionnaire(Page):
    form_model = 'player'
    form_fields = ['question_1', 'question_2', 'question_3', 'question_4',
                   'question_5', 'question_6']

    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds


class Demographic(Page):
    form_model = 'player'
    form_fields = ['name', 'gender', 'phone_id', 'part_id',
                   'venmo_id', 'comments', 'strategy']

    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds


page_sequence = [#WelcomePage,
                 Instruction,
                 WaitStart, Market, ResultWait, RoundResults,
                 Questionnaire, Demographic, FinalResults]
