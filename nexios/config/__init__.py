_global_config = None

def set_config(config):
    global _global_config
    _global_config = config

def get_config(): #support for this will soo be droped
    if _global_config is None:
        raise RuntimeError("Configuration has not been initialized.")
    return _global_config


@lambda _:_()
def app_config():
    return get_config()