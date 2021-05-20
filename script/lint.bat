@echo off
black --check backend/
if %errorlevel% EQU 1 exit /b %errorlevel%
pylint backend/
if %errorlevel% EQU 1 exit /b %errorlevel%
isort --check-only --diff backend/
if %errorlevel% EQU 1 exit /b %errorlevel%
unify --check-only --recursive --quote \" backend/
if %errorlevel% EQU 1 exit /b %errorlevel%
pipenv update --outdated
if %errorlevel% EQU 1 exit /b %errorlevel%
yarn --cwd frontend lint
if %errorlevel% EQU 1 exit /b %errorlevel%