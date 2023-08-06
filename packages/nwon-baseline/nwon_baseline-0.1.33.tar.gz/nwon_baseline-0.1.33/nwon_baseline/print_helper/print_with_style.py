from typing import TYPE_CHECKING

from nwon_baseline.typings import TerminalStyling

if TYPE_CHECKING:
    from nwon_baseline.typings import TerminalColors


def print_with_color_and_style(
    text: str, color: "TerminalColors", style: "TerminalStyling"
) -> None:
    print(f"{color.value}{style.value}{text}{TerminalStyling.END_CHARACTER.value}")


def print_with_style(text: str, style: "TerminalStyling") -> None:
    print(f"{style.value}{text}{TerminalStyling.END_CHARACTER.value}")
