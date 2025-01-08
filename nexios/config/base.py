import json

class MakeConfig:
    def __init__(self, config, defaults=None, validate=None, immutable=False):
        """
        Initialize the configuration object.
        
        Args:
            config (dict): The initial configuration dictionary.
            defaults (dict, optional): Default values for missing keys.
            validate (dict, optional): Validation rules for keys. Format: {key: callable}.
            immutable (bool, optional): If True, makes the configuration immutable.
        """
        self._config = {}
        self._immutable = immutable
        self._validate = validate or {}

        # Apply defaults
        if defaults:
            config = {**defaults, **config}

        # Set configuration with validation
        for key, value in config.items():
            self._set_config(key, value)

    def _set_config(self, key, value):
        if key in self._validate:
            if not self._validate[key](value):
                raise ValueError(f"Invalid value for key '{key}': {value}")
        if isinstance(value, dict):
            value = MakeConfig(value, immutable=self._immutable)  # Recursively nest
        self._config[key] = value

    def __setattr__(self, name, value):
        if name in {"_config", "_immutable", "_validate"}:
            super().__setattr__(name, value)
        elif self._immutable:
            raise AttributeError(f"Cannot modify immutable config: {name}")
        else:
            self._set_config(name, value)

    def __getattr__(self, name):
        if name in self._config:
            value = self._config[name]
            if value is None or (isinstance(value, MakeConfig) and value._config == {}):
                return None
            return value
        return None

    def _get_nested(self, path):
        """
        Helper method to get nested values, returning None if any part of the path is None or doesn't exist.
        
        Args:
            path (str or list): Either a dot-separated string or a list of keys to navigate through.

        Returns:
            Any: The value at the end of the path or None if any part is missing or None.
        """
        if isinstance(path, str):
            path = path.split('.')
        
        current = self
        for key in path:
            if not isinstance(current, MakeConfig):
                return None
            current = getattr(current, key, None)
            if current is None:
                return None
        return current

    def __getitem__(self, path):
        return self._get_nested(path)

    def to_dict(self):
        """Export the configuration as a dictionary."""
        def recurse(config):
            if isinstance(config, MakeConfig):
                result = {}
                for k, v in config._config.items():
                    if v is not None:
                        result[k] = recurse(v)
                return result if result else None
            return config

        return recurse(self)

    def to_json(self):
        """Export the configuration as a JSON string."""
        return json.dumps(self.to_dict(), indent=4)

    def __repr__(self):
        return f"Nexios MakeConfig({self.to_dict()})"