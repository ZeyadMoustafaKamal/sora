run +args="":
  @uv run -m sora.cli {{ args }}

install:
  @uv tool install . --reinstall

