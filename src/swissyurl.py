#!/usr/bin/env python3

# swissyurl-gemini, An implementation of YURLs over Gemini, by Martin Keegan
#
# To the extent (if any) permissible by law, Copyright (C) 2022  Martin Keegan
#
# This programme is free software; you may redistribute and/or modify it under
# the terms of the Apache Software Licence v2.0.

import logging
import argparse
import urllib.parse
import gemini

def validate_swiss(url_parts):
    pu = url_parts
    assert pu.scheme == "swissyurl+gemini"
    assert "!" in pu.path
    assert ":" in pu.netloc
    assert "@" in pu.netloc

    algo_fingerprint, host_port = pu.netloc.split("@")
    logging.info(host_port)

    algo, fingerprint = algo_fingerprint.split(":")
    assert algo == "sha256"
    return host_port, fingerprint.lower()

def change_part(url, part_idx, new_value):
    parts = list(urllib.parse.urlsplit(url))
    parts[part_idx] = new_value
    return urllib.parse.urlunsplit(tuple(parts))

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', required=False,
                    help='set logging level to INFO')
    parser.add_argument('url')

    args = parser.parse_args()
    if args.debug:
        logging.getLogger().setLevel(20)

    url_parts = urllib.parse.urlparse(args.url)
    logging.info(url_parts)
    host_port, fingerprint = validate_swiss(url_parts)

    effective_url = change_part(args.url, 0, "gemini")
    effective_url = change_part(effective_url, 1, host_port)
    parsed_effective_url = urllib.parse.urlparse(effective_url)

    body, mime = gemini.checked_request(
        effective_url, parsed_effective_url, fingerprint)
    # logging.info(mime)
    print(body, end="")

if __name__ == '__main__':
    run()
