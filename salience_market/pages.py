from salience_market.models import Constants
from otree_markets.pages import BaseMarketPage
from ._builtin import Page, WaitPage


class WelcomePage(Page):
    def is_displayed(self):
        return self.round_number == 1


class Instruction(Page):
    def is_displayed(self):
        return self.round_number == 1


class WaitStart(WaitPage):
    body_text = 'Waiting for all players to be ready'
    wait_for_all_groups = True

    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds


class Market(BaseMarketPage):
    def get_timeout_seconds(self):
        return self.group.period_length()

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
            'is_practice': self.subsession.practice
        }


class RoundResults(Page):
    def is_displayed(self):
        return self.round_number <= self.subsession.num_rounds

    def get_timeout_seconds(self):
        return 20

    def vars_for_template(self):
        return {
            'state': self.subsession.state,
            'asset_a_unit': self.player.settled_assets['A'],
            'asset_a_return': self.subsession.get_asset_return('A'),
            'asset_a_total_return': self.player.settled_assets['A'] * self.subsession.get_asset_return('A'),
            'asset_b_unit': self.player.settled_assets['B'],
            'asset_b_return': self.subsession.get_asset_return('B'),
            'asset_b_total_return': self.player.settled_assets['B'] * self.subsession.get_asset_return('B'),
            'settled_cash': self.player.settled_cash,
            'payoff': self.player.compute_payoff()
        }


class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == self.subsession.num_rounds

    def vars_for_template(self):
        r = self.subsession.get_selected_round()
        player = self.player.in_round(r)
        return {
            'selected_round': r,
            'payoff': player.compute_payoff()
        }


page_sequence = [WelcomePage, Instruction,
                 WaitStart, Market, RoundResults, FinalResults]
