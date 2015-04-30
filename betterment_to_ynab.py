#!/usr/bin/env python

# import needed utilities
import pandas as pd
from time import time
from datetime import date, datetime, timedelta
import numpy as np

import sys
if sys.version_info[0] >= 3:
    raw_input = input

# date after which to save the transactions
dateafter = str(raw_input("Date from which to save transactions (YYYY-MM-DD)? [Default: 1 week ago] "))

if dateafter is "":
    dateafter = (date.today() - timedelta(days=7)).isoformat()

# default filename to read from is transactions.csv
filename = str(raw_input("Filename to read transactions from? [Default: transactions.csv] "))

if filename is "":
    filename = 'transactions.csv'

# Read in the data from Betterment
df = pd.read_csv(filename,
                 sep=',',
                 header=0,
                )

df = df[pd.notnull(df['Ending Balance'])]


# Run converters to clean up the data
df['Amount'] = df.apply(lambda row: float(row['Amount'].replace('$', '')), axis=1)
df['Ending Balance'] = df.apply(lambda row: float(row['Ending Balance'].replace('$', '')), axis=1)
# df['Date Completed'] = df.apply(lambda row: str(row['Date Completed'].split('.')[0]))


# Create needed columns and rename existing ones
sLength = len(df['Amount'])
df.rename(columns={'Transaction Description':'Payee'}, inplace=True)
df['Inflow'] = pd.Series(np.zeros(sLength), index=df.index)
df['Outflow'] = pd.Series(np.zeros(sLength), index=df.index)
df['Memo'] = ''
df['Category'] = ''

# Convert timestamps to datetime
df['Date Completed'] = pd.to_datetime(df['Date Completed'], format='%Y-%m-%d %H:%M:%S.%f')

# Create new column for date output
df['Date'] = df['Date Completed'].apply(lambda x: x.strftime('%m/%d/%Y'))

# Figure data for inflows and outflows:
df['Outflow'] = df.apply(lambda row: (-1 * row['Amount']
                                               if row['Amount'] <= 0
                                               else 0),
                                   axis=1)
df['Inflow'] = df.apply(lambda row: (row['Amount']
                                               if row['Amount'] > 0
                                               else 0),
                                   axis=1)

# Mask the dataframe by date (so we're only showing new transactions)
df_masked = df[(df['Date Completed'] > dateafter)]

# Find locations of automatic deposits so they aren't printed
# Add lines to convert_ignore.txt for any types of transactions you wish to ignore
with open("convert_ignore.txt", "r") as f:
    names = f.readlines()

ignore_list = [n[:-1] for n in names[1:]]

print(ignore_list)

idx = df_masked['Payee'].isin(ignore_list)

res = df_masked.loc[~idx,['Date','Payee','Category','Memo','Outflow','Inflow']]

print(res)

res.to_csv(filename[:-4] + '_YNAB.csv',
           sep=',',
           index=False,
           )

print("\nSaved results to " + filename[:-4] + '_YNAB.csv')