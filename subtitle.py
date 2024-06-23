import collections
import re

import pysubs2

from pysubs2 import SSAEvent

fn_pattern = re.compile(r"\\fn([^\\}]*)")


def build_char_map(ass_path: str) -> dict[str, set[str]]:
    subs: pysubs2.SSAFile = pysubs2.load(ass_path, encoding='utf-8-sig')

    style_map: dict[str, str] = {}
    for name, style in subs.styles.items():
        style_map[name] = style.fontname

    font_map_set = collections.defaultdict(set[str])
    for event in subs.events:
        style_name: str = event.style

        font_name: str = style_map[style_name]

        for match in SSAEvent.OVERRIDE_SEQUENCE.finditer(event.text):
            matched_string: str = match.group()
            fn_match = fn_pattern.search(matched_string)
            if fn_match:
                font_name = fn_match.group(1)

        for char in event.plaintext:
            font_map_set[font_name].add(char)

    return font_map_set
