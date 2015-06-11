# This script will automatically download transactions from Betterment.com
# for the user and accounts given. Credentials will be read from `keyring`
# by default, but if not installed will ask for them on the command line.

# important options should be supplied in the account_info.ini file.

import ConfigParser
from getpass import getpass
import sys
import mechanize


def read_config_section(fname, section):
    """
    Read a configuration file from the disk using ConfigParser.

    fname: str
      filename of configuration file for downloading

    Returns:
    --------
    dict1: dictionary
        dictionary containing configuration options
    """
    config = ConfigParser.ConfigParser()
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

user_dict = read_config_section('account_info.ini', 'UserInfo')
acc_dict = read_config_section('account_info.ini', 'AccountInfo')

# Get username and password either from the keyring, or from the user
try:
    import keyring
    user = user_dict['user']
    passwd = keyring.get_password(user_dict['keyring_name'], user)
    if passwd is None:
        raise ValueError("Password not found in keyring")
except ValueError, e:
    print(e)
    user = raw_input("Betterment username: ")
    passwd = getpass("Betterment password: ")
except ImportError, e:
    print(e)
    user = raw_input("Betterment username: ")
    passwd = getpass("Betterment password: ")

try:
    from twill.commands import go, fv, submit, save_html, show
except ImportError, e:
    print("Could not import twill library. "
          "Please check installation and try again")
    sys.exit(1)

# Login to betterment:
go('https://www.betterment.com/')
fv("2", "userName", user)
fv("2", "password", passwd)
submit('0')

# Get account group ID from config file and delete it
acc_group_id = acc_dict['account_group_id']
del acc_dict['account_group_id']

# Loop through the accounts defined in the config file,
# downloading and saving the csv file of transactions for each one
for account_name in acc_dict:
    account_number = acc_dict[account_name]

    # Download accounts:
    go("https://wwws.betterment.com/transactions.csv?accountGroupId=" +
       acc_group_id + "&account=" + account_number + "&startDaysAgo=" +
       user_dict['days'] + "&format=csv")
    save_html("transactions_" + account_name + ".csv")
    # show()

    print("Saved " + "transactions_" + account_name + ".csv")
