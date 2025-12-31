$exclude = @("venv", "tjrs_processos.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "tjrs_processos.zip" -Force