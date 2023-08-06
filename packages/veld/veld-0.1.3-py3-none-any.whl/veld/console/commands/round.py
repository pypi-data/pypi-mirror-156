# -*- coding: utf-8 -*-

from ._base import VeldCommand


class RoundCommand(VeldCommand):
    def __init__(self):
        super().__init__(
            name="round",
            title="Round the floating point values in the input stream",
        )

    def register(self):
        super().register()
        self.add_argument(
            "-n",
            "--n-digits",
            type=int,
            default=None,
            help="The precision to round towards",
            description=(
                "The input values are rounded to the closest multiple of 10 "
                'to the power of ndigits, using the built-in "round" '
                "function of Python. If two multiples of 10 are equally "
                "close, rounding is done towards the even choice. Any "
                "integer value of ndigits can be used (negative, positive, "
                "or zero)."
            ),
        )

    def handle(self) -> int:
        for values in self.default_stream_processor:
            outvalues = []
            for i in range(len(values)):
                val = values[i]
                outvalues.append(round(val, self.args.n_digits))
            print(self.args.separator.join(map(str, outvalues)))
        return 0
