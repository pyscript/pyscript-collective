# TODO

## Now

- CDN mode

## Soon

- Start documentation for example writers
  - Explain that we own the `src` in `py-config`
- Remove the hack in noxfile to have tests only run the "fast" ones
  - Playright files get the example index.html directly
  - And thus, don't have the py-config src re-pointed to cdn
  - When run in nox, there are no local files and need to do CDN

## Eventually

- Get numpy, pandas, etc. downloaded into local dir
- Get rid of Poetry

## Done

- Add a build step for the downloader
- Upgrade to latest PyScript
- Upgrade mypy
- Remove type hints from examples
- Add another example
