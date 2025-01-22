from nexios import MakeConfig
db_config = {{
    'connections': {{
        'default': "sqlite:///{db_name}"
    }},
    'apps': {{
        'models': {{
            'models': ['app.models', 'aerich.models'],
            'default_connection': 'default',
        }},
    }},
}}


nexios_config = MakeConfig({{
    "port" : 8000,
    "cors":{{
        "allow_origins" : ["*"]
    }},
    "debug" : True 
}})