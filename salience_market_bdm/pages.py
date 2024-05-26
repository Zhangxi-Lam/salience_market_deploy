from salience_market_bdm.models import Constants
from otree_markets.pages import BaseMarketPage
from ._builtin import Page, WaitPage
from otree.api import Currency


class WelcomePage(Page):
    def is_displayed(self):
        return self.round_number == 1


class InstructionBDM(Page):
    def is_displayed(self):
        return self.round_number <= 2 and self.subsession.market_format == 'BDM'

    def vars_for_template(self):
        return {
            'state_independent': self.subsession.state_independent,
        }


class MarketBDM(Page):
    timeout_seconds = 80
    form_model = 'player'
    form_fields = ['asset_a_bid','asset_a_ask','asset_b_bid','asset_b_ask']

    @staticmethod
    def error_message(values):
        if values['asset_a_bid'] > values['asset_a_ask']:
            return '对于资产A，你的进价必须小于你的出价。'
        elif values['asset_b_bid'] > values['asset_b_ask']:
            return '对于资产B，你的进价必须小于你的出价。'

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds and self.subsession.market_format == 'BDM'

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
            'asseta_endowments': self.session.config['bdm_a_endow'],
            'assetb_endowments': self.session.config['bdm_b_endow'],
            'cash_endowments': self.session.config['bdm_cash_endow']
        }


class RoundResultsBDM(Page):
    timeout_seconds = 40

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds and self.subsession.market_format == 'BDM'

    def vars_for_template(self):
        if self.subsession.num_assets > 1:
            return {
                'state_a': self.subsession.state_a,
                'state_b': self.subsession.state_b,
                'asset_a_unit': self.player.get_endowments()[0],
                'asset_a_return': self.subsession.get_asset_return('A'),
                'asset_a_total_return': self.player.get_endowments()[0] * self.subsession.get_asset_return('A'),
                'asset_b_unit': self.player.get_endowments()[1],
                'asset_b_return': self.subsession.get_asset_return('B'),
                'asset_b_total_return': self.player.get_endowments()[1] * self.subsession.get_asset_return('B'),
                'settled_cash': self.player.get_endowments()[2],
                'payoff': self.player.compute_payoff(),
                'state_independent': self.subsession.state_independent,
                'num_assets': self.subsession.num_assets,
                'investor_a': self.subsession.investor_price_a,
                'investor_b': self.subsession.investor_price_b
            }
        else:
            return {
                'state_a': self.subsession.state_a,
                'state_b': self.subsession.state_b,
                'asset_a_unit': self.player.get_endowments()[0],
                'asset_a_return': self.subsession.get_asset_return('A'),
                'asset_a_total_return': self.player.get_endowments()[0] * self.subsession.get_asset_return('A'),
                'settled_cash': self.player.get_endowments()[2],
                'payoff': self.player.compute_payoff(),
                'state_independent': self.subsession.state_independent,
                'num_assets': self.subsession.num_assets,
                'investor_a': self.subsession.investor_price_a,
                'investor_b': self.subsession.investor_price_b
            }


class Instruction(Page):
    def is_displayed(self):
        return self.round_number <= 2 and self.subsession.market_format == 'A2S2'

    def vars_for_template(self):
        return {
            'state_independent': self.subsession.state_independent,
        }


class WaitStart(WaitPage):
    body_text = 'Waiting for all players to be ready'
    wait_for_all_groups = True

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds


class Market(BaseMarketPage):
    def get_timeout_seconds(self):
        return self.group.period_length()

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds and self.subsession.market_format == 'A2S2'

    def salient_highlight(self, asset):
        if not self.subsession.salient_payoff:
            return 0
        x, G, L = self.subsession.x, self.subsession.G, self.subsession.L
        if asset == 'A':
            s1 = abs(x + G - x) / (x + G + x)
            s3 = abs(x - L - x) / (x - L + x)
            return 1 if s1 > s3 else 3
        else:
            s1 = abs(x - G - x) / (x - G + x)
            s3 = abs(x + L - x) / (x + L + x)
            return 1 if s1 > s3 else 3

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
            'asset_a_highlight': self.salient_highlight('A'),
            'asset_b_highlight': self.salient_highlight('B'),
        }


class RoundResults(Page):
    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds and self.subsession.market_format == 'A2S2'

    def get_timeout_seconds(self):
        return 20

    def vars_for_template(self):
        if self.subsession.num_assets > 1:
            return {
                'state_a': self.subsession.state_a,
                'state_b': self.subsession.state_b,
                'asset_a_unit': self.player.settled_assets['A'],
                'asset_a_return': self.subsession.get_asset_return('A'),
                'asset_a_total_return': self.player.settled_assets['A'] * self.subsession.get_asset_return('A'),
                'asset_b_unit': self.player.settled_assets['B'],
                'asset_b_return': self.subsession.get_asset_return('B'),
                'asset_b_total_return': self.player.settled_assets['B'] * self.subsession.get_asset_return('B'),
                'settled_cash': self.player.settled_cash,
                'cash_endowment': self.player.cash_endowment(),
                'payoff': self.player.compute_payoff(),
                'state_independent': self.subsession.state_independent,
                'num_assets': self.subsession.num_assets
            }
        else:
            return {
                'state_a': self.subsession.state_a,
                'state_b': self.subsession.state_b,
                'asset_a_unit': self.player.settled_assets['A'],
                'asset_a_return': self.subsession.get_asset_return('A'),
                'asset_a_total_return': self.player.settled_assets['A'] * self.subsession.get_asset_return('A'),
                'settled_cash': self.player.settled_cash,
                'cash_endowment': self.player.cash_endowment(),
                'payoff': self.player.compute_payoff(),
                'state_independent': self.subsession.state_independent,
                'num_assets': self.subsession.num_assets
            }


class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds

    def vars_for_template(self):
        r = self.subsession.get_selected_round()
        player = self.player.in_round(r)

        # Calculate the total payoff by summing up the payoffs from both apps
        player.total_payoff = player.compute_payoff()/9 + Currency(self.participant.vars['mpl_payoff']*4) + 10

        return {
            'selected_round': r,
            'mpl_payoff': self.participant.vars['mpl_payoff'],
            'salience_payoff': player.compute_payoff(),
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
                 InstructionBDM, Instruction,
                 WaitStart, MarketBDM, RoundResultsBDM,
                 Market, RoundResults,
                 Questionnaire, Demographic, FinalResults]
