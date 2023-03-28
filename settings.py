from os import environ

SESSION_CONFIGS = [
    dict(
        name='salience_market',
        display_name='Salience Market',
        num_demo_participants=4,
        app_sequence=['mpl','salience_market'],
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
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ROOMS = [
    dict(
        name='session_room',
        display_name='Session Room',
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
