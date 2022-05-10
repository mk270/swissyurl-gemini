
# swissyurl-gemini, An implementation of YURLs over Gemini, by Martin Keegan
#
# To the extent (if any) permissible by law, Copyright (C) 2022  Martin Keegan
#
# This programme is free software; you may redistribute and/or modify it under
# the terms of the Apache Software Licence v2.0.

import socket
import cryptography.x509
import ssl
import binascii
import logging

def sha256_fingerprint(cert):
    sha256 = cryptography.hazmat.primitives.hashes.SHA256()
    fingerprint = cert.fingerprint(sha256)
    return binascii.hexlify(fingerprint).lower().decode('UTF-8')

def get_socket_certificate(s):
    der = s.getpeercert(True)
    cert = cryptography.x509.load_der_x509_certificate(der)
    return cert

def make_tofu_ssl_socket(hostname, netloc, port):
    tcpsock = socket.create_connection((hostname, port))
    ctx = ssl.SSLContext()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    sslsock = ctx.wrap_socket(tcpsock, server_hostname=netloc)
    return sslsock

