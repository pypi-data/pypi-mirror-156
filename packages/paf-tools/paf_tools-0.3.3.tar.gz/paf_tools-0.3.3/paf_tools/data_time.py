from datetime import datetime
from enum import Enum


class ReturnType(Enum):
    FULL_DATE = 'FullData'
    FULL_DATE_STRING = 'FullDateString'
    DAY = 'Day'
    MONTH = 'Month'
    YEAR = 'Year'


@staticmethod
def today_Minus_X_Months(months_count, at_start_of_month=False):
    pass


# System.DateTime nowDate = default;
# nowDate = nowDate.AddMonths(-monthsCount);
# return (atStartOfMonth ? '01' : nowDate.Day.ToString()) + '.' + nowDate.Month + ':' + nowDate.Year;

@staticmethod
def last_Day_Last_Month(return_type):
    pass


# System.DateTime lastMonthLastDay = System.DateTime.Today.AddDays(0 - System.DateTime.Today.Day);
# return ReturnValue(lastMonthLastDay, returnType);

@staticmethod
def first_Day_Last_Month(return_type):
    pass


# System.DateTime lastMonthLastDay = DateTime.LastDayLastMonth(ReturnType.FullDate);
# System.DateTime lastMonthFirstDay = lastMonthLastDay.AddDays(1 - lastMonthLastDay.Day);
# return ReturnValue(lastMonthFirstDay, returnType);

@staticmethod
def email_Report_Date(pre_string=None, post_string=None):
    return pre_string is not None and pre_string + ' ' or '[' + datetime.now().strftime(
        '%Y-%m-%d - %H:%M:%S') + ']' + post_string is not None and ' ' + post_string or ''
