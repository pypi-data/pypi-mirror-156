from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nwon_baseline.typings import TerminalColors, TerminalStyling


def print_with_color_and_style(
    text: str, color: "TerminalColors", style: "TerminalStyling"
) -> None:
    print(f"{color.value}{text}{style.value}")


def print_with_style(text: str, style: "TerminalStyling") -> None:
    print(f"{text}{style.value}")
