import datetime


class DateValidator:


    @staticmethod
    def dateToString(date):
        format_string = '%Y-%m-%dT%H:%M:%S.%f'
        return date.strftime(format_string)[:-3] + "Z"


    @staticmethod
    def validateDateString(date_string):
        format_string = '%Y-%m-%dT%H:%M:%S.%f%z'
        return datetime.datetime.strptime(date_string, format_string)