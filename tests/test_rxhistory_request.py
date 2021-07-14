from datetime import datetime

from script_facade.client.client import subtract_years


def test_leap_year_subtraction():
    leap_day = datetime.strptime('2020-02-29', '%Y-%m-%d')

    leap_day_2_years_ago = subtract_years(dt=leap_day, years=2)

    assert leap_day_2_years_ago.strftime('%Y-%m-%d') == '2018-02-28'
