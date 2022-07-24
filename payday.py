from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, time, datetime
from decimal import Decimal
import calendar
import re
import sys


@dataclass
class Employee:
    name: str
    payment: Decimal = 0


@dataclass
class Period:
    day: int
    time_init: time
    time_finish: time
    rate: Decimal


@dataclass
class WorkedPeriod:
    init_hour: time
    finish_time: time
    day: int


@dataclass
class WorkedWeek:
    # year: int
    # calendar_week: int
    employee: Employee
    work: list[WorkedPeriod]

    def add_work(self, period: WorkedPeriod):
        self.work.append(period)


class OutputFormater(ABC):
    @staticmethod
    @abstractmethod
    def print_payment(self, payment_list: Employee):
        pass


class TextOutputFormater(OutputFormater):
    @staticmethod
    def print_payment(payment: Employee):
        print(f'The amount to pay {payment.name} is {payment.payment}')


class InputProcessor(ABC):
    @abstractmethod
    def getData(self) -> list[WorkedWeek]:
        """Get the parsed list of the worked hours in a week"""
        pass


class FileInputReader(InputProcessor):
    def __init__(self, file_name):
        self.file_name = file_name

    @staticmethod
    def parse_day(day_code: str):
        if day_code == 'MO':
            return calendar.MONDAY
        elif day_code == 'TU':
            return calendar.TUESDAY
        elif day_code == 'WE':
            return calendar.WEDNESDAY
        elif day_code == 'TH':
            return calendar.THURSDAY
        elif day_code == 'FR':
            return calendar.FRIDAY
        elif day_code == 'SA':
            return calendar.SATURDAY
        elif day_code == 'SU':
            return calendar.SUNDAY
        else:
            raise('Bad day code')

    def _process_work(self, input_string: str) -> WorkedPeriod:
        day_code = input_string[0:2]
        day = FileInputReader.parse_day(day_code)
        period = input_string[2:]
        parsed_period = re.split(':|-', period)

        return WorkedPeriod(
            time(int(parsed_period[0]), int(parsed_period[1])),
            time(int(parsed_period[2]), int(parsed_period[3])),
            day
        )

    def getData(self) -> list[WorkedWeek]:
        with open(self.file_name, 'r') as f:
            res = []
            for line in f.readlines():
                # print(line)
                employee_name = line.split('=')[0]
                work = line.split('=')[1]
                week = []
                for w in work.split(','):
                    # print('Worked period:', w)
                    week.append(self._process_work(w))
                res.append(WorkedWeek(Employee(employee_name), week))
        return res


class Company:
    name: str
    rate_list: dict = {}

    def __init__(self, name: str, input_processor: InputProcessor, output_formater: OutputFormater):
        self.name = name
        self.input_processor = input_processor
        self.output_formater = output_formater

    def add_period(self, period: Period):
        if self.rate_list.get(period.day):
            self.rate_list[period.day].append(period)
        else:
            self.rate_list[period.day] = [period]

    def set_rates(self, rates: list[Period]):
        for r in rates:
            self.add_period(r)

    @classmethod
    def _get_intersection(cls, interval_a: tuple[time], interval_b: tuple[time]):
        intersection_end = None
        if interval_b[1] != time(0):
            if interval_a[0] > interval_b[1]:
                return 0
        else:
            intersection_end = interval_a[1]

        if interval_a[1] != time(0):
            if interval_b[0] > interval_a[1]:
                return 0
        else:
            intersection_end = interval_b[1]

        intersection_start = max(interval_a[0], interval_b[0])
        if not intersection_end:
            intersection_end = min(interval_a[1], interval_b[1])
        dummy_date = date(1, 1, 1)
        datetime_start = datetime.combine(dummy_date, intersection_start)
        datetime_end = datetime.combine(dummy_date, intersection_end)
        intersection = datetime_end - datetime_start
        return intersection.total_seconds()/3600

    def payment_calculator(self, work_week: WorkedWeek) -> Employee:
        pay = 0
        for wp in work_week.work:
            for p in self.rate_list[wp.day]:
                t = Company._get_intersection((wp.init_hour, wp.finish_time), (p.time_init, p.time_finish))
                pay = pay + Decimal(t) * p.rate
        employee = work_week.employee
        employee.payment = pay
        return employee

    def get_payments(self):
        week_work_list = input_processor.getData()
        res = []
        for ww in week_work_list:
            res.append(self.payment_calculator(ww))
        return res

    def print_payments(self):
        payments = self.get_payments()
        for p in payments:
            self.output_formater.print_payment(p)


def get_rates(rates_file: str) -> list[Period]:
    res = []
    with open(rates_file, 'r') as f:
        for line in f.readlines():
            fields = line.split(',')
            parsed_day = FileInputReader.parse_day(fields[0])
            parsed_period = re.split(':|-', fields[1])
            parsed_amount = Decimal(fields[2])
            res.append(
                Period(
                    parsed_day,
                    time(int(parsed_period[0]), int(parsed_period[1])),
                    time(int(parsed_period[2]), int(parsed_period[3])),
                    parsed_amount
                )
            )
    return res


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('You need to specify one input file')
        sys.exit(1)
    # Define output format
    output_formater = TextOutputFormater()

    # Define the source and how process the input data
    input_processor = FileInputReader(sys.argv[1])

    # Create the company
    c = Company('ACME', input_processor, output_formater)

    # Set payment rates for the company
    rates = get_rates('rates.txt')
    c.set_rates(rates)

    # Calculate and print the payment amount
    c.print_payments()
