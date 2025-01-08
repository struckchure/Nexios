_global_config = None

def set_config(config):
    global _global_config
    _global_config = config

def get_config():
    if _global_config is None:
        raise RuntimeError("Configuration has not been initialized.")
    return _global_config
