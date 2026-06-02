import argparse
import base64
import sys
from datetime import datetime
from typing import Any

import httpx


def post_ankiconnect(query: dict[str, Any]) -> Any:
    r = httpx.post('http://localhost:8765/', json=query).json()
    if r['error'] is not None:
        raise Exception(r['error'])
    return r['result']


def get_last_updated_card_id() -> int:
    return post_ankiconnect(
        {
            'action': 'findNotes',
            'version': 5,
            'params': {
                'query': 'added:1',
            },
        }
    )[-1]


def get_note_id(card_id: int) -> int:
    return post_ankiconnect(
        {
            'action': 'notesInfo',
            'version': 5,
            'params': {'notes': [card_id]},
        },
    )[0]['noteId']


def attach_picture_to_note(
    note_id: int, filename: str, data: str, field: str
) -> None:
    post_ankiconnect(
        {
            'action': 'updateNoteFields',
            'version': 5,
            'params': {
                'note': {
                    'id': note_id,
                    'fields': {},
                    'picture': [
                        {
                            'filename': filename,
                            'data': data,
                            'fields': [field],
                        }
                    ],
                }
            },
        }
    )


def attach_picture_to_last_updated_card(
    filename: str, data: str, field: str
) -> None:
    card_id = get_last_updated_card_id()
    note_id = get_note_id(card_id)

    attach_picture_to_note(note_id, filename, data, field)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('field', help='note picture field name')
    args = parser.parse_args()

    filename = f'{datetime.now()}_screenshot.png'
    data = base64.standard_b64encode(sys.stdin.buffer.read()).decode()
    field = args.field

    attach_picture_to_last_updated_card(filename, data, field)
