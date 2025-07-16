import argparse
import collections
import os
import warnings
from typing import Any

from config import read_config, find_process_font_paths, parse_process_tasks
from font import build_font_library, create_font_subset
from subtitle import build_char_map


def generate_command(task: dict, font_list: list[str], aac: bool = False) -> str:
    media: str = task['media']
    subtitle: str = task['subtitle']
    output: str = task['output']

    attach_command: str = ''
    for index, font in enumerate(font_list):
        font_type = font[-3:]
        if font_type == 'ttf':
            mime = 'application/x-truetype-font'
        elif font_type == 'otf':
            mime = 'application/vnd.ms-opentype'
        else:
            raise RuntimeError(f'Unknown font type: {font_type}')
        command = f'-attach "{font}" -metadata:s:t:{index} mimeType="{mime}" '
        attach_command += command

    if not aac:
        audio_command = '-c:a copy'
    else:
        audio_command = '-c:a libfdk_aac -b:a 320k'

    return (f'ffmpeg -i "{media}" -i "{subtitle}" -map 0:v:0 -map 0:a:0 -map 1:s:0 -c:v copy {audio_command} '
            f'-c:s ass -metadata:s:s:0 language=chi '
            f'-disposition:s:0 default ' + attach_command + f'"{output}"')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True, type=str)

    args = parser.parse_args()

    config_path: str = args.config
    config = read_config(config_path)

    font_paths: list[str] = find_process_font_paths(config)
    library: list[dict[str, Any]] = build_font_library(font_paths)
    tasks: list[dict[str, str]] = parse_process_tasks(config)
    aac: bool = config['process']['options']['aac']

    font_library_names: set[str] = set()
    for font in library:
        font_library_names.update(font['names'])

    for task in tasks:
        subtitle: str = task['subtitle']
        char_map: dict[str, set[str]] = build_char_map(subtitle)
        result_map: dict[int, set[str]] = collections.defaultdict(set[str])

        for estimated_font_name in char_map.keys():
            if estimated_font_name not in font_library_names:
                warnings.warn(f'Warning: Font \'{estimated_font_name}\' not found in font library.')

        designated_fonts: set[str] = set()
        for index, font in enumerate(library):
            names: list[str] = font['names']
            for name in names:
                if name in designated_fonts:
                    break
                if name in char_map.keys():
                    result_map[index].update(char_map[name])
                    designated_fonts.add(name)

        font_list: list[str] = []
        for index, charset in result_map.items():
            font_list.append(create_font_subset(library[index], charset))

        command: str = generate_command(task, font_list, aac)
        print(command)
        os.system(command)


if __name__ == '__main__':
    main()
