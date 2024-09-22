# WebSockets Broadcaster - Python

## Pre-requisites
- [uv](https://docs.astral.sh/uv/) (Note that Python is not required)

## Running
```shell
uv run main.py
```

## Deployment
This repository is structured to be deployed to Heroku. The following files are Heroku specific:
- app.json
- Procfile
- requirements.txt (Generated from pyproject.toml, which is the source of truth)
- runtime.txt
