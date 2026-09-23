#!/bin/bash
# Executed before the server starts; renew the leaf, preserve the authority.
set -euo pipefail
app_dir=/home/ubuntu/TCP-Chat
token=$(curl --fail --silent --show-error --max-time 5 -X PUT \
  -H 'X-aws-ec2-metadata-token-ttl-seconds: 60' \
  http://169.254.169.254/latest/api/token)
public_ip=$(curl --fail --silent --show-error --max-time 5 \
  -H "X-aws-ec2-metadata-token: $token" \
  http://169.254.169.254/latest/meta-data/public-ipv4)
"$app_dir/.venv/bin/python" "$app_dir/tools/issue_service_certificate.py" \
  --host "$public_ip" --authority "$app_dir/secrets/authority" --out "$app_dir/certs/service"
ln -sfn "$app_dir/certs/service/server.crt" "$app_dir/certs/server.crt"
ln -sfn "$app_dir/certs/service/server.key" "$app_dir/certs/server.key"
