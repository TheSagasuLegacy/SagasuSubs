# flake8:noqa:F405
# type:ignore
from warnings import warn

from pysubs2.substation import *


@classmethod  # type:ignore
def from_file(cls, subs, fp, format_, **kwargs):
    """See :meth:`pysubs2.formats.FormatBase.from_file()`"""

    def _string_to_field(f, v):
        if f in {"start", "end"}:
            if v.startswith("-"):
                # handle negative timestamps
                v = v[1:]
                return -timestamp_to_ms(TIMESTAMP.match(v).groups())
            else:
                return timestamp_to_ms(TIMESTAMP.match(v).groups())
        elif "color" in f:
            return rgba_to_color(v)
        elif f in {"bold", "underline", "italic", "strikeout"}:
            return v == "-1"
        elif f in {
            "borderstyle",
            "encoding",
            "marginl",
            "marginr",
            "marginv",
            "layer",
            "alphalevel",
        }:
            return int(v)
        elif f in {
            "fontsize",
            "scalex",
            "scaley",
            "spacing",
            "angle",
            "outline",
            "shadow",
        }:
            return float(v)
        elif f == "marked":
            return v.endswith("1")
        elif f == "alignment":
            i = int(v)
            if format_ == "ass":
                return i
            else:
                return ssa_to_ass_alignment(i)
        else:
            return v

    def string_to_field(f, v):
        try:
            return _string_to_field(f, v)
        except Exception as e:
            warn(f"Failed to parse field {f=!r},{v=!r} due to {e!r}, fallback to None")

    subs.info.clear()
    subs.aegisub_project.clear()
    subs.styles.clear()
    subs.fonts_opaque.clear()

    inside_info_section = False
    inside_aegisub_section = False
    inside_font_section = False
    current_font_name = None
    current_font_lines_buffer = []

    for lineno, line in enumerate(fp, 1):
        line = line.strip()

        if SECTION_HEADING.match(line):
            logging.debug("at line %d: section heading %s", lineno, line)
            inside_info_section = "Info" in line
            inside_aegisub_section = "Aegisub" in line
            inside_font_section = "Fonts" in line
        elif inside_info_section or inside_aegisub_section:
            if line.startswith(";"):
                continue  # skip comments
            try:
                k, v = line.split(":", 1)
                if inside_info_section:
                    subs.info[k] = v.strip()
                elif inside_aegisub_section:
                    subs.aegisub_project[k] = v.strip()
            except ValueError:
                pass
        elif inside_font_section:
            m = FONT_FILE_HEADING.match(line)

            if current_font_name and (m or not line):
                # flush last font on newline or new font name
                font_data = current_font_lines_buffer[:]
                subs.fonts_opaque[current_font_name] = font_data
                logging.debug(
                    "at line %d: finished font definition %s",
                    lineno,
                    current_font_name,
                )
                current_font_lines_buffer.clear()
                current_font_name = None

            if m:
                # start new font
                font_name = m.group(1)
                current_font_name = font_name
            elif line:
                # add non-empty line to current buffer
                current_font_lines_buffer.append(line)
        elif line.startswith("Style:"):
            _, rest = line.split(":", 1)
            buf = rest.strip().split(",")
            name, raw_fields = buf[0], buf[1:]  # splat workaround for Python 2.7
            field_dict = {
                f: string_to_field(f, v)
                for f, v in zip(STYLE_FIELDS[format_], raw_fields)
            }
            sty = SSAStyle(**field_dict)
            subs.styles[name] = sty
        elif line.startswith("Dialogue:") or line.startswith("Comment:"):
            ev_type, rest = line.split(":", 1)
            raw_fields = rest.strip().split(",", len(EVENT_FIELDS[format_]) - 1)
            field_dict = {
                f: string_to_field(f, v)
                for f, v in zip(EVENT_FIELDS[format_], raw_fields)
            }
            field_dict["type"] = ev_type
            ev = SSAEvent(**field_dict)
            subs.events.append(ev)

    # cleanup fonts
    if current_font_name:
        # flush last font on EOF or new section w/o newline
        font_data = current_font_lines_buffer[:]
        subs.fonts_opaque[current_font_name] = font_data
        logging.debug("at EOF: finished font definition %s", current_font_name)
        current_font_lines_buffer.clear()
        current_font_name = None


from pysubs2 import substation

color_parser = substation.rgba_to_color


def rgba_to_color(rgba: str) -> substation.Color:
    try:
        return color_parser(rgba)
    except Exception as e:
        warn(f"Failed to parse color {rgba!r} due to {e!r}, fallback to #000000.")
        return substation.Color(0, 0, 0)


def patch():
    substation.rgba_to_color = rgba_to_color
    substation.SubstationFormat.from_file = from_file


__all__ = ["patch"]
