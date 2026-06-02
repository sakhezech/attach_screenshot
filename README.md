# attach_screenshot

A script for attaching screenshots to Anki notes with `grimblast` (or other utilities that can write to stdout).

## Usage

Pipe the screenshot into the utility

```console
grimblast save area - | attach_screenshot Picture
```

where `Picture` is the image field.

## Installation

```console
pipx install git+https://github.com/sakhezech/attach_screenshot
# or
uv tool install git+https://github.com/sakhezech/attach_screenshot
```
