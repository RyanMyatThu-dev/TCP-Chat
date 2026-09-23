# Operate the NEON CHAT service

Friends only need the install, host, and join commands in the [README](../README.md).
This guide is for the AWS operator. The service uses Singapore (`ap-southeast-1`),
one Ubuntu ARM64 `t4g.small`, encrypted 8 GiB gp3, a stable Elastic IP, and public
TLS on TCP 5000. SSH remains restricted to the administrator's `/32`.

## Start or stop an existing deployment

Authenticate with `aws login --profile neon-chat --region ap-southeast-1`.
Find the instance ID in the `neon-chat` CloudFormation stack outputs, then:

```bash
aws ec2 start-instances --profile neon-chat --region ap-southeast-1 --instance-ids INSTANCE_ID
aws ec2 stop-instances --profile neon-chat --region ap-southeast-1 --instance-ids INSTANCE_ID
```

The systemd service starts on boot and renews its seven-day leaf certificate using
its existing private authority. The Elastic IP and public trust certificate stay
unchanged. Allow startup time before running `neon-chat host`.

The instance auto-stops roughly three hours after its timer starts each boot.
Over SSH, `sudo systemctl restart neon-chat-autostop.timer` grants another three
hours. `/quit` closes your client (and your room if hosting), not the instance.
The retained IPv4 costs about $3.65/month even while stopped; disk charges also
continue. The timer is not a spending cap.

## New deployment

[`stack.json`](stack.json) creates the VPC, subnet, gateway, firewall, instance,
and stable address. Supply an existing Singapore SSH key pair, your public IPv4
as `AdminCidr`, `ChatCidr=0.0.0.0/0` for public code-based onboarding, and a reviewed
40-character Git commit containing the service scripts as `AppRevision`.

```bash
aws cloudformation deploy --profile neon-chat --region ap-southeast-1 \
  --stack-name neon-chat --template-file deploy/stack.json \
  --parameter-overrides AdminCidr=YOUR_IP/32 KeyPairName=YOUR_KEY \
  ChatCidr=0.0.0.0/0 AppRevision=REVIEWED_COMMIT
```

Validate with `cfn-lint` and `cfn-guard --rules deploy/security.guard` before
creating/reviewing a change set. Stack completion establishes infrastructure;
verify `sudo cloud-init status --wait` and `sudo systemctl status neon-chat` over
SSH before inviting anyone. Verify the SSH host key through authenticated AWS
console output; never disable host-key checking.

Bootstrap installs a pinned revision, a private legacy password, persistent TLS
authority, and the service. Since the Elastic IP may attach after bootstrap,
restart `neon-chat` after stack completion to issue a leaf for the stable address.
The default AppRevision must be updated to a reviewed room-capable commit when
using this template for a fresh deployment.

A new deployment has a new identity: retrieve **only**
`/home/ubuntu/TCP-Chat/secrets/authority/ca.crt` to `neon_chat/service-ca.crt`, and
set `neon_chat/service.json` to its stable IP/port. Build and distribute the updated
client. Never download or publish `ca.key`, `server.key`, SSH keys, or passwords.
Existing clients trust the original deployment and cannot use a new one until
updated. Normal stop/start does not require this procedure.

## Upgrade the application

On the server, fetch and check out a reviewed commit in `/home/ubuntu/TCP-Chat`,
then run `sudo bash deploy/install-service.sh`. This refreshes the service scripts
and restarts the app, disconnecting existing rooms. Changing CloudFormation
UserData alone does not rerun bootstrap on an existing disk.

The CA is created once and reused. Do not delete `secrets/authority`. The hardened
service can write certificates but cannot replace the authority. Root and the
server account can access its keys. The bundled public CA is not a secret.

## Checks and troubleshooting

- `systemctl is-active neon-chat` and `journalctl -u neon-chat` show service health.
- `systemctl list-timers neon-chat-autostop.timer` shows shutdown time.
- Offline: check instance state, service, TCP 5000, and your network's outbound rules.
- Invalid code: the host must still be connected; start a new room if it expired.
- TLS failure: check leaf expiry, address and bundled CA; never disable verification.
- Rate limit: wait one minute; devices behind one router share the login budget.
- TLS protects client/server links, not end-to-end messages. The server can read them.
- No database or message logging; participants may retain terminal output.

Deleting the stack terminates the instance, deletes its disk/authority, and releases
its address. Separately imported SSH key pairs remain. Use deletion only when
finished permanently and after retaining anything needed.
