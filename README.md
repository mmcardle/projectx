# Project X

Django and React Boilerplate Project

Python 3.8, 3.9

# Services

Docker Compose Setup

* Nginx container for web app
* Postgres DB
* Redis Cache and Broker

# Devspace

A devspace.yaml config for deployment to kubernetes

# CI

Github actions are in `.github` and run the CI tasks

# Structure

* backend/ - Django 3.X project using Django Channels and Fast API
* frontend/ - React app
* Desktop/ - Electon app
* tests/ - System tests

# How to use Projectx in your own project

Create a new bare project and clone

    git clone git@github.com:<YOUR_USERNAME>/fork-repo.git

Add an upstream remote pointing to original-repo
    
    cd fork-repo
    git remote add upstream git@github.com:mmcardle/projectx.git
    # OR with https
    git remote add upstream https://github.com/mmcardle/projectx.git

Pull from original-repo
    
    git pull upstream main

Push to fork-repo

    git push origin main

Sync fork-repo
    
    cd fork-repo
    git fetch upstream
    git merge upstream/main
    git push origin main

# Fix line endings windows

    $path = "backend/tests/test_app/models.py"
    (Get-Content $path -Raw).Replace("`r`n","`n") | Set-Content $path -Force