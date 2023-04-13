from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Instructions(Page):
    form_model = 'player'

    def is_displayed(self):
        return self.subsession.round_number == 1

    def vars_for_template(self):
        return {
            'lottery_a_hi': "{:.2f}".format(Constants.lottery_a_hi),
            'lottery_a_lo': "{:.2f}".format(Constants.lottery_a_lo),
            'lottery_b_hi': "{:.2f}".format(Constants.lottery_b_hi),
            'lottery_b_lo': "{:.2f}".format(Constants.lottery_b_lo),
            'num_choices': Constants.num_choices,
        }


class Decision(Page):
    form_model = 'player'

    def get_form_fields(self):
        form_fields = [list(t) for t in zip(
            *self.player.participant.vars['mpl_choices'])][1]
        return form_fields

    def vars_for_template(self):
        print(self.player.participant.vars['mpl_choices'])
        return {
            'lottery_a_hi': "{:.2f}".format(Constants.lottery_a_hi),
            'lottery_a_lo': "{:.2f}".format(Constants.lottery_a_lo),
            'lottery_b_hi': "{:.2f}".format(Constants.lottery_b_hi),
            'lottery_b_lo': "{:.2f}".format(Constants.lottery_b_lo),
            'choices': self.player.participant.vars['mpl_choices']
        }

    def before_next_page(self):
        player = self.player
        # unzip indices and form fields from <mpl_choices> list
        form_fields = [list(t) for t in zip(
            *player.participant.vars['mpl_choices'])][1]

        indices = [list(t)
                   for t in zip(*player.participant.vars['mpl_choices'])][0]
        # if choices are displayed in tabular format
        for j, choice in zip(indices, form_fields):
            choice_i = getattr(player, choice)
            player.participant.vars['mpl_choices_made'][j - 1] = choice_i
        player.set_payoffs()


class Results(Page):
    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds

    def vars_for_template(self):
        player = self.player
        choices = [list(t)
                   for t in zip(*player.participant.vars['mpl_choices'])]
        indices = choices[0]
        # get index, round, and choice to pay
        index_to_pay = player.participant.vars['mpl_index_to_pay']
        round_to_pay = indices.index(index_to_pay) + 1
        choice_to_pay = player.participant.vars['mpl_choices'][round_to_pay - 1]

        return {
            'lottery_a_hi': "{:.2f}".format(Constants.lottery_a_hi),
            'lottery_a_lo': "{:.2f}".format(Constants.lottery_a_lo),
            'lottery_b_hi': "{:.2f}".format(Constants.lottery_b_hi),
            'lottery_b_lo': "{:.2f}".format(Constants.lottery_b_lo),
            'choice_to_pay':  [choice_to_pay],
            'option_to_pay':  player.option_to_pay,
            'payoff':         player.total_pay
        }


page_sequence = [Instructions, Decision, Results]
