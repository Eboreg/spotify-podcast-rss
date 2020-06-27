#!/usr/bin/env python3

import argparse

from spr import SPR, Config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("show_id", help="Spotify ID of a podcast")
    parser.add_argument("-c", "--config", help="Path to config file")
    args = parser.parse_args()

    config = Config.load(args.config)

    spr = SPR(**config.__dict__)

    print(spr.get_rss_by_show_id(args.show_id).decode())


if __name__ == "__main__":
    main()
