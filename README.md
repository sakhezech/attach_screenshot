# attach_screenshot

A script for quickly attaching screenshots to Anki notes.

Attaches the screenshot to the last added card. Requires [AnkiConnect](https://ankiweb.net/shared/info/2055492159).

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

> [!WARNING]
>
> > You must not be viewing the note that you are updating on your Anki browser, otherwise the fields will not update.
> > See [this issue](https://github.com/FooSoft/anki-connect/issues/82) for further details.
>
> from [AnkiConnect README](https://git.sr.ht/~foosoft/anki-connect/tree/de6e6e1b8aaf4ae195eb1d1ff6db5409b99b2a3e/item/README.md#codeupdatenotefieldscode)

### More Options

```console
$ attach_screenshot --help
usage: attach_screenshot [-h] [-f FILE] [--ext EXT] [--notify] field

positional arguments:
  field            note picture field name

options:
  -h, --help       show this help message and exit
  -f, --file FILE  file path (defaults to stdin)
  --ext EXT        stdin screenshot format (defaults to png)
  --notify         send a notification via notify-send
```

## Installation

Via `pipx`.

```console
pipx install git+https://github.com/sakhezech/attach_screenshot
```

Via `uv`.

```console
uv tool install git+https://github.com/sakhezech/attach_screenshot
```

Since the script has no external dependencies, just download it.

```console
curl -LO https://raw.githubusercontent.com/sakhezech/attach_screenshot/refs/heads/main/attach_screenshot.py
chmod +x attach_screenshot.py
```
