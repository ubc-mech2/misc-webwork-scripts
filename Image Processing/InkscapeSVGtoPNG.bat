@echo off
for %%f in (%*) do (
    echo %%~f
    "C:\Program Files\Inkscape\inkscape.exe" ^
      -z ^
      --export-background-opacity=255 ^
      --export-dpi=400 ^
      --export-png="%%~dpnf.png" ^
      --export-background="#ffffff" ^
      --file="%%~f"

)