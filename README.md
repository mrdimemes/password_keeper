# Password Keeper
Hello there. It's simple console application based on MySQL BDMS.
## Functional
* Storing passwords for accounts of various services
* Adding and removing accounts to the database
* Password generating
* Storing security policy
* Configurating security policy
   * Manual
   * Loading from preset 
* Changing passwords of existing accounts from the database
   * Manual
   * Auto (by security policy)
* Checking stored passwords
* Storing password history for any account
* Printing table of stored accounts into console
   * In simple format
   * In extended format (with more info)
   * With hidden passwords
* Printing password history for account into console
* Exporting table of stored accounts to file 
   * In simple format
   * In extended format
* Exporting password history for account to file
* Copying password for specified account into clipboad
* Clearing clipboard
## Requirements
* **Python 3.8+**
* **MySQL server**
* **getpass** library
* **mysql.connector** module
* **numpy** library
* **pyperclip** library
## Modules
* **run_application.py** - executable file, contain PasswordKeeper class and his initialization code
* **PasswordOperator.py** - contain PasswordOperator class
* **SQLProcessor.py** - contain SQLProcessor class
