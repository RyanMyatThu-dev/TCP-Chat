#!/bin/sh
# NEON CHAT installer. Requires uv; no administrator privileges needed.
set -eu
cyan='' dim='' reset=''
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ] && [ "${TERM:-}" != 'dumb' ]; then
  cyan=$(printf '\033[38;5;121m')
  dim=$(printf '\033[38;5;245m')
  reset=$(printf '\033[0m')
fi
printf '\n%s' "$cyan"
cat <<'LOGO'
    _   _  _____  ___   _   _
   | \ | || ____|/ _ \ | \ | |
   |  \| ||  _| | | | ||  \| |
   | |\  || |___| |_| || |\  |
   |_| \_||_____|\___/ |_| \_|

           C H A T  /  T E R M I N A L
LOGO
printf '%s\n%s   A little signal in the noise.%s\n\n' "$reset" "$dim" "$reset"
if ! command -v uv >/dev/null 2>&1; then
  printf '  uv is required. Install it first:\n  https://docs.astral.sh/uv/getting-started/installation/\n\n' >&2
  exit 1
fi
printf '%s  [01/02] Installing NEON CHAT...%s\n\n' "$cyan" "$reset"
if ! uv tool install --reinstall --python 3.12 https://github.com/RyanMyatThu-dev/TCP-Chat/archive/refs/heads/main.zip; then
  printf '\n  Installation failed. Check the error above and try again.\n' >&2
  exit 1
fi
printf '\n%s  [02/02] Installation complete.%s\n' "$cyan" "$reset"
printf '\n  CREATE A ROOM     neon-chat host\n  JOIN A FRIEND     neon-chat join YOUR-ROOM-CODE\n\n'
printf '%s  Command not found? Run uv tool update-shell, then reopen\n  your terminal. Rooms are available while the service is online.%s\n\n' "$dim" "$reset"
