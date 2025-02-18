run +args="":
  @uv run -m sora {{ args }}

install:
  @uv tool install . --reinstall

clean:
  @rm -rf build sora.egg-info

