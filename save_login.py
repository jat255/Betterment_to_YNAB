# This script will take two command line parameters and save the login
# information provided to the system keyring. Should work on Gnome, KDE,
# Windows, OS X, and any other system supported by `keyring`

# run with the command `python save_login.py -u <username> -p <password>
# in order to save your login information securely to the system keyring
# It is probably best practice to put both your username and password in
# quotation marks when you supply them to the script.

import sys
import getopt
import keyring


def usage():
    print(sys.argv[0] + " -u <username> -p <password>")
    sys.exit(2)


def main():
    user = None
    passwd = None

    options, arg = getopt.getopt(sys.argv[1:], 'hu:p:', ['help',
                                                         'user=',
                                                         'pass=',])
    if len(options) is 0:
        usage()

    for opt, arg in options:
        if opt in ('-h', '--help'):
            usage()
        elif opt in ('-u', '--user'):
            user = arg
        elif opt in ('-p', '--pass'):
            passwd = arg

    if user is not None and passwd is not None:
        keyring.set_password('betterment_to_ynab',
                             user,
                             passwd)
        print('Saved login information to system keyring under '
              'the name \"betterment_to_ynab\".')

    else:
        print("Both username and password must be provided:")
        usage()

if __name__ == "__main__":
    main()
