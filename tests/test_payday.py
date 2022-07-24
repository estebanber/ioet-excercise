# import pytest
from payday.payday import Period, Company, WorkedWeek, WorkedPeriod, Employee, FileInputReader
from datetime import time
import calendar
from decimal import Decimal


def test_get_intersection():
    period_a = (time(0, 0), time(3, 0))
    period_b = (time(2, 0), time(5, 0))
    intersection_1 = Company._get_intersection(period_a, period_b)
    assert intersection_1 == 1

    period_a = (time(15, 0), time(20, 0))
    period_b = (time(18, 0), time(0, 0))
    intersection_1 = Company._get_intersection(period_a, period_b)
    assert intersection_1 == 2

    period_a = (time(5, 0), time(8, 0))
    period_b = (time(9, 0), time(20, 0))
    intersection_1 = Company._get_intersection(period_a, period_b)
    assert intersection_1 == 0

    period_a = (time(15, 0), time(15, 30))
    period_b = (time(12, 0), time(20, 0))
    intersection_1 = Company._get_intersection(period_a, period_b)
    assert intersection_1 == 0.5

    period_a = (time(20, 0), time(0, 0))
    period_b = (time(18, 0), time(0, 0))
    intersection_1 = Company._get_intersection(period_a, period_b)
    assert intersection_1 == 4


def test_payment_Calculator():
    wp1 = WorkedPeriod(time(0), time(2), calendar.MONDAY)
    ww = WorkedWeek(Employee("ESTEBAN"), [wp1])
    c = Company("ACME")
    c.add_period(Period(calendar.MONDAY, time(0), time(9), Decimal('25')))
    employee = c.payment_calculator(ww)
    assert employee.name == 'ESTEBAN'
    assert employee.payment == 50

    wp2 = WorkedPeriod(time(23), time(0), calendar.MONDAY)
    ww.add_work(wp2)
    employee = c.payment_calculator(ww)
    assert employee.name == 'ESTEBAN'
    assert employee.payment == 50

    c.add_period(Period(calendar.MONDAY, time(9), time(0), Decimal('30')))
    employee = c.payment_calculator(ww)
    assert employee.name == 'ESTEBAN'
    assert employee.payment == 80

    c.add_period(Period(calendar.TUESDAY, time(0), time(9), Decimal('5.5')))
    c.add_period(Period(calendar.TUESDAY, time(9), time(18), Decimal('10.2')))
    c.add_period(Period(calendar.TUESDAY, time(18), time(0), Decimal('20.8')))
    wp3 = WorkedPeriod(time(15), time(18), calendar.TUESDAY)  # 3*10.2
    wp4 = WorkedPeriod(time(5), time(8), calendar.TUESDAY)  # 3*5.5
    ww.add_work(wp3)
    ww.add_work(wp4)
    employee = c.payment_calculator(ww)
    assert employee.name == 'ESTEBAN'
    payment = Decimal('80') + 3*Decimal('10.2') + 3*Decimal('5.5')
    assert employee.payment == payment


def test_FileInputProcessor():
    input_processor = FileInputReader('tests/test_input.txt')
    wp1 = WorkedPeriod(time(10), time(12), calendar.MONDAY)
    wp2 = WorkedPeriod(time(10), time(12), calendar.TUESDAY)
    wp3 = WorkedPeriod(time(1), time(3), calendar.THURSDAY)
    wp4 = WorkedPeriod(time(14), time(18), calendar.SATURDAY)
    wp5 = WorkedPeriod(time(20), time(21), calendar.SUNDAY)
    ww = WorkedWeek(Employee("RENE"), [wp1, wp2, wp3, wp4, wp5])
    read_ww = input_processor.getData()
    assert [ww] == read_ww

