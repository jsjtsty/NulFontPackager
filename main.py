import argparse
import collections
import os
import shlex
import subprocess
import tempfile
from typing import Any

from config import read_config, find_process_font_paths, parse_process_tasks
from font import build_font_library, create_font_subset
from subtitle import build_char_map


def generate_command(task: dict, font_list: list[str]) -> list[str]:
    media: str = task['media']
    subtitle: str = task['subtitle']
    output: str = task['output']

    command_parts: list[str] = [
        'mkvmerge',
        '-o',
        output,
        '--no-subtitles',
        '--no-attachments',
        media,
        '--language',
        '0:chi',
        '--default-track',
        '0:yes',
        subtitle,
    ]

    for font in font_list:
        font_name = os.path.basename(font)
        font_type = font[-3:].lower()
        if font_type == 'ttf':
            mime = 'font/ttf'
        elif font_type == 'otf':
            mime = 'font/otf'
        else:
            raise RuntimeError(f'Unknown font type: {font_type}')

        command_parts.extend([
            '--attachment-mime-type',
            mime,
            '--attachment-name',
            font_name,
            '--attach-file',
            font,
        ])

    return command_parts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True, type=str)

    args = parser.parse_args()

    config_path: str = args.config
    config = read_config(config_path)

    font_paths: list[str] = find_process_font_paths(config)
    library: list[dict[str, Any]] = build_font_library(font_paths)
    tasks: list[dict[str, str]] = parse_process_tasks(config)

    font_library_names: set[str] = set()
    for font in library:
        font_library_names.update(font['names'])

    for task in tasks:
        subtitle: str = task['subtitle']
        char_map: dict[str, set[str]] = build_char_map(subtitle)
        result_map: dict[int, set[str]] = collections.defaultdict(set[str])

        for estimated_font_name in char_map.keys():
            if estimated_font_name not in font_library_names:
                raise RuntimeError(f'Warning: Font \'{estimated_font_name}\' not found in font library.')

        designated_fonts: set[str] = set()
        for index, font in enumerate(library):
            names: list[str] = font['names']
            for name in names:
                if name in designated_fonts:
                    break
                if name in char_map.keys():
                    result_map[index].update(char_map[name])
                    designated_fonts.add(name)

        with tempfile.TemporaryDirectory(prefix='nul-font-packager-') as temp_dir:
            font_list: list[str] = []
            for index, charset in result_map.items():
                font_list.append(create_font_subset(library[index], charset, temp_dir))

            command: list[str] = generate_command(task, font_list)
            print(shlex.join(command))
            subprocess.run(command, check=True)


if __name__ == '__main__':
    main()
