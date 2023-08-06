"""Date format machine, Tool for manipulating date strings."""
import os
import sys
import math
import logging
import yaml
import click
import click_log
import pendulum
from pendulum.parsing.exceptions import ParserError
from tabulate import tabulate
# from . import print_version

log = logging.getLogger(__name__)
click_log.basic_config(log)

APPLE_DIFF_SECONDS = 2082844800
MSOFT_DIFF_DAYS = 25569.0               # noqa
MSOF_DIFF_SECONDS = 2209161600
FILETIME_DIFF_SECONDS = 11644473600


class DateFormatMachine:
    """Date format machine, Tool for manipulating date strings."""

    def __init__(self, parse_string=None, in_type="pendulum", out_type="8601"):
        """Initialize."""
        log.debug("dfm init")

        self.parse_string = parse_string
        self.in_type = in_type
        self.out_type = out_type

        formats_path = os.path.join(
            os.path.dirname(__file__), "dfm_formats.yaml"
        )

        with open(formats_path, "r", encoding="utf-8") as reader:
            self.formats = yaml.safe_load(reader)

    def list(self):
        """Show list of available formats."""
        product = []
        for key in self.formats:
            data = self.formats[key]
            msg_dict = [
                key,
                data["desc"],
                data["example"],
                data["note"],
                data["action"]
            ]
            product.append(msg_dict)

        headers = [
            "key",
            "type",
            "example",
            "note",
            "action"
        ]
        table_data = tabulate(product, headers, tablefmt="simple")

        click.echo(table_data)

    def discover(self, input_string):
        """Attempt to discover what format a given string is using."""
        log.debug(f"discover {input_string}")

        for key in self.formats:
            item = self.formats[key]
            click.echo(item["format"])

    def report(self, pdt):      # noqa
        """Report."""
        log.debug(f"report {pdt}")
        if self.out_type in "unix":
            click.echo(self.to_unix(pdt))

        elif self.out_type in "apple":
            click.echo(self.to_apple(pdt))

        elif self.out_type in "microsoft":
            click.echo(self.to_microsoft(pdt))

        elif self.out_type in "filetime":
            # click.echo("%d" % self.to_filetime(pdt))
            click.echo(f"{self.to_filetime(pdt)}")

        elif self.out_type in "atom":
            click.echo(pdt.to_atom_string())

        elif self.out_type in "cookie":
            click.echo(pdt.to_cookie_string())

        elif self.out_type in "8601":
            click.echo(pdt.to_iso8601_string())

        elif self.out_type in "822":
            click.echo(pdt.to_rfc822_string())

        elif self.out_type in "850":
            click.echo(pdt.to_850_string())

        elif self.out_type in "1036":
            click.echo(pdt.to_1036_string())

        elif self.out_type in "1123":
            click.echo(pdt.to_1123_string())

        elif self.out_type in "2822":
            click.echo(pdt.to_2822_string())

        elif self.out_type in "3339":
            click.echo(pdt.to_3339_string())

        elif self.out_type in "rss":
            click.echo(pdt.to_rss_string())

        elif self.out_type in "w3c":
            click.echo(pdt.to_w3c_string())

        else:
            click.echo(pdt)

    @staticmethod
    def to_unix(pdt):
        """To unix."""
        log.debug("to_unix")
        unix_start = pendulum.datetime(1970, 1, 1, 0, 0, 0)
        diff = pdt - unix_start
        return int(diff.total_seconds())

    @staticmethod
    def to_apple(pdt):
        """To apple."""
        log.debug("to_apple")
        apple_start = pendulum.datetime(1904, 1, 1, 0, 0, 0)
        diff = pdt - apple_start
        return int(diff.total_seconds())

    @staticmethod
    def to_microsoft(pdt):
        """To microsoft."""
        log.debug("to_microsoft")
        msoft_start = pendulum.datetime(1899, 12, 30, 0, 0, 0)
        diff = pdt - msoft_start
        days = diff.in_days()

        seconds = (pdt.hour * 60 * 60) + (pdt.minute * 60) + pdt.second
        log.debug(f"seconds {seconds}")
        fraction = seconds / 86400.0 * 100.0
        seconds_fraction = 100000.0 / 100.0 * fraction
        product = math.modf(seconds_fraction)
        # return float("%d.%d" % (days, product[1]))
        return float(f"{days}.{int(product[1])}")

    @staticmethod
    def to_filetime(pdt):
        """To filetime."""
        log.debug("to_filetime")
        file_start = pendulum.datetime(1601, 1, 1, 0, 0, 0)
        diff = pdt - file_start
        seconds = diff.total_seconds()
        hundred_nanos = seconds * 10000000
        return hundred_nanos

    def parse(self):
        """Parse."""
        product = None
        if self.in_type is not None:

            if self.in_type in "unix":
                product = self.parse_unix_timestamp(self.parse_string)
            elif self.in_type in "apple":
                product = self.parse_apple_timestamp(self.parse_string)
            elif self.in_type in "microsoft":
                product = self.parse_microsoft_timestamp(self.parse_string)
            elif self.in_type in "filetime":
                product = self.parse_filetime_timestamp(self.parse_string)
            elif self.in_type in "pendulum":
                product = self.parse_pendulum(self.parse_string)
        else:
            product = self.parse_pendulum(self.parse_string)

        return product

    def parse_unix_timestamp(self, input_string):
        """Parse unix timestamp."""
        product = None
        log.debug(f"parse_unix_timestamp {input_string} ")
        try:
            product = pendulum.from_timestamp(input_string, tz="UTC")
        except ValueError as error:
            log.critical(error)
        except OSError as error:
            log.critical(error)
            log.critical("Can only handle timestamps starting at 1970")
            sys.exit(3)

        return product

    def parse_apple_timestamp(self, input_string):
        """Parse apple timestamp."""
        log.debug(f"parse_apple_timestamp {input_string}")
        product = None
        try:
            int_input = int(input_string)
            unix = int_input - APPLE_DIFF_SECONDS
            product = self.parse_unix_timestamp(unix)
        except ValueError:
            log.critical("input_string not integer, cannot parse")

        return product

    def msoft_time_to_seconds(self, input_string):
        """
        Convert microsoft time to seconds.

        Valid time values range from .0 (00:00:00) to .99999 (23:59:59).
        The numeric value represents a fraction of one day.
        You can convert the numeric value into hours, minutes, and seconds
        by multiplying the numeric value by 24.

        15:00 hours is 54000 seconds
        fractional 625 * 24 = 15000

        96875 is 11:15:00 P.M.  or 23:15:00
        83700 seconds
        whole_day_in_seconds = 86400.0
        """
        whole_day_in_seconds = 86400.0

        log.debug(f"msoft_time_to_seconds {input_string}")

        input_float = float(input_string)
        percentage = input_float / 0.99999 * 100.0
        log.debug(f"percentage {percentage}")
        seconds_float = whole_day_in_seconds / 100.0 * percentage
        seconds = int(seconds_float)
        log.debug(f"seconds {seconds_float}")
        return seconds

    def parse_microsoft_timestamp(self, input_string):
        """Parse microsoft timestamp.

        https://msdn.microsoft.com/en-us/library/office/ff197413.aspx
        """
        log.debug(f"parse_microsoft_timestamp {input_string}")
        product = None
        try:

            float_input = float(input_string)
            seconds_fraction, days = math.modf(float_input)
            day_seconds = days * 86400.0
            seconds = self.msoft_time_to_seconds(seconds_fraction)
            unix = day_seconds + seconds - MSOF_DIFF_SECONDS
            product = self.parse_unix_timestamp(unix)

        except ValueError:
            log.critical("input_string not a float, cannot parse")

        return product

    def parse_filetime_timestamp(self, input_string):
        """Parse filetime timestamp."""
        product = None
        try:
            int_input = int(input_string)
            # convert input from 100-nanosecond blocks to seconds
            # then subtract the offset to unix epoch
            unix = (int_input / 10000000) - FILETIME_DIFF_SECONDS
            product = self.parse_unix_timestamp(unix)
        except ValueError:
            log.critical("input_string not an integer, cannot parse")

        return product

    def parse_pendulum(self, input_string):
        """Parse pendulum."""
        product = None
        log.debug(f"parse_pendulum {input_string}")
        try:
            product = pendulum.parse(input_string)
        except ParserError as error:
            log.critical(error)
            sys.exit(2)

        return product


def print_list(ctx, param, value):   # noqa ctx is used by the callback
    """Print list of formats."""
    if not value:
        return

    dfm = DateFormatMachine()
    dfm.list()
    sys.exit(0)


@click.command()
@click.argument(
    "parse",
    required=True,
)
@click.option(
    "--list",
    "list",
    is_flag=True,
    callback=print_list,
    expose_value=False,
    help="show list of formats",
    is_eager=True
)
@click.option(
    "--type",
    "in_type",
)
@click.option(
    "--output",
    "--out",
    "out_type",
    default="8601"
)
@click.option(
    "--now",
    "now_flag",
    is_flag=True,
    help="compare date/time to now"
)
@click.option(
    "--days",
    "days_flag",
    is_flag=True,
    help="compare date/time to now in days"
)
@click.pass_context
@click_log.simple_verbosity_option(log)
def cli(ctx, parse, in_type, out_type, now_flag, days_flag):  # noqa
    """Entry point."""
    log.debug("cli")
    log.debug(f"parse {parse}")
    log.debug(f"type  {in_type}")
    log.debug(f"out   {out_type}")

    dfm = DateFormatMachine(
        parse_string=parse,
        in_type=in_type,
        out_type=out_type
    )
    product = dfm.parse()
    log.debug(product)
    if now_flag:
        now_date = pendulum.now()
        log.debug(f"now {now_date}")
        log.debug(f"product {product}")

        click.echo(product.diff_for_humans())

    elif days_flag:
        days_date = pendulum.now()
        click.echo(product.diff(days_date).in_days())
    else:
        dfm.report(product)


if __name__ == "__main__":
    cli()                       # noqa
