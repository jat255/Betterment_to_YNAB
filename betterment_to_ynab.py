#!/usr/bin/env python

# TODO: Add arguments to choose which function to use from main function

# import needed utilities
import pandas as pd
from time import time
from datetime import date, datetime, timedelta
from selenium import webdriver
from time import sleep
import tempfile
import shutil
import os
import platform

try:
    # Python 2 import
    import ConfigParser as cp
except:
    # Python 3 import
    import configparser as cp

from getpass import getpass
import sys
import argparse

if sys.version_info[0] >= 3:
    raw_input = input

print_out = False



def log(output):
    """
    Helper function to print output if flag is set
    """
    if print_out:
        print(output)


def convert_betterment_to_ynab(dateafter='earliest',
                               filenames=None,
                               print_output=False
                               ):
    """
    Convert a csv file downloaded from Betterment to YNAB format

    Parameters
    ----------
    dateafter: 'earliest', date str, or None
        Date before which to filter out transactions
        If 'earliest', all transactions will be included.
        If None, the user will be asked for a date interactively.
        If providing as a str, must be in the format 'YYYY-MM-DD'
    filenames: str, list of str, or None
        Name of file containing downloaded transactions (CSV file)
        If None, the user will be asked for a filename interactively.
    print_output: boolean
        switch to control whether output about the conversion is printed
        for the user
    """
    global print_out
    print_out = print_output

    if dateafter is None:
        # date after which to save the transactions
        dateafter = str(raw_input("Date from which to save transactions "
                                  "(YYYY-MM-DD)? "
                                  "[Default: 1 week ago] "))
        if dateafter is "":
            dateafter = (date.today() - timedelta(days=7)).isoformat()

    if filenames is None:
        # default filename to read from is transactions.csv
        filenames = [str(raw_input("Filename to read transactions from? "
                                  "[Default: transactions.csv] "))]
        if filenames is "":
            filenames = ['transactions.csv']

    # If filename is just one string, convert it to single-item list
    if isinstance(filenames, str):
        filenames = [filenames]

    # Loop through filename list and convert them
    for f in filenames:
        # Read in the data from Betterment
        df = pd.read_csv(f,
                         sep=',',
                         header=0,)

        df = df[pd.notnull(df['Ending Balance'])]

        # Run converters to clean up the data

        # As of Jan 2016, $ characters are no longer included, so don't need
        #  to do this anymore...
        # df['Amount'] = df.apply(lambda row: float(row['Amount'].replace(
        # '$',  '')),
        #                         axis=1)
        # df['Ending Balance'] = df.apply(lambda row:
        #                                 float(row['Ending Balance'].replace(
        #                                       '$', '')),
        #                                 axis=1)

        # Remove the time zone information from the Date column
        df['Date Completed'] = df['Date Completed'].map(lambda x: x[:-6])

        # Create needed columns and rename existing ones
        s_length = len(df['Amount'])
        df.rename(columns={'Transaction Description':'Payee'}, inplace=True)
        df['Inflow'] = pd.Series([0] * s_length, index=df.index)
        df['Outflow'] = pd.Series([0] * s_length, index=df.index)

        df['Memo'] = ''
        df['Category'] = ''

        # Convert timestamps to datetime
        df['Date Completed'] = pd.to_datetime(df['Date Completed'],
                                              format='%Y-%m-%d %H:%M:%S')

        # Create new column for date output
        df['Date'] = df['Date Completed'].apply(lambda x:
                                                x.strftime('%m/%d/%Y'))

        # Figure data for inflows and outflows:
        df['Outflow'] = df.apply(lambda row: (-1 * row['Amount']
                                              if row['Amount'] <= 0 else 0),
                                 axis=1)
        df['Inflow'] = df.apply(lambda row: (row['Amount']
                                             if row['Amount'] > 0 else 0),
                                axis=1)

        if dateafter != 'earliest':
            # Mask the dataframe by date (so we're only showing  new
            # transactions)
            df_masked = df[(df['Date Completed'] > dateafter)]
        else:
            df_masked = df

        # Find locations of automatic deposits so they aren't printed
        # Add lines to convert_ignore.txt for any types of
        # transactions you wish to ignore
        with open("convert_ignore.txt", "r") as ignore_file:
            names = ignore_file.readlines()

        ignore_list = [n[:-1] for n in names[1:]]

        idx = df_masked['Payee'].isin(ignore_list)

        res = df_masked.loc[~idx,['Date','Payee','Category','Memo',
                                  'Outflow', 'Inflow']]

        log("")
        log(res)

        res.to_csv(f[:-4] + '_YNAB.csv',
                   sep=',',
                   index=False,
                   )

        os.remove(f)
        log("\nSaved results to " + f[:-4] + '_YNAB.csv')


def read_config_section(fname, section):
    """
    Read a configuration file from the disk using ConfigParser.

    Parameters
    ----------
    fname: str
        filename of configuration file for downloading
    section: str
        section to read from

    Returns
    -------
    dict1: dictionary
        dictionary containing configuration options


    """
    config = cp.ConfigParser()
    config.read(fname)

    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None

    return dict1


def download_trans(print_output=False,
                   days_ago=None):
    """
    Download transactions according to configuration file
    'account_info.ini', using saved keyring credentials (if available). If
    not, user will be asked for username and password

    Parameters
    ----------
    print_output: boolean
        switch to control whether or not information is printed to the console
    days_ago: int or None
        number of days back for which to download transactions.
        If None, will be read from configuration file

    Returns
    -------
    files: list of str
        list of file names that were downloaded
    """
    global print_out
    print_out = print_output
    files = []

    user_dict = read_config_section('account_info.ini', 'UserInfo')
    acc_dict = read_config_section('account_info.ini', 'AccountInfo')
    dir_dict = read_config_section('account_info.ini', 'Directory')

    # Figure out number of days
    if days_ago is None:
        days_ago = str(user_dict['days'])

    # generate proper date strings
    end_d = date.today()
    end_s = end_d.strftime("%Y-%m-%d")
    dt = timedelta(days=int(days_ago))
    start_d = end_d - dt
    start_s = start_d.strftime("%Y-%m-%d")

    # Get username and password either from the keyring, or from the user
    try:
        import keyring
        user = user_dict['user']
        passwd = keyring.get_password(user_dict['keyring_name'], user)
        if passwd is None:
            raise ValueError("Password not found in keyring")
    except ValueError as e:
        print(e)
        user = raw_input("Betterment username: ")
        passwd = getpass("Betterment password: ")
    except ImportError as e:
        print(e)
        user = raw_input("Betterment username: ")
        passwd = getpass("Betterment password: ")

    # Create temp dir and firefox profile
    tmpdir = tempfile.mkdtemp()
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting",
                           False)
    profile.set_preference("browser.download.dir", tmpdir)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "text/csv")
    driver = webdriver.Firefox(firefox_profile=profile)

    # Login to betterment:
    driver.get('https://wwws.betterment.com/app/login')
    wd_login = driver.find_elements_by_id('web_authentication_email')[0]
    wd_passwd = driver.find_elements_by_id('web_authentication_password')[0]
    wd_login.clear()
    wd_passwd.clear()
    wd_login.send_keys(user)
    wd_passwd.send_keys(passwd)
    button = driver.find_element_by_name('commit')
    button.click()

    # wait for page load:
    while driver.current_url != 'https://wwws.betterment.com/app/#summary':
        sleep(0.5)
    sleep(5)

    # Download transactions and move files to directory in account_info.ini
    for account_name in acc_dict:
        account_number = acc_dict[account_name]

        filter_text = '&activity_filter%5Btransaction_type_categories%5D%5B%5D'
        dl_link = 'https://wwws.betterment.com/app/activity_transactions.csv' \
                  '?activity_filter%5Bend_on%5D=' + end_s + \
                  '&activity_filter%5Bstart_on%5D=' + start_s + \
                  '&activity_filter%5Bsub_account_id%5D=' + account_number + \
                  filter_text + '=deposits' + \
                  filter_text + '=withdrawals' + \
                  filter_text + '=dividends' + \
                  filter_text + '=tax_loss_harvests' + \
                  filter_text + '=allocation_changes' + \
                  filter_text + '=fees' + \
                  filter_text + '=other' + \
                  filter_text + '=market_changes'

        driver.get(dl_link)
        log('Downloading from: ' + dl_link)
        fname = os.path.join(tmpdir, 'transactions.csv')
        if platform.system() == 'Windows':
            directory = dir_dict['win_dir']
        elif platform.system() == 'Linux':
            directory = dir_dict['linux_dir']
        else:
            directory = '~'

        new_fname = os.path.join(directory,
                                 'transactions_{}.csv'.format(account_name))
        shutil.move(fname, new_fname)

        log("\nSaved " + fname + '\n')
        files.append(new_fname)

    driver.close()
    shutil.rmtree(tmpdir)

    return files


def dl_convert(print_output=False,
               days_ago=None):
    """
    Helper function to call the two methods above that do the
    downloading and converting.
    See those methods for parameter definitions.
    """
    files = download_trans(print_output=print_output,
                           days_ago=days_ago)

    convert_betterment_to_ynab(filenames=files,
                               print_output=print_output)


def main():
    parser = argparse.ArgumentParser(description='Script to download and  '
                                                 'convert transactions '
                                                 'from Betterment for  '
                                                 'import into YNAB. To '
                                                 'download and convert '
                                                 '(showing output), use '
                                                 'the options \'-dcv\'.')
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='verbose flag to show more output on command '
                             'line')
    parser.add_argument('-d', '--download',
                        action='store_true',
                        help='use this flag to control if transactions are '
                             'downloaded')
    parser.add_argument('-c', '--convert',
                        action='store_true',
                        help='use this flag to control if transactions are '
                             'converted')
    parser.add_argument('-f', '--filenames',
                        action='store',
                        nargs='+',
                        help='names of files to convert, separated by spaces')
    parser.add_argument('--days',
                        action='store',
                        help='number of days of history to download from '
                             'Betterment')
    parser.add_argument('--dateafter',
                        action='store',
                        help='date after which to save transactions (when '
                             'converting). '
                             'Must be in format YYYY-MM-DD. '
                             'Default is all transactions are saved.')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()

    if args.dateafter is None:
        # Set default conversion time as all days that were downloaded
        args.dateafter = 'earliest'

    if args.download and not args.convert:
        # Just downloading transactions
        download_trans(print_output=args.verbose,
                       days_ago=args.days)
    elif not args.download and args.convert:
        # Just converting transactions
        convert_betterment_to_ynab(print_output=args.verbose,
                                   filenames=args.filenames,
                                   dateafter=args.dateafter)
    elif args.download and args.convert:
        # Download and convert:
        dl_convert(print_output=args.verbose,
                   days_ago=args.days)


if __name__ == "__main__":
    main()
