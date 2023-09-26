"""Generates PCIO-compatible cards.csv from cards.json."""


from csv import DictWriter
from json import load
from os import listdir
from os.path import isfile
from typing import Any, NotRequired, TypedDict


class CardJSON(TypedDict):
    """A card's JSON specifications"""

    count: int
    type: str
    range: NotRequired[str]
    effects: list[dict[str, str]]
    info: NotRequired[str]


def asset_path(base: str, path: str) -> str:
    """Gets absolute asset path from relative-to-root base path and a relative-to-base path"""

    rel_path = f'{base}/{path}.png'
    if not isfile(rel_path):
        raise ValueError(f'bad path: {rel_path}')
    return f'https://github.com/One-Nose/Myths/blob/main/{rel_path}?raw=true'


def card_dict(name: str, card: CardJSON, card_type: str) -> dict[str, str]:
    """Gets the fields of a card."""

    fields = {
        'label': name,
        'card_type': card_type,
        'range': asset_path(
            'assets/hexes/range',
            card['range'] if 'range' in card else 'untargeted/none',
        ),
    }

    fields.update(get_effects(card['effects']))

    fields.update(
        {
            'info': ' - ' + card['info'] if 'info' in card else '',
            'item-count': str(card['count']),
        }
    )

    return fields


def get_effects(effects: list[dict[str, str]]) -> dict[str, str]:
    """Gets the effect fields of a card from its effects specifications"""

    fields: dict[str, str] = {}

    for i in range(3):
        if i < len(effects):
            fields[f'image{i+1}'] = asset_path('assets/effect', effects[i]['type'])
            fields[f'text{i+1}'] = effects[i]['text'] if 'text' in effects[i] else ''
        else:
            fields[f'image{i+1}'] = fields[f'text{i+1}'] = ''

    return fields


def get_cards(source: str) -> list[dict[str, str]]:
    """Gets the fields of the cards from cards.json."""

    cards = get_json(source)
    return [
        card_dict(name, card, 'ACTION') for name, card in cards['actions'].items()
    ] + [card_dict(name, card, 'STANCE') for name, card in cards['stances'].items()]


def get_json(source: str) -> dict[str, dict[str, CardJSON]]:
    """Gets the cards.json dictionary"""

    with open(source, encoding='UTF-8') as file:
        cards: dict[str, Any] = load(file)

    del cards['$schema']
    return cards


def main() -> None:
    """Generates cards.csv from cards.json."""

    for filename in listdir('cards'):
        cards = get_cards(f'cards/{filename}')
        write_cards(cards, f'csv/{filename}.csv')


def write_cards(cards: list[dict[str, str]], destination: str) -> None:
    """Writes a list of card fields to cards.csv"""

    fieldnames = cards[0].keys()
    with open(destination, 'w', encoding='UTF-8', newline='') as file:
        writer = DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(cards)


if __name__ == '__main__':
    main()
