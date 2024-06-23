import os.path
from typing import Any

from fontTools.subset import Subsetter
from fontTools.ttLib import TTFont, TTCollection

from exception import NulException


def build_font_information(font_path: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []

    file_name: str = os.path.basename(font_path)
    is_collection: bool = False
    fonts: list[TTFont] = []

    if file_name.endswith('.ttc'):
        is_collection = True
        collection: TTCollection = TTCollection(font_path)
        fonts = collection.fonts
    else:
        fonts.append(TTFont(font_path))

    for index, font in enumerate(fonts):
        current_result: dict[str, Any] = {'collection': is_collection, 'path': font_path}
        if is_collection:
            current_result['index'] = index
        names: set[str] = set()
        for record in font['name'].names:
            if record.nameID == 4:
                names.add(record.toUnicode().strip())
        current_result['names'] = list(names)
        result.append(current_result)

    return result


def build_font_library(font_paths: list[str]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []

    for font_path in font_paths:
        font_info = build_font_information(font_path)
        result.extend(font_info)

    return result


def create_font_subset(font_info: dict, charset: set[str]) -> str:
    def get_output_name(strings: list[str]) -> str:
        for s in strings:
            if s.isascii():
                return s
        raise NulException('Invalid name table')

    is_collection: bool = font_info['collection']
    if is_collection:
        index: int = font_info['index']
        collection: TTCollection = TTCollection(font_info['path'])
        font: TTFont = collection.fonts[index]
    else:
        font: TTFont = TTFont(font_info['path'])

    names = font['name'].names

    subsetter = Subsetter()
    text: str = ''.join(sorted(charset))
    subsetter.populate(text=text)

    subsetter.subset(font)

    font['name'].names = names

    output: str = get_output_name(font_info['names']) + font_info['path'][-4:].lower()
    font.save(output, reorderTables=False)

    return output
