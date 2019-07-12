"""
    Copyright (C) 2019  Judah Caruso Rodriguez

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import sys
import toml

# ===========================================================================

INDENT_LEVEL = 4

TERM_TO_HEX = {}
TERM_TO_COLOR = {}


def parse_colors(colors):
    """ not happy with this, but it works """
    for name, values in colors.items():
        for _type in values:
            for i, code in enumerate(values["hex"]):
                c_name = name
                h_code = code
                t_color = values["term"][i]

                if code[0] == "*":
                    c_name = "Dark" + c_name
                    h_code = h_code[1:]

                TERM_TO_HEX[int(t_color)] = f"#{h_code}"
                TERM_TO_COLOR[int(t_color)] = c_name


def to_hex(color):
    if color == -1 or color == 'NONE':
        return 'NONE'

    try:
        return TERM_TO_HEX[color]
    except KeyError as err:
        print(f"Invalid color '{color}'!")
        sys.exit(-1)


def to_gui(color):
    if color == -1 or color == 'NONE':
        return 'NONE'

    try:
        return TERM_TO_COLOR[color]
    except KeyError as err:
        print(f"Invalid color '{color}'!")
        sys.exit(-1)


def convert_theme_to_vimscript(name, theme):
    """
    Takes a name (string) and a theme (dict) and returns valid vimscript theme
    code (string).
    """
    ws_indent = 0
    vimscript = []
    colors_gui = []
    colors_term = []

    for ident, values in theme.items():
        flags = None
        if values["term"] != -1:
            flags = ','.join(values["term"])

        cterm = 'NONE' if not flags else flags
        ctermfg = 'NONE' if values["fg"] == -1 else values["fg"]
        ctermbg = 'NONE' if values["bg"] == -1 else values["bg"]
        gui = cterm
        guifg = to_hex(ctermfg)
        guibg = to_hex(ctermbg)

        colors_gui.append(f"hi {ident} cterm={cterm} ctermfg={ctermfg} ctermbg={ctermbg} gui={gui} guifg={guifg} guibg={guibg}")
        colors_term.append(f"hi {ident} cterm={cterm} ctermfg={to_gui(ctermfg)} ctermbg={to_gui(ctermbg)}")

    vimscript.append(f"if s:main_color == '{name}'")
    ws_indent += INDENT_LEVEL

    vimscript.append(f"{' ' * ws_indent}if has('gui_running') || &t_Co == 256")
    ws_indent += INDENT_LEVEL

    vimscript.append("\n".join([f"{' ' * ws_indent}{line}" for line in colors_gui]))
    ws_indent -= INDENT_LEVEL

    vimscript.append(f"{' ' * ws_indent}else")
    ws_indent += INDENT_LEVEL

    vimscript.append("\n".join([f"{' ' * ws_indent}{line}" for line in colors_term]))
    ws_indent -= INDENT_LEVEL

    vimscript.append(f"{' ' * ws_indent}endif")
    ws_indent -= INDENT_LEVEL
    vimscript.append(f"{' ' * ws_indent}endif\n")

    return "\n".join(vimscript)


def convert_highlights_to_vimscript(highlights):
    """
    Takes a highlights dict and returns valid vimscript syntax highlighting
    code (string).
    """
    vimscript = []

    for ident, value_dict in highlights.items():
        for scope in value_dict:
            vimscript.append(f"highlight! link {scope} {ident}")

    return "\n".join(vimscript)


def combine_theme_with_base(base, theme):
    """
    Returns a dict with the combined values of base (dict) and theme (dict).
    Theme takes higher precedence and overwrites any values in base.
    """
    new_theme = base.copy()

    for key, value in theme.items():
        new_theme[key] = value

    return new_theme


def file_start(name, version):
    return f"""\
"        Name: {name} ({version})
"     Creator: Judah Caruso Rodriguez <judah@tuta.io>
"     License: GNU General Public License v2.0 (see: LICENSE)
"  Repository: https://github.com/kyoto-shift/film-noir
" Forked From: Andreas van Cranenburgh [vim-256noir] <andreas@unstable.nl>

" Description:
"   A minimal vim colorscheme, focusing on clarity and simplicity. Based off of the
"   colorscheme 'vim-256noir' by Andreas van Cranenburgh <https://github.com/andreasvc/vim-256noir>

highlight clear
set background=dark
if version > 580
    if exists('syntax_on')
        syntax reset
    endif
endif

let s:main_color = get(g:, 'film_noir_color', 'blue')
let g:colors_name = 'film_noir'
"""


def main():
    config_file = toml.load("config.toml")
    parse_colors(config_file["Theme"]["Colors"])

    theme_red = combine_theme_with_base(config_file["Theme"]["Base"], config_file["Theme"]["Red"])
    theme_green = combine_theme_with_base(config_file["Theme"]["Base"], config_file["Theme"]["Green"])
    theme_blue = combine_theme_with_base(config_file["Theme"]["Base"], config_file["Theme"]["Blue"])

    print(file_start(config_file["Information"]["Name"], config_file["Information"]["Version"]))
    print(convert_theme_to_vimscript("red", theme_red))
    print(convert_theme_to_vimscript("green", theme_green))
    print(convert_theme_to_vimscript("blue", theme_blue))
    print(convert_highlights_to_vimscript(config_file["Theme"]["Highlights"]))


if __name__ == "__main__":
    main()
