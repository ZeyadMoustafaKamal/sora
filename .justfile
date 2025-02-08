run +args="":
  @uv run sora/cli.py {{ args }}

install:
  @uv tool install . --reinstall

