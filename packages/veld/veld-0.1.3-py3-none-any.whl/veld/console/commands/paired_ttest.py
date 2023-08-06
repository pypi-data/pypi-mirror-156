# -*- coding: utf-8 -*-

import json
import math

from veld.core.betain import betain
from veld.core.streamed_variance import StreamedVariance
from veld.exceptions import InvalidInputError

from ._base import VeldCommand


class PairedTTestCommand(VeldCommand):
    def __init__(self):
        super().__init__(
            name="paired-ttest",
            title="Perform a paired t-test on two-dimensional data",
            description=(
                "This command can be used to run a paired differences t-test "
                "on a two-dimensional stream of input data. This is used when "
                "two sets of observations are made on the same collection of "
                "objects. The observations for each object must be on the "
                "same line (that is, they must be paired). An example "
                "application could be to test if a change in an algorithm "
                "significantly improved its runtime on a set of test cases."
            ),
        )

    def register(self) -> None:
        super().register()
        self.add_argument(
            "--nan",
            help="How to handle NaN values",
            choices=["raise", "propagate", "omit"],
            description=(
                "It can happen that nan values are present in the data stream "
                "(either because they're created by the process or when using "
                "the -i / --ignore-invalid option). With this option the user "
                "can decide what should happen when these values are "
                "encountered. The default behavior is to 'raise' an error "
                "when a NaN value is found. Alternatively, the user can "
                "choose to 'propagate' nan values, or 'omit' rows in the data "
                "stream that contain them."
            ),
            default="raise",
        )
        self.add_argument(
            "-j",
            "--json",
            help="Print structured output in JSON format",
            action="store_true",
        )

    def handle(self) -> int:
        streamed_var = StreamedVariance()
        sp = self.default_stream_processor

        # Compute necessary statistics in a streaming fashion
        for values in sp:
            if len(values) != 2:
                raise InvalidInputError(
                    f"The {self.name} command only two-dimensional input data."
                )
            if any(map(math.isnan, values)):
                if self.args.nan == "raise":
                    raise InvalidInputError(
                        f"Received nan value on line: {sp.last_line}"
                    )
                elif self.args.nan == "omit":
                    continue

            a, b = values
            diff = a - b
            streamed_var.update(diff)

        mean_D = streamed_var.mean
        std_D = streamed_var.stdev
        n = streamed_var.count

        # Compute t-statistic and degrees of freedom
        t = mean_D / (std_D / math.sqrt(n))
        df = n - 1

        # Use the incomplete beta integral to get the p-value
        x = df / (df + t * t)
        p_value = betain(x, df / 2, 1 / 2)
        reject_at_005 = p_value < 0.05

        if self.args.json:
            obj = {
                "statistic": t,
                "dof": df,
                "pvalue": p_value,
                "reject_H0_at_0.05": reject_at_005,
                "mean_difference": mean_D,
                "std_difference": std_D,
                "count": n,
            }
            print(json.dumps(obj, indent="\t"))
        else:
            out = f"Test statistic = {t:.6f}\npvalue = {p_value:.6g}"
            print(out)
        return 0
