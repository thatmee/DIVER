import json

class ConfigManageMixin:
    def add_config_names(self, config_names:list):
        if not hasattr(self, 'config_names'):
            self.config_names = config_names
        else:
            self.config_names += config_names
            self.config_names = list(set(self.config_names))

    
    def load_config(self, config_file):
        self.config_file = config_file
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

        for name in self.config_names:
            setattr(self, name, self.config.get(name))
            

    def save_config(self):
        if not hasattr(self, 'config_names'):
            raise AttributeError("Please add config names to save.")
        if not hasattr(self, 'config_file'):
            raise AttributeError("No config file to save, please set config file first.")
        
        for config_name in self.config_names:
            self.config[config_name] = getattr(self, config_name)

        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    