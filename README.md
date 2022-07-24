# IOET Excersice: Payday

## Run aplication
´´´bash
python payday/payday.py [file]
´´´
Example:
´´´bash
python payday/payday.py work.txt
´´´

## Run tests
´´´bash
python -m pytest -v
´´´

## Architecture
The Company class is main structure in the solution. An instance of this class
contains the rate list for diferent periods and days of the week and use
this information to calculate the total pay amount to each employee.
This data is introduced with the "add_period" and the "set_rates" methods

The table with the amount to pay according to the time of the day and the day
of the week is stored in a text file (rates.txt) and is readed with the
"get_rates" function

The worked hours data is introduce to the company class using an "InputProcessor"
in this case the implementation of this abstract class (FileInputProcessor)
reads a plain text file with the specified format for each employee work week.

The output is formated through an "Outputformatter". In this case the implementation 
prints the data in the system console 

Using this composition method allows the program to be extended with multiple
ways of introducing the input data (employees worked hours) and multiples way to deliver the 
results

Other dataclasses (Employee, Period, WorkedWeek, etc.) are created  in order to
structure the data in the best possible way
