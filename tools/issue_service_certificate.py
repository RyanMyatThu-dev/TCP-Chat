"""Renew a service certificate while preserving the clients' trusted authority."""
import argparse
import os
from pathlib import Path
import secrets
import subprocess
import tempfile

from generate_certificate import subject_name


def openssl(*args):
    subprocess.run(['openssl', *map(str, args)], check=True, capture_output=True, umask=0o077)


def issue(host, authority, output):
    name = subject_name(host)
    authority.mkdir(parents=True, exist_ok=True, mode=0o700)
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    ca, ca_key = authority / 'ca.crt', authority / 'ca.key'
    if ca.exists() != ca_key.exists():
        raise ValueError('Incomplete authority. Restore its original files; do not silently replace client trust.')
    if not ca.exists():
        with tempfile.TemporaryDirectory(dir=authority) as directory:
            temporary = Path(directory)
            openssl('req', '-x509', '-newkey', 'rsa:3072', '-sha256', '-nodes',
                    '-keyout', temporary / 'ca.key', '-out', temporary / 'ca.crt',
                    '-days', '3650', '-subj', '/CN=NEON CHAT SERVICE AUTHORITY',
                    '-addext', 'basicConstraints=critical,CA:TRUE,pathlen:0',
                    '-addext', 'keyUsage=critical,keyCertSign,cRLSign')
            os.replace(temporary / 'ca.key', ca_key)
            os.replace(temporary / 'ca.crt', ca)
    with tempfile.TemporaryDirectory(dir=output) as directory:
        temporary = Path(directory)
        openssl('req', '-new', '-newkey', 'rsa:3072', '-nodes', '-sha256',
                '-keyout', temporary / 'server.key', '-out', temporary / 'server.csr',
                '-subj', '/CN=NEON CHAT')
        extensions = temporary / 'extensions.cnf'
        extensions.write_text('\n'.join([
            'basicConstraints=critical,CA:FALSE',
            'keyUsage=critical,digitalSignature,keyEncipherment',
            'extendedKeyUsage=serverAuth', f'subjectAltName={name}',
            'subjectKeyIdentifier=hash', 'authorityKeyIdentifier=keyid,issuer',
        ]))
        openssl('x509', '-req', '-in', temporary / 'server.csr', '-CA', ca,
                '-CAkey', ca_key, '-set_serial', '0x' + secrets.token_hex(16),
                '-days', '7', '-sha256', '-extfile', extensions,
                '-out', temporary / 'server.crt')
        openssl('verify', '-CAfile', ca, temporary / 'server.crt')
        os.replace(temporary / 'server.key', output / 'server.key')
        os.replace(temporary / 'server.crt', output / 'server.crt')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True)
    parser.add_argument('--authority', type=Path, default=Path('secrets/authority'))
    parser.add_argument('--out', type=Path, default=Path('certs/service'))
    arguments = parser.parse_args()
    try:
        issue(arguments.host, arguments.authority, arguments.out)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Certificate issuance failed: {error}\n')
    print('Service certificate renewed; authority preserved.')


if __name__ == '__main__':
    main()
