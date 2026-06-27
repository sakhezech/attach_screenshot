#!/usr/bin/env python3
import argparse
import base64
import enum
import json
import subprocess
import sys
import urllib.request
from collections.abc import Collection, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any


class AttachmentType(enum.StrEnum):
    PICTURE = 'picture'
    VIDEO = 'video'
    AUDIO = 'audio'


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


def get_recently_added_note_ids() -> Sequence[int]:
    result = _post_ankiconnect('findNotes', {'query': 'added:1'})
    if not result:
        raise Exception('no recently added notes')
    result.sort()
    return result


def get_note_info(note_id: int) -> dict[str, Any]:
    return _post_ankiconnect('notesInfo', {'notes': [note_id]})[0]


def update_note_fields_and_tags(
    note_id: int, fields: dict[str, Any], tags: Collection[str] | None = None
) -> None:
    params = {'note': {'id': note_id, 'fields': fields}}
    if tags is not None:
        params['note']['tags'] = tags
    return _post_ankiconnect('updateNote', params)


def attach_media_to_note(
    note_id: int,
    filename: str,
    fields: Collection[str],
    type_: AttachmentType = AttachmentType.PICTURE,
    data: str | None = None,
    path: str | None = None,
) -> None:
    if not ((data is None) ^ (path is None)):
        raise Exception("'data' and 'path' are both set or unset")
    if data is not None and not data:
        raise Exception('no data')

    _post_ankiconnect(
        'updateNoteFields',
        {
            'note': {
                'id': note_id,
                'fields': {},
                type_: [
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


def attach_media_to_last_note(
    filename: str,
    fields: Collection[str],
    type_: AttachmentType = AttachmentType.PICTURE,
    data: str | None = None,
    path: str | None = None,
) -> None:
    note_id = get_recently_added_note_ids()[-1]
    attach_media_to_note(note_id, filename, fields, type_, data, path)


def duplicate_fields_to_last_note(
    fields: Collection[str], duplicate_tags: bool = False
) -> None:
    *_, second_id, last_id = get_recently_added_note_ids()
    info = get_note_info(second_id)
    update_note_fields_and_tags(
        last_id,
        {field: info['fields'][field]['value'] for field in fields},
        info['tags'] if duplicate_tags else None,
    )


def _read_stdin_data() -> str:
    return base64.standard_b64encode(sys.stdin.buffer.read()).decode()


def _send_notification(summary: str, body: str) -> None:
    subprocess.run(['notify-send', summary, body]).check_returncode()


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
        '--type',
        dest='type_',
        type=AttachmentType,
        choices=AttachmentType.__members__.values(),
        default=AttachmentType.PICTURE,
        help='attachment type (defaults ot picture)',
    )
    parser.add_argument(
        '-d',
        '--duplicate',
        action='store_true',
        help='duplicate field from the second-to-last note',
    )
    parser.add_argument(
        '--tags',
        action='store_true',
        help='also duplicate tags',
    )
    parser.add_argument(
        '--ext',
        default='png',
        help='stdin format (defaults to png)',
    )
    parser.add_argument(
        '--notify',
        action='store_true',
        help='send a notification via notify-send',
    )
    parser.add_argument('field', nargs='+', help='target field name')
    args = parser.parse_args(argv)

    fields = args.field
    type_ = args.type_
    duplicate = args.duplicate
    duplicate_tags = args.tags
    ext = args.ext
    data = path = None
    if args.file == Path('-') and not duplicate:
        filename = (
            f'{type_.title()}{datetime.now().strftime("%Y%m%d%H%M%S%f")}.{ext}'
        )
        data = _read_stdin_data()
    else:
        filename = args.file.name
        path = str(args.file.resolve())

    try:
        if duplicate:
            duplicate_fields_to_last_note(fields, duplicate_tags)
        else:
            attach_media_to_last_note(filename, fields, type_, data, path)
    except Exception as err:
        msg = ' '.join(str(v) for v in err.args) if err.args else repr(err)
        if args.notify:
            _send_notification(
                'ERROR', f'{type_.title()} not attached!\n{msg}'
            )
        raise err
    else:
        if args.notify:
            _send_notification('SUCCESS', f'{type_.title()} attached!')


if __name__ == '__main__':
    cli(None)
