# attach_screenshot

A script for quickly attaching screenshots to Anki notes.

Attaches the screenshot to the last added card.

1. Mine the word you want using [Yomitan](https://yomitan.wiki/).
2. Attach an image by running your screenshot script (preferably with a keybind).

Automation removes friction.

## Usage

Pipe the screenshot into the program

```console
grimblast save area - | attach_screenshot Picture
```

or, if your screenshot utility can't write to stdout, you can save the screenshot into a temporary directory and attach the last added file

```console
ls -t /path/to/directory/* | head -1 | xargs -I {} attach_screenshot --file {} Picture
```

where `Picture` is the image field.

## Installation

```console
pipx install git+https://github.com/sakhezech/attach_screenshot
# or
uv tool install git+https://github.com/sakhezech/attach_screenshot
```
