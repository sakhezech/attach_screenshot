#!/usr/bin/env python3
import argparse
import base64
import json
import subprocess
import sys
import urllib.request
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Any


def post_ankiconnect(action: str, params: dict[str, Any]) -> Any:
    with urllib.request.urlopen(
        'http://localhost:8765/',
        data=json.dumps(
            {'action': action, 'version': 5, 'params': params}
        ).encode(),
    ) as response:
        r = json.loads(response.read())
    if r['error'] is not None:
        raise Exception(r['error'])
    return r['result']


def get_last_added_card_id() -> int:
    result = post_ankiconnect('findNotes', {'query': 'added:1'})
    if not result:
        raise Exception('no recently added cards')
    return result[-1]


def get_note_id(card_id: int) -> int:
    return post_ankiconnect('notesInfo', {'notes': [card_id]})[0]['noteId']


def attach_picture_to_note(
    note_id: int,
    filename: str,
    field: str,
    data: str | None = None,
    path: str | None = None,
) -> None:
    if not ((data is None) ^ (path is None)):
        raise Exception("'data' and 'path' are both set or unset")
    post_ankiconnect(
        'updateNoteFields',
        {
            'note': {
                'id': note_id,
                'fields': {},
                'picture': [
                    {
                        'filename': filename,
                        'data': data,
                        'path': path,
                        'fields': [field],
                    }
                ],
            }
        },
    )


def attach_picture_to_last_card(
    filename: str, field: str, data: str | None = None, path: str | None = None
) -> None:
    card_id = get_last_added_card_id()
    note_id = get_note_id(card_id)

    attach_picture_to_note(note_id, filename, field, data, path)


def read_screenshot_data() -> str:
    return base64.standard_b64encode(sys.stdin.buffer.read()).decode()


def send_notification(summary: str, body: str) -> None:
    subprocess.run(['notify-send', summary, body])


def cli(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f',
        '--file',
        type=Path,
        default=Path('-'),
        help='file path (defaults to stdin)',
    )
    parser.add_argument(
        '--ext',
        default='png',
        help='stdin screenshot format (defaults to png)',
    )
    parser.add_argument(
        '--notify',
        action='store_true',
        help='send a notification via notify-send',
    )
    parser.add_argument('field', help='note picture field name')
    args = parser.parse_args(argv)

    field = args.field
    data = path = None
    if args.file == Path('-'):
        filename = f'{datetime.now()} screenshot.{args.ext}'
        data = read_screenshot_data()
    else:
        filename = args.file.name
        path = str(args.file.resolve())

    try:
        attach_picture_to_last_card(filename, field, data, path)
    except Exception as err:
        if args.notify:
            send_notification('ERROR', f'Screenshot not attached!\n{err!r}')
        raise err
    else:
        if args.notify:
            send_notification('SUCCESS', 'Screenshot attached!')


if __name__ == '__main__':
    cli(None)
