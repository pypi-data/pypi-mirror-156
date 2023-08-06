# -*- coding: utf-8 -*-

import sys

from wilderness import Application
from wilderness import Command

from veld.__version__ import __version__

from .commands.barcount import BarCountCommand
from .commands.comparison import EqualCommand
from .commands.comparison import GreaterEqualCommand
from .commands.comparison import GreaterThanCommand
from .commands.comparison import LessEqualCommand
from .commands.comparison import LessThanCommand
from .commands.comparison import NotEqualCommand
from .commands.count import CountCommand
from .commands.cumsum import CumSumCommand
from .commands.histogram import HistogramCommand
from .commands.lines import LinesCommand
from .commands.log import LogCommand
from .commands.max import MaxCommand
from .commands.mean import MeanCommand
from .commands.median import MedianCommand
from .commands.min import MinCommand
from .commands.mode import ModeCommand
from .commands.paired_ttest import PairedTTestCommand
from .commands.quantile import QuantileCommand
from .commands.round import RoundCommand
from .commands.scatter import ScatterPlotCommand
from .commands.stdev import StandardDeviationCommand
from .commands.sum import SumCommand
from .commands.variance import VarianceCommand


class VeldApplication(Application):

    _description = (
        "Veld is a command line processor for (multi-dimensional) numeric "
        "data streams. It can compute basic univariate statistics such as the "
        "mean or the variance of a stream of numbers, process the stream by "
        "computing logarithms or rounding, or create a histogram or scatter "
        "plot of the data (among other functionality)."
        "\n\n"
        "Veld can be used for quick exploration of a data stream or can be "
        "integrated in a command line data processing pipeline."
        "\n\n"
        "Detailed information on Veld commands can be obtained using: veld "
        "help <command>. Online documentation of Veld can be found via the "
        "GitHub page [1]."
    )

    _extra = {
        "author": (
            "Veld was created by Gertjan van den Burg [2]. See the GitHub "
            "project page at [3] for an up-to-date list of contributors."
        ),
        "reporting bugs": (
            "Any bugs that you encounter can be reported at the GitHub page "
            "for Veld [1]. Please do not hesitate, you're helping to make "
            "this project better for everyone!"
        ),
        "notes": (
            "1. Veld page on GitHub\n"
            "   https://github.com/GjjvdBurg/Veld\n"
            "\n"
            "2. More about Gertjan van den Burg\n"
            "   https://gertjan.dev\n"
            "\n"
            "3. Contributors to Veld\n"
            "   https://github.com/GjjvdBurg/Veld/graphs/contributors\n"
        ),
    }

    def __init__(self):
        super().__init__(
            "veld",
            version=__version__,
            title="Easy command line analytics",
            author="Gerrit J.J. van den Burg",
            description=self._description,
            extra_sections=self._extra,
            add_commands_section=True,
        )

    def register(self):
        self.add_argument(
            "-V",
            "--version",
            help="show version information and exit",
            action="version",
            version=__version__,
        )
        self.add_argument(
            "--debug",
            help="Enable debug mode",
            action="store_true",
            description=(
                "Debug mode disables the default exception handling, which "
                "can be useful for debugging."
            ),
        )

    def get_commands_text(self) -> str:
        text = []
        text.append("We list the available Veld commands by use case.")
        text.append("")
        for group in self.groups:
            if group.is_root:
                continue
            assert group.title is not None
            text.append(group.title.capitalize())
            for command in group.commands:
                assert command.title is not None
                text.append(f"\t{self.name}-{command.name}(1)")
                text.append(f"\t\t{command.title.capitalize() or ''}")
                text.append("")
        text.append(
            "For more information about each command, use: veld help "
            "<command>, or: man veld <command> from the command line."
        )
        return "\n".join(text)

    def set_excepthook(self) -> None:
        sys_hook = sys.excepthook

        def exception_handler(exception_type, value, traceback):
            if self.args.debug:
                sys_hook(exception_type, value, traceback)
            else:
                print(value, file=sys.stderr)

        sys.excepthook = exception_handler

    def run_command(self, command: Command) -> int:
        self.set_excepthook()
        return super().run_command(command)


def build_application() -> Application:
    app = VeldApplication()
    app.set_prolog(
        "Below are the available Veld commands. Use veld help <command>\n"
        "to learn more about each command."
    )
    app.set_epilog(
        "For more information about Veld, visit:\n"
        "https://github.com/GjjvdBurg/Veld"
    )

    group = app.add_group("univariate statistics")
    group.add(SumCommand())
    group.add(MeanCommand())
    group.add(ModeCommand())
    group.add(MedianCommand())
    group.add(StandardDeviationCommand())
    group.add(VarianceCommand())
    group.add(QuantileCommand())

    group = app.add_group("extreme values and counts")
    group.add(MinCommand())
    group.add(MaxCommand())
    group.add(CountCommand())

    group = app.add_group("filtering values")
    group.add(LessThanCommand())
    group.add(LessEqualCommand())
    group.add(GreaterThanCommand())
    group.add(GreaterEqualCommand())
    group.add(EqualCommand())
    group.add(NotEqualCommand())

    group = app.add_group("math operators")
    group.add(LogCommand())
    group.add(RoundCommand())
    group.add(CumSumCommand())

    group = app.add_group("plotting")
    group.add(LinesCommand())
    group.add(ScatterPlotCommand())
    group.add(HistogramCommand())
    group.add(BarCountCommand())

    group = app.add_group("hypothesis testing")
    group.add(PairedTTestCommand())

    return app
