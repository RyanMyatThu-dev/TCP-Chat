export const repository = "https://github.com/RyanMyatThu-dev/TCP-Chat";
export const install = `uv tool install --python 3.12 ${repository}/archive/refs/heads/main.zip`;
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
