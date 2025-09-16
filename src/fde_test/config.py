import configparser
from dotenv import load_dotenv

load_dotenv()

def read_config():
    config = configparser.ConfigParser()
    config.read("src/fde_test/config.ini")

    config_values = {
        "db_source": config.get("Database", "db_source"),
        "db_uri": config.get("Database", "db_uri"),
        "city": config.get("QueryParams", "city"),
        "date_time": config.get("QueryParams", "date_time"),
        "api_base_url": config.get("API", "base_url"),
        "api_retries": int(config.get("API", "retries")),
        "output_dir": config.get("Output", "output_dir"),
        "output_file": config.get("Output", "output_file")
    }
    return config_values