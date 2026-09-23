"""Create a short-lived self-signed certificate for a private chat session."""

import argparse
import ipaddress
from pathlib import Path
import re
import subprocess


def subject_name(host):
    try:
        return f"IP:{ipaddress.ip_address(host)}"
    except ValueError:
        name = host.encode('idna').decode('ascii')
        if len(name) > 253 or not all(
            re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', label)
            for label in name.split('.')
        ):
            raise ValueError(f"Invalid DNS name: {host!r}")
        return f"DNS:{name}"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', action='append', help='DNS name or IP; repeat for multiple names')
    parser.add_argument('--out', type=Path, default=Path('certs'))
    arguments = parser.parse_args()
    certificate, key = arguments.out / 'server.crt', arguments.out / 'server.key'
    if certificate.exists() or key.exists():
        parser.error('Certificate or key already exists; choose a new --out directory.')
    try:
        names = ','.join(subject_name(host) for host in (arguments.host or ['localhost', '127.0.0.1']))
        arguments.out.mkdir(parents=True, exist_ok=True, mode=0o700)
        subprocess.run([
            'openssl', 'req', '-x509', '-newkey', 'rsa:3072', '-sha256', '-nodes',
            '-keyout', str(key), '-out', str(certificate), '-days', '7',
            '-subj', '/CN=NEON CHAT', '-addext', f'subjectAltName={names}',
            '-addext', 'basicConstraints=critical,CA:TRUE',
            '-addext', 'keyUsage=critical,digitalSignature,keyEncipherment,keyCertSign',
            '-addext', 'extendedKeyUsage=serverAuth',
        ], check=True, capture_output=True, umask=0o077)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Could not create certificate: {error}\n')
    print(f'Created {certificate} and {key} (valid for 7 days).')
    print('Share only server.crt through a trusted channel. Keep server.key private.')


if __name__ == '__main__':
    main()
