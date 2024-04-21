from os import environ

SESSION_CONFIGS = [
    dict(
        name='salience_market',
        display_name='Salience Market',
        num_demo_participants=8,
        app_sequence=['mpl','salience_market'],
        config_file='demo.csv'
    ),
    dict(
        name='salience_market_2p',
        display_name='Salience Market 2 Players (DUFE)',
        num_demo_participants=2,
        app_sequence=['mpl','salience_market_2p'],
        config_file='demo.csv'
    ),
    dict(
        name='salience_market_8p',
        display_name='Salience Market 8 Players (DUFE)',
        num_demo_participants=8,
        app_sequence=['mpl','salience_market_8p'],
        config_file='demo.csv'
    ),
    dict(
        name='salience_market_bdm',
        display_name='Salience Market with BDM (DUFE)',
        num_demo_participants=8,
        app_sequence=['mpl','salience_market_bdm'],
        config_file='demo.csv'
    ),
    dict(
        name='bdm_market',
        display_name='BDM Market',
        num_demo_participants=1,
        app_sequence=['mpl','bdm_market'],
        config_file='demo.csv'
    ),
    dict(
        name='bdm_single',
        display_name='BDM Single Asset',
        num_demo_participants=1,
        app_sequence=['mpl','bdm_single'],
        config_file='demo.csv'
    ),
    dict(
        name='call_market',
        display_name='Call Market',
        num_demo_participants=8,
        app_sequence=['mpl','call_market'],
        config_file='demo.csv'
    ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'CNY'
USE_POINTS = True

ROOMS = [
    dict(
        name='dufe_iaer',
        display_name='DUFE-IAER Lab Experiment',
        participant_label_file='_rooms/participant_label.txt',
        # use_secure_urls=True
    ),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = 'admin'

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = 'sn#gmlcv%_5kq-3mf&77gex=$mxfl47)43ui13*3tg+p^i0zps'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']

EXTENSION_APPS = ['otree_redwood', 'otree_markets']
