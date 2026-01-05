@echo off
setlocal enabledelayedexpansion

(set LF=^
%=empty line=%
)

set /p "a=!LF!Is the load.txt file set properly?!LF!"

python download.py

set /p "a=!LF!Have you downloaded all the archives?!LF!"

python unpack.py

:: SET YOUR PATHS HERE (dest_trigger is a temporary path in your JASM-managed mod folder to copy to and back from to get the mods registered)
set "root_dir=%~dp0"
set "extracted_dir=%~dp0extracted"
set "dest_trigger=<PATH>"

copy /y "load.txt" "%extracted_dir%\load.txt"

cd /d "%extracted_dir%"

for /d %%f in ("*") do (
    echo Moving to trigger: "%%f"
    move "%%f" "%dest_trigger%\"
)

echo Waiting for script to assign UUIDs...
timeout /t 3 /nobreak >nul

cd /d "%dest_trigger%"
for /d %%f in ("*") do (
    echo Moving back: "%%f"
    :: Moving back to the original script directory
    move "%%f" "%extracted_dir%"
)

cd /d "%extracted_dir%"
set /p "a=!LF!Mods imported. Ready to gbloader?!LF!"

python gbloader.py
pause