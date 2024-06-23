import os

import yaml

from environment import NUL_VERSION
from exception import NulException
from util import get_value_or_default, get_value_or_except


def read_config(config_file_path: str) -> dict:
    with open(config_file_path, encoding='utf-8') as config_file:
        result = yaml.safe_load(config_file)

    # Check version information.
    version: int = get_value_or_except(result, 'version', NulException('No version in config file'))
    if version > NUL_VERSION:
        raise NulException('Unsupported version')

    return result


def find_process_font_paths(parsed_config: dict) -> list[str]:
    result: list[str] = []

    fonts: dict = get_value_or_except(parsed_config, 'fonts', NulException('No fonts in config file'))
    workspaces: list[str] = get_value_or_default(fonts, 'workspaces', [])
    additional_fonts: list[str] = get_value_or_default(parsed_config, 'additional_fonts', [])

    # Check validity of additional fonts.
    for font_path in additional_fonts:
        font_path = font_path.lower()
        if not font_path.endswith(('.ttf', '.otf', '.ttc')):
            raise NulException('Unsupported font format: {}'.format(font_path))

    result.extend(additional_fonts)

    # Find fonts in workspaces.
    for workspace in workspaces:
        for root, dirs, files in os.walk(workspace):
            for file_name in files:
                if not file_name.lower().endswith(('.ttf', '.otf', '.ttc')):
                    continue
                file_path: str = str(os.path.join(root, file_name))
                result.append(file_path)

    return result


def parse_process_tasks(parsed_config: dict) -> list[dict[str, str]]:
    process: dict = get_value_or_except(parsed_config, 'process', NulException('No process in config file'))
    targets: list[dict[str, str]] = get_value_or_except(process, 'targets', NulException('No targets in config file'))
    workspace: str | None = get_value_or_default(process, 'workspace', None)

    result: list[dict[str, str]] = []

    for target in targets:
        current_result: dict[str, str] = {}
        for key, value in target.items():
            if workspace is not None:
                value = os.path.join(workspace, value)
            current_result[key] = value
        result.append(current_result)

    return result
