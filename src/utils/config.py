import yaml

def load_config():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)["production_information"]
    return config