# -*- coding: utf-8 -*-

from veld.core.cumsum import cumsum

from ._plot import VeldPlotCommand


class LinesCommand(VeldPlotCommand):
    def __init__(self) -> None:
        super().__init__(
            name="lines", title="Show line plots of the input data"
        )

    def register(self) -> None:
        super().register()
        self.add_argument(
            "-x",
            "--have-x",
            help="Whether the shared x coordinate is in the first column",
            action="store_true",
            description=(
                "The default behavior with multiple input columns is to plot "
                "each column as a separate line, and use a horizontal axis of "
                "sequential integer values. With this option, the user can "
                "specify that the first column in the input data stream "
                "should be used as the horizontal axis."
            ),
        )
        self.add_argument(
            "-c",
            "--consolidate",
            help="Create a single plot instead of multiple subplots",
            action="store_true",
            description=(
                "By default, this command creates a subplot for each "
                "specified dimension. The user can use this argument to "
                "create a single plot with multiple lines instead."
            ),
        )
        self.add_argument(
            "-n",
            "--no-scatter",
            help="Disable the scatter plot component",
            action="store_true",
        )
        self.add_argument(
            "-t",
            "--transpose",
            help="Transpose the data before plotting",
            action="store_true",
        )
        self.add_argument(
            "--cumulative",
            help="Plot the values cumulatively",
            action="store_true",
            description=(
                "This option can be used to plot the values cumulatively. "
                "When specified in combination with --have-x, the values for "
                "the horizontal axis will not be transformed."
            ),
        )
        self.add_argument(
            "--relative",
            help="Plot values relative to the maximum value",
            action="store_true",
            description=(
                "This option can be used to plot the values normalized by the "
                "maximum in each dimension. If combined with the --cumulative "
                "option, the last value in each dimension will be 1."
            ),
        )

    def handle(self) -> int:
        columns = self._consume_stream()
        if columns is None:
            return 1

        if self.args.transpose:
            columns = list(map(list, zip(*columns)))

        # Extract the horizontal axis or set it to a list of integers
        if self.args.have_x:
            x_axis = columns[0]
            columns = columns[1:]
        else:
            x_axis = list(range(len(columns[0])))

        if not columns:
            print(
                "ERROR: Insufficient values remaining for plot (1-dimensional "
                "input and --have-x)."
            )
            return 1

        if self.args.cumulative:
            columns = [cumsum(col) for col in columns]

        if self.args.relative:
            columns = [[v / max(col) for v in col] for col in columns]

        if self.args.consolidate:
            for column in columns:
                if not self.args.no_scatter:
                    self.plt.scatter(x_axis, column)
                self.plt.plot(x_axis, column)
        else:
            fig, axs = self.plt.subplots(len(columns), 1, squeeze=False)
            for i, column in enumerate(columns):
                if not self.args.no_scatter:
                    axs[i, 0].scatter(x_axis, column)
                axs[i, 0].plot(x_axis, column)

        self.set_plot_attributes()
        self.plt.show()
        return 0
