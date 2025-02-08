run +args="":
  @uv run -m sora {{ args }}

install:
  @uv tool install . --reinstall

