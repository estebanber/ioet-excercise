from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, time, datetime
from decimal import Decimal
import calendar
import re
import sys
import os


@dataclass
class Employee:
    name: str
    payment: Decimal = 0


@dataclass
class Period:
    """Data class that contains information from the payment rate in one period and one day"""
    day: int
    time_init: time
    time_finish: time
    rate: Decimal


@dataclass
class WorkedPeriod:
    """Data class that contains information of a specific worked period"""
    init_hour: time
    finish_time: time
    day: int


@dataclass
class WorkedWeek:
    """Data class that contains information of whole worked week of an employee"""
    # year: int
    # calendar_week: int
    employee: Employee
    work: list[WorkedPeriod]

    def add_work(self, period: WorkedPeriod):
        self.work.append(period)


class Outputformatter(ABC):
    """Abstract class that define the interface to print output data"""
    @staticmethod
    @abstractmethod
    def print_payment(self, payment_list: Employee):
        pass


class TextOutputformatter(Outputformatter):
    """Implementation of Outputformatter that prints data as text in the system console"""
    @staticmethod
    def print_payment(payment: Employee):
        print(f'The amount to pay {payment.name} is {payment.payment}')


class InputProcessor(ABC):
    """Abstract class that define the interface to get input data"""
    @abstractmethod
    def getData(self) -> list[WorkedWeek]:
        """Get the parsed list of the worked hours in a week"""
        pass


class FileInputReader(InputProcessor):
    """Implementation of InputProcessor that gets data from text files"""

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
            print('Wrong day code')
            sys.exit(3)

    def _process_work(self, input_string: str) -> WorkedPeriod:
        """Parse data from each line to get the worked periods from an employee"""

        day_code = input_string[0:2]
        day = FileInputReader.parse_day(day_code)
        period = input_string[2:]
        parsed_period = re.split(':|-', period)
        try:
            return WorkedPeriod(
                time(int(parsed_period[0]), int(parsed_period[1])),
                time(int(parsed_period[2]), int(parsed_period[3])),
                day
            )
        except Exception:
            print('Parsing problem in input file, malformed line')
            sys.exit(3)

    @staticmethod
    def _check_line_format(line: str) -> bool:
        if '=' not in line:
            return True
        if ':' not in line:
            return True
        if '-' not in line:
            return True
        return False

    def getData(self) -> list[WorkedWeek]:
        """Obtain and parse worked hours of all employees in the text file"""

        with open(self.file_name, 'r') as f:
            res = []
            for line in f.readlines():
                if not line.strip():  # Ignore blank lines
                    continue
                if FileInputReader._check_line_format(line):  # Check the line format
                    print('Wrong input file format')
                    sys.exit(2)
                employee_name = line.split('=')[0]
                work = line.split('=')[1]
                week = []
                for w in work.split(','):
                    # print('Worked period:', w)
                    week.append(self._process_work(w))
                res.append(WorkedWeek(Employee(employee_name), week))
        return res


class Company:
    """Company class that calculates the employee's payments using multiple rates and hours worked"""
    name: str
    rate_list: dict = {}

    def __init__(
        self,
        name: str,
        input_processor: InputProcessor = None,
        output_formatter: Outputformatter = None
    ):
        self.name = name
        self.input_processor = input_processor
        self.output_formatter = output_formatter

    def add_period(self, period: Period):
        """Insert a new period rate to the company"""
        if self.rate_list.get(period.day):
            self.rate_list[period.day].append(period)
        else:
            self.rate_list[period.day] = [period]

    def set_rates(self, rates: list[Period]):
        """Add mulltiple pay rates in the company"""
        for r in rates:
            self.add_period(r)

    @staticmethod
    def _get_intersection(interval_a: tuple[time], interval_b: tuple[time]):
        """Get the intersection between to time intervals
           used to calculate the worked hours of each employee"""
        intersection_end = None
        if interval_b[1] != time(0):  # Fix for 0 hour interval end
            if interval_a[0] > interval_b[1]:
                return 0
        else:
            intersection_end = interval_a[1]

        if interval_a[1] != time(0):  # Fix for 0 hour interval end
            if interval_b[0] > interval_a[1]:
                return 0
        else:
            intersection_end = interval_b[1]

        intersection_start = max(interval_a[0], interval_b[0])
        if not intersection_end:
            intersection_end = min(interval_a[1], interval_b[1])
        dummy_date1 = dummy_date2 = date(1, 1, 1)
        if intersection_end == time(0):  # Fix for both 0 hour interval end
            dummy_date2 = date(1, 1, 2)

        datetime_start = datetime.combine(dummy_date1, intersection_start)
        datetime_end = datetime.combine(dummy_date2, intersection_end)
        intersection = datetime_end - datetime_start
        return intersection.total_seconds()/3600

    def payment_calculator(self, work_week: WorkedWeek) -> Employee:
        """Calculate the total amount to pay to an employee in a week"""
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
        """Print payments using the chosen formatter"""
        payments = self.get_payments()
        for p in payments:
            self.output_formatter.print_payment(p)


def get_rates(rates_file: str) -> list[Period]:
    """Function to parse the complete rate list of a company from a text file"""
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
    output_formatter = TextOutputformatter()

    # Define the source and how process the input data
    input_processor = FileInputReader(sys.argv[1])

    # Create the company
    c = Company('ACME', input_processor, output_formatter)

    # Set payment rates for the company
    script_path = os.path.dirname( __file__ ) 
    print(script_path)
    rates = get_rates(script_path+'/rates.txt')
    c.set_rates(rates)

    # Calculate and print the payment amount
    c.print_payments()
