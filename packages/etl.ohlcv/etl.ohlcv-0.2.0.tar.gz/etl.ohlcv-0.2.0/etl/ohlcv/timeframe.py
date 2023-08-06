"""Module containing the Timeframe class."""

from __future__ import annotations

from dateutil.relativedelta import relativedelta

from etl.ohlcv.timeunit import TimeUnit


__all__ = [
    # Class exports
    "Timeframe",
]


class Timeframe:
    """Object representation of a timeframe.

    Example:
    ```python
    timeframe_1 = Timeframe("1h")
    timeframe_2 = Timeframe(interval=1, unit="h")
    timeframe_3 = Timeframe(timeframe_1)

    # These three are equal
    assert timeframe_1 == timeframe_2 == timeframe_3

    # These are equal as well
    assert Timeframe("1d") == Timeframe("24h")
    ```

    Arguments:
        interval: This can be the actual interval of the timeframe
            as an `int` or `float`. It can also be used to input an
            existing `Timeframe` object or a string containing the
            interval and the unit of the timeframe.
        unit: The unit of the timeframe. Used only if the value of
            the `interval` argument is an `int` or `float`.

    Attribute:
        interval: The integer interval of the timeframe. There are times
            where the `OHLCV` class tries to automatically detect
            the timeframe. In the case where it can't detect it,
            the value of the interval is `None`.
    """

    def __init__(
        self,
        interval: Timeframe | str | int | float | None = None,
        unit: TimeUnit | str | None = None,
    ):
        # Input is None, so let's just assign None internally
        if not interval and interval != 0:
            self.interval = None
            self.unit = None

        # Input is another `Timeframe` object, let's extract the
        # internal components and assign them to the new timeframe
        elif isinstance(interval, Timeframe):
            self.interval = interval.interval
            self.unit = interval.unit

        # Input is a string. Check whether the `interval` argument
        # contains the all digits, if it is then we need to use the
        # `unit` argument. Otherwise, `interval` contains both the
        # interval and the unit of the timeframe
        elif isinstance(interval, str):

            # Input interval already includes the unit
            if not interval.isdigit():

                # Special case: millisecond has 2 characters as the unit
                if interval.endswith(TimeUnit.MILLISECOND):
                    self.interval = interval[:-2]
                    self.unit = interval[-2:]
                else:
                    self.interval = interval[:-1]
                    self.unit = interval[-1:]

            # Input interval is just the interval, use the unit argument
            else:
                self.interval = interval
                self.unit = unit

        elif isinstance(interval, (int, float)):
            self.interval = interval
            self.unit = unit

        else:
            raise ValueError(f"Invalid timeframe: {(interval, unit)}")

    def __repr__(self):
        properties = ["interval", "unit"]
        return (
            f"{self.__class__.__name__}("
            + ", ".join([f"{p}={getattr(self, p)!r}" for p in properties])
            + ")"
        )

    def __str__(self):
        return (
            f"{self.interval if self.interval else 0}"
            f"{self.unit if self.unit else ''}"
        )

    def __bool__(self):
        return bool(self.interval and self.unit and self.interval != 0)

    def __eq__(self, other):
        if not isinstance(other, Timeframe):
            other = Timeframe(other)
        if bool(self) and bool(other):
            return self.get_duration() == other.get_duration()
        return str(self) == str(other)

    def get_duration(self, unit: str = "ms") -> float | int:
        """Get the duration of the timeframe in the target unit.

        Arguments:
            unit: The target unit of time that we want the duration
                in. Valid input values are `"y"`, `"M"`, `"w"`, `"d"`,
                `"h"`, `"m"`, `"s"`, and `"ms"`.

        Return:
            A floating number representing the duration of the
            timeframe in the target unit of time. If the target unit
            is "milliseconds" then the return type is an integer.
        """
        if not self.interval or not self.unit:
            return 0

        duration_in_seconds = self.unit.to_seconds()
        duration_in_seconds *= self.interval

        # Convert target unit to our standard class
        target_unit = TimeUnit(unit)

        duration_in_target_unit = target_unit.to_seconds()
        duration_in_target_unit = 1 / duration_in_target_unit
        duration_in_target_unit *= duration_in_seconds

        # Type casting function: int for milliseconds, float for others
        type_fn = int if unit == TimeUnit.MILLISECOND else float

        return type_fn(duration_in_target_unit)

    def to_timedelta(self) -> relativedelta:
        """Returns the equivalent timedelta object of the timeframe."""

        # Month and year is not accepted as timedelta key arguments
        # so we need to cover them specifically. Note that these
        # timedeltas are not accurate because we don't take into
        # account leap years and all those edge cases.

        if self.unit == TimeUnit.MONTH:
            return relativedelta(days=(365 / 12.0) * self.interval)

        if self.unit == TimeUnit.YEAR:
            return relativedelta(days=365 * self.interval)

        if self.unit == TimeUnit.MILLISECOND:
            return relativedelta(microseconds=int(self.interval))

        return relativedelta(
            **{f"{self.unit.to_word()}s": self.get_duration(unit=self.unit)}
        )

    @property
    def interval(self) -> float | int:
        return self._interval

    @interval.setter
    def interval(self, value: str | int | float | None):
        if not value and value != 0:
            self._interval = None
        else:
            try:
                self._interval = int(float(value))
            except (TypeError, ValueError):
                self._interval = None

    @property
    def unit(self) -> TimeUnit:
        return self._unit

    @unit.setter
    def unit(self, value: TimeUnit | str | None):
        self._unit = TimeUnit(value)
