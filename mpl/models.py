from otree.api import (
    models,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
)
import random


class Constants(BaseConstants):
    num_choices = 10
    num_rounds = 1
    name_in_url = 'mpl'
    players_per_group = None
    lottery_a_hi = 2.00
    lottery_a_lo = 1.60
    lottery_b_hi = 3.85
    lottery_b_lo = 0.10


class Subsession(BaseSubsession):
    def creating_session(self):
        # if self.round_number == 1:
        n = Constants.num_choices
        for p in self.get_players():
            indices = [j for j in range(1, n + 1)]
            probabilities = [
                str(k) + "/" + str(n)
                for k in indices
            ]
            q = [
                str(n - k) + "/" + str(n)
                for k in indices
            ]
            form_fields = ['choice_' + str(k) for k in indices]
            p.participant.vars['mpl_choices'] = list(
                zip(indices, form_fields, probabilities, q))
            # print(p.participant.vars['mpl_choices'])
            p.participant.vars['mpl_index_to_pay'] = random.choice(indices)
            p.participant.vars['mpl_choice_to_pay'] = 'choice_' + \
                str(p.participant.vars['mpl_index_to_pay'])
            p.participant.vars['mpl_choices_made'] = [
                None for j in range(1, n + 1)]


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # add model fields to class player
    for j in range(1, Constants.num_choices + 1):
        locals()['choice_' + str(j)] = models.StringField()
    del j
    random_draw = models.IntegerField()
    # total_pay = models.CurrencyField()
    choice_to_pay = models.StringField()
    option_to_pay = models.StringField()

    def set_payoffs(self):
        self.random_draw = random.randrange(
            1, len(self.participant.vars['mpl_choices']))
        self.choice_to_pay = self.participant.vars['mpl_choice_to_pay']

        # elicit whether lottery "A" or "B" was chosen for the respective choice
        self.option_to_pay = getattr(self, self.choice_to_pay)

        if self.option_to_pay == 'A':
            if self.random_draw <= self.participant.vars['mpl_index_to_pay']:
                self.payoff = Constants.lottery_a_hi
            else:
                self.payoff = Constants.lottery_a_lo
        else:
            if self.random_draw <= self.participant.vars['mpl_index_to_pay']:
                self.payoff = Constants.lottery_b_hi
            else:
                self.payoff = Constants.lottery_b_lo

        # set payoff as global variable
        self.participant.vars['mpl_payoff'] = self.payoff
