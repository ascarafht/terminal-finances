#!/usr/bin/python3

import os
import csv
import datetime
import calendar
import re
from argparse import ArgumentParser

import pandas as pd

from ExactCalc.ExactFloat import ExactFloat

FILE_PATH =  os.path.expanduser('~/Documents/finances/finance.csv')

CSV_FIELDS = ['Name', 'Category', 'Essential', 'Date', 'Total']
CATEGORY_CHOICES = ['Housing', 'Food', 'Transport', 'Taxes', 'Donations', 'Insurance', 'Savings/Investments', 'Health', 'Services', 'Personal', 'Recreation', 'Debts', 'Incomes']
DATE_FORMAT = "%d/%m/%Y"

def create_file():
    '''Create files in PATH and create directories if they doesn't exist'''
    if not os.path.exists(FILE_PATH):
        os.makedirs(os.path.dirname(FILE_PATH), exist_ok=True)
        with open(FILE_PATH, 'w') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(CSV_FIELDS)

class Bill:
    def __init__(self, name, category, essential, entry_date, total):
        if name == None:
            raise ValueError('Name not defined.')
        if category == None:
            raise ValueError('Category not defined.')
        if entry_date == None:
            raise ValueError('Date not defined.')
        if total == None:
            raise ValueError('Total not defined.')
        if not (category in CATEGORY_CHOICES):
            raise ValueError('Category not valid.')
        self.name = name
        self.category = category
        self.essential = essential
        split_date = entry_date.split('/')
        self.entry_date = datetime.date(int(split_date[2]), int(split_date[1]), int(split_date[0]))
        self.total = ExactFloat(total)

    def to_dict(self):
        return {
            'Name': self.name,
            'Category': self.category,
            'Essential': self.essential,
            'Date': self.entry_date,
            'Total': str(self.total)
        }

    def __str__(self):
        return f'{self.name}\t{self.category}\t{self.essential}\t{self.entry_date.strftime(DATE_FORMAT)}\t{self.total}'

def validate_range(str_value):
    '''Check if entry data for date or total is in correct format and return the value(s) and comparision symbol(s), if not return False.'''
    value_components =[value for value in re.split(r'([=><~]+)', str_value) if value != '']
    if len(value_components) == 1:
        value = value_components[0]
        return [value]
    elif len(value_components) == 2:
        value = value_components[1]
        evaluation = value_components[0]
        if evaluation == '<=' or evaluation == '>=' or evaluation == '<' or evaluation == '>':
            return value, evaluation
        else:
            return False
    else:
        value1 = value_components[0]
        value2 = value_components[2]
        evaluation = value_components[1]
        if evaluation =='~':
            return value1, value2, evaluation
        else:
            return False

def get_range_month(str_date):
    '''Get date for first day and last day of corresponding month/year, return (first_date, last_date)'''
    month, year = str_date.split('/')
    first_date = datetime.date(int(year), int(month), 1)
    last_date = datetime.date(first_date.year, first_date.month, calendar.monthrange(first_date.year, first_date.month)[1])
    return first_date.strftime(DATE_FORMAT), last_date.strftime(DATE_FORMAT)

def get_date_filter(str_date, table):
    '''Filter date in pandas DataFrame, return DataFrame or raise an Error'''
    values = validate_range(str_date)
    if values:
        if len(values) == 1:
            '''For evaluate ='''
            date_value_str = values[0].split('/')
            date_value = datetime.date(int(date_value_str[2]), int(date_value_str[1]), int(date_value_str[0]))
            return table[table['Date'] == str(date_value)]
        elif len(values) == 2:
            '''For evaluate >, <, >= or <='''
            date_value_str = values[0].split('/')
            date_value = datetime.date(int(date_value_str[2]), int(date_value_str[1]), int(date_value_str[0]))
            evaluation = values[1]
            if evaluation == '>':
                return table[table['Date'] > str(date_value)]
            elif evaluation == '>=':
                return table[table['Date'] >= str(date_value)]
            elif evaluation == '<':
                return table[table['Date'] < str(date_value)]
            elif evaluation == '<=':
                return table[table['Date'] <= str(date_value)]
            else:
                raise ValueError('Date filter in wrong format.')
        else:
            '''for evaluate a range'''
            evaluation = values[2]
            date_value_str1 = values[0].split('/')
            date_value_str2 = values[1].split('/')
            date_value1 = datetime.date(int(date_value_str1[2]), int(date_value_str1[1]), int(date_value_str1[0]))
            date_value2 = datetime.date(int(date_value_str2[2]), int(date_value_str2[1]), int(date_value_str2[0]))

            if evaluation == '~':
                return table[(table['Date'] >= str(date_value1)) & (table['Date'] <= str(date_value2))]
            else:
                raise ValueError('Date filter in wrong format.')
    else:
        raise ValueError('Date filter in wrong format.')

def get_total_filter(str_total, table):
    '''Filter total in pandas DataFrame, return DataFrame or raise an Error'''
    values = validate_range(str_total)
    if values:
        if len(values) == 1:
            '''For evaluate ='''
            total_value = values[0]
            return table[table['Total'].astype(float) == float(total_value)]
        elif len(values) == 2:
            '''For evaluate >, <, >= or <='''
            total_value = values[0]
            evaluation = values[1]
            if evaluation == '>':
                return table[table['Total'].astype(float) > float(total_value)]
            elif evaluation == '>=':
                return table[table['Total'].astype(float) >= float(total_value)]
            elif evaluation == '<':
                return table[table['Total'].astype(float) < float(total_value)]
            elif evaluation == '<=':
                return table[table['Total'].astype(float) <= float(total_value)]
            else:
                raise ValueError('Total filter in wrong format.')
        else:
            '''for evaluate a range'''
            total_value1 = values[0]
            total_value2 = values[1]
            evaluation = values[2]
            if evaluation == '~':
                return table[(table['Total'].astype(float) >= float(total_value1)) & (table['Total'].astype(float) <= float(total_value2))]
            else:
                raise ValueError('Total filter in wrong format.')
    else:
        raise ValueError('Total filter in wrong format.')

def filter_table(**kwargs):
    '''Filter pandas DataFrame by Name, Category, Essential, Date and/or Total, return DataFrame'''
    name = kwargs['name'] if 'name' in kwargs.keys() else None
    category = kwargs['category'] if 'category' in kwargs.keys() else None
    essential = kwargs['essential'] if 'essential' in kwargs.keys() else None
    date =  kwargs['date'] if 'date' in kwargs.keys() else None
    total = kwargs['total'] if 'total' in kwargs.keys() else None
    finance_table = pd.read_csv(FILE_PATH, sep='\t', header=0)
    '''Make column Date into date type'''
    finance_table['Date'] = pd.to_datetime(finance_table['Date'])
    if name != None:
        finance_table = finance_table[finance_table['Name'].str.contains(name)]
    if category != None:
        finance_table = finance_table[finance_table['Category'] == category]
    if essential != None:
        finance_table = finance_table[finance_table['Essential'] == essential]
    if date != None:
        finance_table = get_date_filter(date, finance_table)
    if total != None:
        finance_table = get_total_filter(total, finance_table)
    finance_table = finance_table.sort_values(by='Date')
    finance_table['Date'] = finance_table['Date'].dt.strftime(DATE_FORMAT)
    return finance_table

def create_bill_dummy(**kwargs):
    name = kwargs['name'] if 'name' in kwargs.keys() else None
    category = kwargs['category'] if 'category' in kwargs.keys() else None
    essential = kwargs['essential'] if 'essential' in kwargs.keys() else None
    date =  kwargs['date'] if 'date' in kwargs.keys() else None
    total = kwargs['total'] if 'total' in kwargs.keys() else None
    return Bill(name, category, essential, date, total)

def add_bill(**kwargs):
    '''Add bill to csv file and return added bill as Bill object. entry_bill must be [name, category, essential, date, total]'''
    bill = create_bill_dummy(**kwargs)
    with open(FILE_PATH, 'a') as file:
        writer = csv.DictWriter(file, CSV_FIELDS, delimiter='\t')
        writer.writerow(bill.to_dict())
    return bill

def delete_bill(**kwargs):
    '''Remove bill from csv fil end return deleted bill as Bill object. exit_bill must be [name, category, essential, date, total] '''
    bill = create_bill_dummy(**kwargs)
    with open(FILE_PATH, 'r') as file:
        table = [row for row in csv.DictReader(file, CSV_FIELDS, delimiter='\t') if (row['Name'] != bill.name) or (row['Category'] != bill.category) or (row['Essential'] != bill.essential) or (row['Date'] != str(bill.entry_date)) or (row['Total'] != str(bill.total)) ]
    with open(FILE_PATH, 'w') as file:
        writer = csv.DictWriter(file, CSV_FIELDS, delimiter='\t')
        writer.writerows(table)
    return bill

def get_report(**kwargs):
    '''Get month DataFrame. Return DataFrame and sum of total DataFrame column'''
    category = kwargs['category'] if 'category' in kwargs.keys() else None
    date =  kwargs['date'] if 'date' in kwargs.keys() else None
    if date != None:
        date1, date2 = get_range_month(date)
        finance_table = filter_table(category=category, date=f'{date1}~{date2}')
        total_list = [ExactFloat(str(total)) for total in finance_table['Total'].to_list()]
        total = ExactFloat('0')
        for value in total_list:
            total =total + value
        return finance_table, total
    else:
        raise ValueError('Total filter in wrong format.')

parser = ArgumentParser(
    prog='finances',
    description='Manage personal finances.'
)
parser.add_argument('--add', '-a',action='store_true', required=False, help=f'Add bill. Needs to defiend NAME CATEGORY ESSENTIAL DATE TOTAL commands.')
parser.add_argument('--delete', '-d', action='store_true', required=False, help='Delete bill. Needs to defiend NAME CATEGORY ESSENTIAL DATE TOTAL commands.')
parser.add_argument('--show', '-s', action='store_true', required=False, help='Show all table.')
parser.add_argument('--name', '-N', required=False, help='Filter for --show , bills whose name contain the argument.')
parser.add_argument('--category', '-C', required=False, help=f'Filter for --show, bills whose category contain the argument. It must be one of those options {CATEGORY_CHOICES}.')
parser.add_argument('--essential', '-E', required=False, help='Filter for --show, bills whose essential value is the argument.')
parser.add_argument('--date', '-D', required=False, help='Filter for --show, bills whose date value is the argument. For dates in a range of greater than (>), greater or equal than (>=), smaller than (<), smaller or equal than (<=), adds its corresponding symbol at the start of the date as delimeters, and for a range between two dates, place the first date, then the symbol (~), and at the end the second date. Example 12/10/2021 for equal, >=12/10/2021 for grater or equal than, 12/10/2021~14/10/2021, for between the range.')
parser.add_argument('--total', '-T', required=False, help='Filter for --show, bills whose total value is the argument. For total in a range of greater than (>), greater or equal than (>=), smaller than (<), smaller or equal than (<=), adds its corresponding symbol at the start of the quantity as delimeters, and for a range between two quantities, place the first quantity, then the symbol (~), and at the end the second quantity. Example 120.00 for equal, >=120.00 for grater or equal than, 120.00~150.00 for between the range.')
parser.add_argument('--report', '-r', action='store_true', required=False, help='Shows month report. Needs DATE argument, CATEGORY argument is optional.')
parser.add_argument('--export', '-e', nargs=1, required=False, help='Exports report as .csv to given path. Needs DATE argument, CATEGORY argument is optional.')
args = parser.parse_args()


create_file()

if args.delete:
    bill = delete_bill(name=args.name, category=args.category, essential=args.essential, date=args.date, total=args.total)
    finance_table=filter_table(name=bill.name, category=bill.category, essential=bill.essential, date=bill.entry_date.strftime(DATE_FORMAT), total=str(bill.total))
    print(finance_table)
    print('Deleted:', bill.to_dict())
elif args.add:
    bill = add_bill(name=args.name, category=args.category, essential=args.essential, date=args.date, total=args.total)
    finance_table=filter_table(name=bill.name, category=bill.category, essential=bill.essential, date=bill.entry_date.strftime(DATE_FORMAT), total=str(bill.total))
    print(finance_table)
elif args.show:
    finance_table = filter_table(name=args.name, category=args.category, essential=args.essential, date=args.date, total=args.total)
    print(finance_table)
elif args.report:
    finance_table, total = get_report(category=args.category, date=args.date)
    print(finance_table)
    print(f'Total report: {total}')
elif args.export:
    path = args.export[0]
    finance_table, total = get_report(category=args.category, date=args.date)
    category = f'_{args.category}'
    if args.category == None:
        category = ''
    if path[-1] != '/':
        path = f'{path}/'
    month, year = args.date.split('/')
    finance_table['Date'] = pd.to_datetime(finance_table['Date'], format='%d/%m/%Y')
    finance_table['Date'] = finance_table['Date'].dt.strftime('%Y-%m-%d')
    finance_table.to_csv(f'{path}finance_report{category}_{month}-{year}.csv', sep='\t', index=False)
else:
    print('Error: Command failure')