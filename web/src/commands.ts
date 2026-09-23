export const repository = "https://github.com/RyanMyatThu-dev/TCP-Chat";
const installerRoot =
  "https://raw.githubusercontent.com/RyanMyatThu-dev/TCP-Chat/main/web/public";
export const install = {
  unix: `curl -fsSL ${installerRoot}/install.sh | sh`,
  windows: `irm ${installerRoot}/install.ps1 | iex`,
};
export const uvCommands = {
  unix: "curl -LsSf https://astral.sh/uv/install.sh | sh",
  windows:
    'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"',
};
export function invitation(value: string): string | null {
  const code = value.trim().toUpperCase().replaceAll("-", "");
  return /^[0-9A-HJKMNP-TV-Z]{12}$/.test(code)
    ? code.match(/.{4}/g)!.join("-")
    : null;
}
