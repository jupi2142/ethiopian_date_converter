#!/usr/bin/env python
# -*- coding: utf-8 -*-
import calendar
from datetime import date
from functools import wraps

JD_EPOCH_OFFSET_AMETE_ALEM = -285019    # ዓ/ዓ
JD_EPOCH_OFFSET_AMETE_MIHRET = 1723856  # ዓ/ም
JD_EPOCH_OFFSET_GREGORIAN = 1721426

era_to_offset = {
    "AM": JD_EPOCH_OFFSET_AMETE_MIHRET,
    "AA": JD_EPOCH_OFFSET_AMETE_ALEM,
}


def string_dates(function):
    @wraps(function)
    def inner(date, *args, **kwargs):
        year, month, day = map(int, date.split('-'))
        return "{:04d}-{:02d}-{:02d}".format(
            *function(year, month, day, *args, **kwargs)
        )
    return inner


def ethiopian_coptic_to_julian_day_number(year, month, day, era):
    """
    Computes the Julian day number of the given Coptic or Ethiopic date.
    This method assumes that the JDN epoch offset has been set. This method
    is called by copticToGregorian and ethiopian_to_gregorian which will set
    the jdn offset context.

    :year: year in the Ethiopic calendar
    :month: month in the Ethiopic calendar
    :day: date in the Ethiopic calendar
    :era: [description]

    :returns: The Julian Day Number (JDN)
    """
    return (era + 365) + 365 * (year - 1) + (year / 4) + 30 * month + day - 31


def julian_day_number_to_gregorian(jdn,
                                   JD_OFFSET=JD_EPOCH_OFFSET_GREGORIAN,
                                   leapYear=calendar.isleap):
    """
    Converts JDN to Gregorian

    :jdn:
    :JD_OFFSET:
    :leapYear:
    :returns:
    """
    nMonths = 12
    monthDays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    r2000 = (jdn - JD_OFFSET) % 730485
    r400 = (jdn - JD_OFFSET) % 146097
    r100 = r400 % 36524
    r4 = r100 % 1461

    n = (r4 % 365) + 365 * (r4 / 1460)
    s = (r4 / 1095)
    aprime = 400 * ((jdn - JD_OFFSET) / 146097) + 100 * (r400 / 36524) + 4 * (
        r100 / 1461) + (r4 / 365) - (r4 / 1460) - (r2000 / 730484)
    year = aprime + 1
    t = ((364 + s - n) / 306)
    month = t * ((n / 31) + 1) + (1 - t) * (((5 * (n - s) + 13) / 153) + 1)
    n += 1 - (r2000 / 730484)
    day = n

    if ((r100 == 0) and (n == 0) and (r400 != 0)):
        month = 12
        day = 31
    else:
        monthDays[2] = 29 if (leapYear(year)) else 28
        for i in range(1, nMonths + 1):
            if n <= monthDays[i]:
                day = n
                break
            n -= monthDays[i]
    return (year, month, day)


def guessEra(jdn,
             JD_AM=JD_EPOCH_OFFSET_AMETE_MIHRET,
             JD_AA=JD_EPOCH_OFFSET_AMETE_ALEM):
    """
    Guesses ERA from JDN

    :jdn:
    :returns: {Number}
    """
    return JD_AM if jdn >= (JD_AM + 365) else JD_AA


def gregorian_to_julian_day_number(
        year=1, month=1,
        day=1, JD_OFFSET=JD_EPOCH_OFFSET_GREGORIAN):
    """
    Given year, month and day of Gregorian returns JDN

    :year:
    :month:
    :day:
    :JD_OFFSET:
    :returns:
    """
    s = (year / 4) - ((year - 1) / 4) - (year / 100) + (
        (year - 1) / 100) + (year / 400) - ((year - 1) / 400)
    t = ((14 - month) / 12)
    n = 31 * t * (month - 1) + (1 - t) * (59 + s + 30 * (month - 3) +
                                          ((3 * month - 7) / 5)) + day - 1
    j = JD_OFFSET + 365 * (year - 1) + ((year - 1) / 4) - ((year - 1) / 100) + (
        (year - 1) / 400) + n
    return j


def julian_day_number_to_ethiopic(jdn, era=JD_EPOCH_OFFSET_AMETE_MIHRET):
    """
    Given a JDN and an era returns the Ethiopic equivalent

    :jdn:
    :era:
    :returns: (year, month, day)
    """
    r = ((jdn - era) % 1461)
    n = (r % 365) + 365 * (r / 1460)
    year = 4 * ((jdn - era) / 1461) + (r / 365) - (r / 1460)
    month = (n / 30) + 1
    day = (n % 30) + 1
    return year, month, day


@string_dates
def ethiopian_to_gregorian(year=1,
                           month=1,
                           day=1,
                           era=JD_EPOCH_OFFSET_AMETE_MIHRET):
    if month not in range(1, 14):
        raise ValueError("Invalid month")
    if year <= 0:
        raise ValueError("Invalid year")
    if day not in range(1, 31):
        raise ValueError("Invalid day")
    if month == 13 and day not in range(1, 7):  # How about non leap year Pagume
        raise ValueError("Invalid day")
    return julian_day_number_to_gregorian(
        ethiopian_coptic_to_julian_day_number(year, month, day, era)
    )


@string_dates
def gregorian_to_ethiopic(year=1, month=1, day=1):
    date(year=year, month=month, day=day)
    jdn = gregorian_to_julian_day_number(year, month, day)
    return julian_day_number_to_ethiopic(jdn, guessEra(jdn))


def converter(date, era="AM", to='gregorian'):
    if to == 'gregorian':
        return ethiopian_to_gregorian(date, era=era_to_offset[era])
    elif to == 'ethiopian':
        return gregorian_to_ethiopic(date)
