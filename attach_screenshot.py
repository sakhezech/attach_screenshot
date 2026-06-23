#!/usr/bin/env python3
import argparse
import base64
import json
import subprocess
import sys
import urllib.request
from collections.abc import Collection, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any


def _post_ankiconnect(action: str, params: dict[str, Any]) -> Any:
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


def _get_recently_added_note_ids() -> Sequence[int]:
    result = _post_ankiconnect('findNotes', {'query': 'added:1'})
    if not result:
        raise Exception('no recently added notes')
    result.sort()
    return result


def _get_note_info(note_id: int) -> dict[str, Any]:
    return _post_ankiconnect('notesInfo', {'notes': [note_id]})[0]


def _update_note_fields(note_id: int, fields: dict[str, Any]) -> None:
    return _post_ankiconnect(
        'updateNoteFields', {'note': {'id': note_id, 'fields': fields}}
    )


def _attach_picture_to_note(
    note_id: int,
    filename: str,
    fields: Collection[str],
    data: str | None = None,
    path: str | None = None,
) -> None:
    if not ((data is None) ^ (path is None)):
        raise Exception("'data' and 'path' are both set or unset")
    if data is not None and not data:
        raise Exception('no screenshot data')

    _post_ankiconnect(
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
                        'fields': fields,
                    }
                ],
            }
        },
    )


def attach_picture_to_last_note(
    filename: str,
    fields: Collection[str],
    data: str | None = None,
    path: str | None = None,
) -> None:
    note_id = _get_recently_added_note_ids()[-1]
    _attach_picture_to_note(note_id, filename, fields, data, path)


def duplicate_fields_to_last_note(fields: Collection[str]) -> None:
    *_, second_id, last_id = _get_recently_added_note_ids()
    info = _get_note_info(second_id)
    _update_note_fields(
        last_id, {field: info['fields'][field]['value'] for field in fields}
    )


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
        '-d',
        '--duplicate',
        action='store_true',
        help='duplicate field from the second-to-last note',
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
    parser.add_argument('field', nargs='+', help='note picture field name')
    args = parser.parse_args(argv)

    fields = args.field
    duplicate = args.duplicate
    ext = args.ext
    data = path = None
    if args.file == Path('-') and not duplicate:
        filename = (
            f'Screenshot{datetime.now().strftime("%Y%m%d%H%M%S%f")}.{ext}'
        )
        data = read_screenshot_data()
    else:
        filename = args.file.name
        path = str(args.file.resolve())

    try:
        if duplicate:
            duplicate_fields_to_last_note(fields)
        else:
            attach_picture_to_last_note(filename, fields, data, path)
    except Exception as err:
        msg = ' '.join(str(v) for v in err.args) if err.args else repr(err)
        if args.notify:
            send_notification('ERROR', f'Screenshot not attached!\n{msg}')
        raise err
    else:
        if args.notify:
            send_notification('SUCCESS', 'Screenshot attached!')


if __name__ == '__main__':
    cli(None)
