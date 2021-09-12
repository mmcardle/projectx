@echo off
poetry run python -mblack --check backend/
if %errorlevel% EQU 1 exit /b %errorlevel%
poetry run python -m pylint backend/
if %errorlevel% EQU 1 exit /b %errorlevel%
poetry run python -misort --check-only --diff backend/
if %errorlevel% EQU 1 exit /b %errorlevel%
poetry run python -munify --check-only --recursive --quote \" backend/
if %errorlevel% EQU 1 exit /b %errorlevel%
poetry show --outdated
if %errorlevel% EQU 1 exit /b %errorlevel%
yarn --cwd frontend lint
if %errorlevel% EQU 1 exit /b %errorlevel%