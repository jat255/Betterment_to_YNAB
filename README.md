# Betterment_to_YNAB
Script to convert [Betterment](https://betterment.com)'s saved transactions to a format understood by [YNAB](https://www.youneedabudget.com/).

Installation
------------
Written and tested using: 
 * Python 2.7.9 (should also work with 3.4.3+) ([link](https://www.python.org/downloads/))
 * Pandas 0.16.0 ([link] (http://pandas.pydata.org/))
 * Numpy 1.9.2 ([link](http://www.scipy.org/scipylib/download.html))

Make sure the above are installed, then simply clone (or download) this repository to a local directory.

Usage
-----
 
To use:
 1. Download transactions from Betterment.com and save to same directory as script
 2. Run `python betterment_to_ynab.py`
 3. Enter date you wish to go back to for saving transactions (usually the day after whatever the last entry in YNAB was)
 4. Enter the filename of the downloaded CSV file, or press enter to accept the default.
 5. Import the resulting CSV into YNAB and confirm that transactions look correct
 
Note:
 * Because deposits, contributions, withdrawals, etc. to Betterment accounts are usually classified as 
   transfers within YNAB from another account,  they are supposed to be ignored by this import script (or else you'll end up with duplicates). 
   The transactions to ignore can be included (one per line) in an ignore list named `convert_ignore.txt`, which
   is provided when downloading the repository locally.
 
Troubleshooting
---------------
I have been successfully using this script for a while, and haven't had any issues with it. Check the following if you are having issues:
 * `Pandas` and `Numpy` installed
 * `convert_ignore.txt` matches the format of the version included with the code
 
Help!
-----
File an issue on [github](https://github.com/jat255/Betterment_to_YNAB/issues) so I can try to help.

Contributions
-------------
Suggestions or actual contributions are more than welcome. The easiest way is to fork this repository and add a pull request so I can review the changes easily.
