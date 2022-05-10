
# swissyurl-gemini, An implementation of YURLs over Gemini, by Martin Keegan
#
# To the extent (if any) permissible by law, Copyright (C) 2022  Martin Keegan
#
# This programme is free software; you may redistribute and/or modify it under
# the terms of the Apache Software Licence v2.0.

import logging
import argparse
import cgi
import os
import sys
import urllib.parse
import tofu_ssl
import gemini_url

MAX_RETRIES = 5


class RetriesExceeded(Exception): pass


def get_port(url_parts):
    if url_parts.port is None:
        return 1965
    return url_parts.port

def issue_request(s, url):
    request_text = url + "\r\n"
    request_body = request_text.encode("UTF-8")
    s.sendall(request_body)

def request(url, url_parts, fingerprint):
    retries = MAX_RETRIES
    while retries > 0: # should have a redirect limit
        retries -= 1
        assert url_parts.scheme in ["gemini"]
        port = get_port(url_parts)

        hostname = url_parts.hostname
        netloc = url_parts.netloc
        s = tofu_ssl.make_tofu_ssl_socket(hostname, netloc, port)
        cert = tofu_ssl.get_socket_certificate(s)
        issue_request(s, url)

        stream = s.makefile("rb")
        header = stream.readline().decode("UTF-8").strip()
        status, meta = header.split(maxsplit=1)

        general_status = status[0]
        assert general_status in ["2", "3"], status

        if status.startswith("3"):
            url = gemini_url.gemini_urljoin(url, meta)
            url_parts = urllib.parse.urlparse(url)
            continue

        if fingerprint is not None:
            server_fp = tofu_ssl.sha256_fingerprint(cert)
            assert server_fp == fingerprint

        return status, meta, stream

    raise RetriesExceeded


def checked_request(url, url_parts, fingerprint):
    status, mime, stream = request(url, url_parts, fingerprint)
    return stream.read(), mime


if __name__ == '__main__':
    run()

