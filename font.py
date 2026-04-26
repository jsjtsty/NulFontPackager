import os
import os.path
import warnings
from typing import Any

from fontTools.subset import Subsetter
from fontTools.ttLib import TTFont, TTCollection, TTLibError


def build_font_information(font_path: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []

    file_name: str = os.path.basename(font_path)
    is_collection: bool = False
    fonts: list[TTFont] = []

    try:
        if file_name.lower().endswith('.ttc'):
            is_collection = True
            collection: TTCollection = TTCollection(font_path)
            fonts = collection.fonts
        else:
            fonts.append(TTFont(font_path))
    except TTLibError:
        warnings.warn('Warning: Cannot read font file: {}'.format(file_name))

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


def create_font_subset(font_info: dict, charset: set[str], output_dir: str | None = None) -> str:
    def get_output_name(strings: list[str]) -> str:
        for s in strings:
            if s.isascii():
                return s
        return strings[0]

    def get_safe_file_name(file_name: str) -> str:
        result = file_name.replace(os.sep, '_')
        if os.altsep is not None:
            result = result.replace(os.altsep, '_')
        return result

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

    font_ext: str = font_info['path'][-4:].lower()

    if font_ext == '.ttc':
        font_ext = '.ttf'

    output_name: str = get_safe_file_name(get_output_name(font_info['names']) + font_ext)
    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        output = os.path.join(output_dir, output_name)
        index = 1
        while os.path.exists(output):
            name, ext = os.path.splitext(output_name)
            output = os.path.join(output_dir, f'{name}-{index}{ext}')
            index += 1
    else:
        output = output_name

    font.save(output)

    return output
