# Host a temporary NEON / CHAT room on AWS EC2

This guide uses an Ubuntu EC2 instance and a short-lived, self-signed TLS
certificate that friends explicitly trust. You do not need a domain name.
The app has not been deployed to AWS automatically.

## 1. Create the instance and network rules

Launch an Ubuntu instance in a public subnet with a public IPv4 address and an
internet gateway route. Select your SSH key pair. A small instance is a starting
point for this friends-only prototype; capacity has not been load-tested on AWS.

Configure its security group:

| Inbound rule | Source |
| --- | --- |
| TCP 22 (SSH) | Your public IP only (`/32`) |
| TCP 5000 (chat) | Each participant's public IP (`/32`) where practical |

Friends sharing a router usually share a public IP. If their IP changes, update
the rule. Opening TCP 5000 to `0.0.0.0/0` allows everyone to attempt a connection;
TLS and the password are still required. Never open SSH to everyone.
If you enable an OS firewall, allow the same ports there too.

Keep the instance's address stable for the session. After a stop/start, its
public IP may change; regenerate the certificate and redistribute it if so.
An Elastic IP is another option, with its own AWS charges.

## 2. Install the app

Connect using the EC2 console's SSH instructions. On the instance:

```bash
sudo apt update
sudo apt install -y python3 python3-venv git openssl
git clone https://github.com/RyanMyatThu-dev/TCP-Chat.git
cd TCP-Chat
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## 3. Create the server identity

Replace `YOUR_EC2_PUBLIC_IP` with the actual numeric public IP:

```bash
.venv/bin/python tools/generate_certificate.py --host YOUR_EC2_PUBLIC_IP
```

If you use a DNS name, pass that instead (or repeat `--host` to include both).
Clients must connect using a name or IP listed in the certificate.

The helper requires OpenSSL, creates `certs/server.crt` and `certs/server.key`,
and refuses to overwrite either. The certificate expires after seven days.
For another session, choose a new `--out` directory and update the paths below.

Share **only `server.crt`** with friends through a trusted channel. Keep the key
on the server. Friends can compare the certificate fingerprint with you:

```bash
openssl x509 -in certs/server.crt -noout -fingerprint -sha256
```

Accepting an attacker's certificate would let them impersonate the room and
collect its password. Do not disable certificate verification to fix a mismatch.
For longer-term hosting, use a certificate from a public CA matching your domain
and automate renewal; clients can then omit `--ca`.

## 4. Choose the room password and start

For a one-time session, launch in a terminal and enter the password at the hidden
prompt (at least 16 characters; prefer a randomly generated password):

```bash
.venv/bin/python server.py --host 0.0.0.0 --port 5000 \
  --cert certs/server.crt --key certs/server.key
```

The process must stay running. For operation after disconnecting SSH, use the
optional systemd setup below. Share the password privately with invited friends;
anyone with it can join and choose an unused alias.

## 5. Friends connect

Each friend downloads the repository and installs its requirements in a Python
virtual environment. Give them the public address, port, trusted `server.crt`,
and password. On their machine:

```bash
python client.py --host YOUR_EC2_PUBLIC_IP --port 5000 --ca /path/to/server.crt
```

The client prompts for an alias and masks the password. It verifies TLS before
sending credentials. Chat starts only after the server accepts the login.
`/quit` or Ctrl+D leaves the room. Restart the client to reconnect.

## Optional: run as a systemd service

The included `neon-chat.service` assumes the Ubuntu login user is `ubuntu` and
the checkout is `/home/ubuntu/TCP-Chat`. Edit those paths if yours differ.
Stop a manually running server before starting the service on the same port.

Create the password file without putting the password in shell history:

```bash
mkdir -p secrets
chmod 700 secrets
.venv/bin/python - <<'PY'
import getpass
import os
password = getpass.getpass('New room password (16+ characters): ')
if len(password) < 16 or len(password.encode('utf-8')) > 1024:
    raise SystemExit('Use at least 16 characters and at most 1024 UTF-8 bytes.')
fd = os.open('secrets/room-password', os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, 'w') as file:
    file.write(password)
PY
sudo install -m 644 deploy/neon-chat.service /etc/systemd/system/neon-chat.service
sudo systemctl daemon-reload
sudo systemctl start neon-chat
sudo systemctl status neon-chat
```

The password file is plaintext readable by the server user. `secrets/`, `certs/`,
and private key files are ignored by Git. Never commit credentials. The server
also accepts `CHAT_ROOM_PASSWORD` for controlled automation; do not paste real
passwords into shell commands or commit environment files.

The service intentionally is not enabled at boot for a one-time room. Inspect
startup errors with `sudo journalctl -u neon-chat`. The app does not log message
contents or passwords.

## End the session

Stop the server with Ctrl+C, or `sudo systemctl stop neon-chat` for the service.
All clients disconnect. Messages are held only in memory, but participants can
still retain terminal output or screenshots. Change the password before another
session; changing the password file takes effect after restarting the server.

Stop or terminate the EC2 instance when finished, and review remaining storage
and public IP resources to avoid ongoing charges. Termination is destructive;
retain any files you still need before doing it.

## Limits and troubleshooting

- **Certificate error:** match `--host` to a certificate SAN, check its expiry,
  and use the correct public certificate with `--ca`.
- **Timeout / refused connection:** check the process, bind address, public IP,
  security group, and OS firewall.
- **Room access denied:** verify the shared password; login never falls back to
  plaintext.
- **Too many login attempts:** wait one minute. The budget is 10 attempts per
  source IP per minute, including successful attempts, and is shared behind NAT.
- **Alias in use:** choose another alias; uniqueness is case-insensitive while
  connected, and aliases are not permanent identities.
- Limits: 32 connections after the TLS handshake, 4000 UTF-8 bytes per chat
  message, and 20 messages per client per 10 seconds. Slow recipients disconnect
  if their outbound queue fills or a write takes too long.
- These limits are basic abuse controls, not internet-scale denial-of-service
  protection. The pre-authentication TLS handshake still consumes resources.
- TLS encrypts the client/server links; it is **not end-to-end encryption**.
  The server sees messages and the room password during authentication.

## References

- [AWS security group setup](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/creating-security-group.html)
- [AWS inbound rule configuration](https://docs.aws.amazon.com/vpc/latest/userguide/working-with-security-group-rules.html)
- [Python TLS and certificate verification](https://docs.python.org/3/library/ssl.html)
