#!/bin/bash
# Run as root after checking out a reviewed revision on the Ubuntu server.
set -euo pipefail
app_dir=/home/ubuntu/TCP-Chat
install -d -m 700 -o ubuntu -g ubuntu "$app_dir/secrets/authority" "$app_dir/certs"
install -m 755 "$app_dir/deploy/session.sh" /usr/local/bin/neon-chat-session
# Create the persistent authority before starting the restricted service.
runuser -u ubuntu -- /usr/local/bin/neon-chat-session
install -m 644 "$app_dir/deploy/neon-chat.service" /etc/systemd/system/neon-chat.service
install -d /etc/systemd/system/neon-chat.service.d
cat > /etc/systemd/system/neon-chat.service.d/session.conf <<'UNIT'
[Service]
ExecStartPre=/usr/local/bin/neon-chat-session
ReadWritePaths=/home/ubuntu/TCP-Chat/certs
UNIT
systemctl daemon-reload
systemctl enable neon-chat.service
systemctl restart neon-chat.service
