import argparse
import configparser
import os

from spr.spr import SPR


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Path to config file")
    args = parser.parse_args()

    if args.config:
        config_file = args.config
    else:
        config_file = os.environ.get("SPR_CONFIG", None)
    if config_file is None:
        config_file = "config.ini"

    config = configparser.ConfigParser()
    config.read(config_file)
    assert "spotify" in config, f"No `spotify` section in {config_file}"
    assert "client_id" in config["spotify"], f"No Spotify client ID in {config_file}"
    assert "client_secret" in config["spotify"], f"No Spotify client secret in {config_file}"

    spr = SPR(config["spotify"]["client_id"], config["spotify"]["client_secret"])


if __name__ == "__main__":
    main()
