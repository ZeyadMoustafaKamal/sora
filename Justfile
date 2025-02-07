run +args="":
  @uv run src/cli.py {{ args }}

install:
  @uv tool install . --reinstall

