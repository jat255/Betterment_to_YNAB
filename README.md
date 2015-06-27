# Betterment_to_YNAB
Script to convert [Betterment](https://betterment.com)'s saved transactions 
to  a format understood by [YNAB](https://www.youneedabudget.com/).

Installation
------------
Written and tested using: 
 * Python 2.7.9 (auto downloading does not work with 3.4.3+) 
 ([link](https://www.python.org/downloads/))
 
 * Pandas 0.16.0 ([link] (http://pandas.pydata.org/))
 
 * Numpy 1.9.2 ([link](http://www.scipy.org/scipylib/download.html))
 
 * *optional -* Keyring 5.3 ([link] (https://pypi.python.org/pypi/keyring))
 
 * *optional -* Requests 2.7.0 ([link] 
                (http://docs.python-requests.org/en/latest/))
 
 * *optional -* Twill 0.9 ([link] (http://twill.idyll.org/))
    * Note, for some reason this is not working with the most recent version
     of twill (1.8.0), so stick with 0.9. Also, this does not work with python3, unfortunately

Make sure the above are installed, then simply clone (or download) this
repository to a local directory.

Usage
-----
 
To setup automatic downloading:
 
 2. First, you need to save your login information to your system keyring so
  the script will be able to log you in. This script does not save any login
  information on its own, but instead places it in the system's keyring, so it is as 
  secure as your computer's local account. You will need to run the script 
  `save_login.py` on each computer you wish to run the automated downloading
  on. If you don't do this, the script will ask for your username and 
  password each time it is run, since it is not saved.
 
 3. Then, configure the `account_info.ini` file to match the values for 
  your account. Under the `[UserInfo]` section, the only values that should 
  need changing are the user and the default days (prior to today) of transactions 
  that you wish to download. Under the `[AccountInfo]` section, you need to 
  add your account group ID and your account numbers. This information can 
  be found by visiting the [activity page] 
  (https://wwws.betterment.com/app/#activity) of your Betterment account, 
  and hovering over the "Download Activity as CSV" link. In this link, you 
  will see the values `accountGroupID=` and `account=`. The GroupID should 
  be the same for all accounts, but each account you have will have a 
  different number. In the example `account_info.ini` file, I have two 
  accounts (Wealth building and Roth IRA), so I have listed them there. The 
  names you give them (`wb` and `roth`) don't matter, as the script will 
  loop through all the accounts you put in this section and try to download 
  their activity. The supplied names will be used in the outputted .csv files.
 
To use the actual script:

 2. Run `python betterment_to_ynab.py` to see all the options available.
 
 3. To download transactions, supply the `-d` flag to the script. To convert
 transactions, use the `-c` flag. To automate both processes, you can combine the
 options and supply them as `-dc`.
 
 4. Other options are available, such as a custom number of days to download (`--days`),
 the days after which to convert transactions (`--daysafter`), the names of files to convert
 (`-f` or `--filenames`), and the text output of the script (use `-v` to see more output).
 
 5. Import the resulting CSV files into YNAB and confirm that transactions look
 correct

Note:
 
 * Because deposits, contributions, withdrawals, etc. to Betterment accounts
   are usually classified as transfers within YNAB from another account,
   they are supposed to be ignored by this import script (or else you'll
   end up with duplicates). The transactions to ignore can be included  (one
   per line) in an ignore list named `convert_ignore.txt`, which is
   provided  when downloading the repository locally.
   

Examples
--------

* To save your login information to the system keyring:

        python save_login.py -u <username> -p <password>
     
* To automatically download and convert transactions (after 
  `account_info.ini` is configured), showing output:

        python betterment_to_ynab.py -dcv
 
* To (just) download transactions from 25 days ago until now
  (not showing any output):
  
        python betterment_to_ynab.py -d --days 25
        
* To (just) convert files named `file1.csv` and `file2.csv`,
  discarding any transactions before June 12, 2015:
  
        python betterment_to_ynab.py -c -f file1.csv file2.csv --dateafter 2015-06-12
 
 
 
Troubleshooting
---------------
I have been successfully using this script for a while, and haven't had any
issues with it. Check the following if you are having issues:
 
 * `Pandas` and `Numpy` installed
 
 * `convert_ignore.txt` matches the format of the version included  with the
   code
 
Help!
-----
File an issue on [github](https://github.com/jat255/Betterment_to_YNAB/issues)
so I can try to help.

Contributions
-------------
Suggestions or actual contributions are more than welcome. The easiest way
is to fork this repository and add a pull request so I can review the
changes easily.
