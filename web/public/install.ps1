# NEON CHAT installer. Requires uv; no administrator privileges needed.
& {
    $ErrorActionPreference = 'Stop'
    $logo = @'
    _   _  _____  ___   _   _
   | \ | || ____|/ _ \ | \ | |
   |  \| ||  _| | | | ||  \| |
   | |\  || |___| |_| || |\  |
   |_| \_||_____|\___/ |_| \_|

           C H A T  /  T E R M I N A L
'@
    Write-Host ''
    if ($env:NO_COLOR) { Write-Host $logo } else { Write-Host $logo -ForegroundColor Cyan }
    Write-Host "`n   A little signal in the noise.`n"
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        throw 'uv is required. Install it from https://docs.astral.sh/uv/getting-started/installation/ and reopen your terminal.'
    }
    Write-Host "  [01/02] Installing NEON CHAT...`n"
    & uv tool install --reinstall --python 3.12 https://github.com/RyanMyatThu-dev/TCP-Chat/archive/refs/heads/main.zip
    if ($LASTEXITCODE -ne 0) { throw 'Installation failed. Check the error above and try again.' }
    Write-Host "`n  [02/02] Installation complete.`n"
    Write-Host '  CREATE A ROOM     neon-chat host'
    Write-Host '  JOIN A FRIEND     neon-chat join YOUR-ROOM-CODE'
    Write-Host "`n  Command not found? Run uv tool update-shell, then reopen"
    Write-Host "  your terminal. Rooms are available while the service is online.`n"
}
