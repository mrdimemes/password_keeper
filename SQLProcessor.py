import datetime

import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode


class SQLProcessor():
    '''
    Class for interaction with MySQL server.
    
    '''
    def __init__(self, host_name, user_name, user_password, db_name):
        self.connect_to_database(host_name, user_name, user_password, db_name)   
        
        self.make_sql_query("SHOW tables")
        if len(self.get_output()) < 4:
            print('Some tables not found. Creating...')
            self.create_tables()
        
        self.check_security_policy()

            
    def connect_to_database(self, host_name, user_name, user_password, db_name):
        '''
        Connect and autorize at MySQL server via mysql.connector.
        Connection and cursor objects will saves as self atrubutes.
        
        See mysql.connector documentation for more info about args.
        The argument "host_name" is str type. It's host of your
        MySQL server;
        The argument "user_name" is str type. It's your login
        from MySQL server;
        The argument "user_password" is str type. It's your
        password from MySQL server;
        The argument "db_name" is str type. It's name of database
        used by this application.
        
        Incorrect host_name, user_name or user_password values
        will raise ValueError.
        
        '''
        try:
            self.connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password,
                database=db_name
            )
            self.cursor = self.connection.cursor()
            print("Connection to MySQL DB successful")
        except Error as e:
            if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise ValueError("Authentication error.")
            elif e.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database not found. Creating...")
                self.connection = mysql.connector.connect(
                    host=host_name,
                    user=user_name,
                    passwd=user_password,
                )
                self.cursor = self.connection.cursor()
                self.make_sql_query("CREATE DATABASE " + db_name)
                self.close_connection()
                self.connect_to_database(host_name, user_name, user_password, db_name)
            else:
                raise
    
    
    def close_connection(self):
        '''
        Disconnect from MySQL server.
        
        '''
        self.cursor.close()
        self.connection.close()

        
    def make_sql_query(self, query):
        '''
        Makes a request to MySQL server.
        The argument "query" is str type. It contain SQL command.
        
        '''
        self.cursor.execute(query)

        
    def get_output(self):
        '''
        Returns MySQL server response to the previous command.
        Works like mysql.connector.cursor.fetchall(), but
        does not throw an exception if the answer is empty
        (Returns an empty list instead).
        
        '''
        return [i for i in self.cursor]

    
    def create_tables(self):
        '''
        Сreates tables in database if they don't already exist.
        
        '''
        self.make_sql_query("SHOW tables")
        tables_list = self.get_output()
        
        if ("security_policy",) not in tables_list:
            self.make_sql_query(("CREATE TABLE security_policy ("
                                 "importance INT PRIMARY KEY, "
                                 "length INT NOT NULL, "
                                 "numbers BOOL NOT NULL, "
                                 "uppercase BOOL NOT NULL, "
                                 "characters BOOL NOT NULL, "
                                 "life INT NOT NULL, "
                                 "repeats BOOL NOT NULL)"))
            print("No security policy set.")
            self.set_security_policy()
            
        if ("services",) not in tables_list: 
            self.make_sql_query(("CREATE TABLE services ("
                                 "service_id INT AUTO_INCREMENT PRIMARY KEY, "
                                 "service_name VARCHAR(15) NOT NULL)"))
        
        if ("accounts",) not in tables_list: 
            self.make_sql_query(("CREATE TABLE accounts ("
                                 "account_id INT AUTO_INCREMENT PRIMARY KEY, "
                                 "service_id INT NOT NULL, "
                                 "login VARCHAR(25) NOT NULL, "
                                 "password VARCHAR(30) NOT NULL, "
                                 "upd_date DATE, "
                                 "importance INT NOT NULL, "
                                 "info VARCHAR(100), "
                                 "FOREIGN KEY (service_id) "
                                 "REFERENCES services (service_id), "
                                 "FOREIGN KEY (importance) "
                                 "REFERENCES security_policy (importance))"))
        
        if ("history",) not in tables_list: 
            self.make_sql_query(("CREATE TABLE history ("
                                 "change_id INT AUTO_INCREMENT PRIMARY KEY, "
                                 "account_id INT NOT NULL, "
                                 "password VARCHAR(30) NOT NULL, "
                                 "reset_date DATE NOT NULL, "
                                 "FOREIGN KEY (account_id) "
                                 "REFERENCES accounts (account_id))"))
        
        print("Tables were created successfully")

        
    def set_security_policy(self):
        '''
        Cleans security_policy table and runs one of
        configuration function by user choice.
        
        '''
        self.make_sql_query('SET FOREIGN_KEY_CHECKS = 0')
        self.make_sql_query('DELETE FROM security_policy')
        self.make_sql_query('SET FOREIGN_KEY_CHECKS = 1')
        print("Would you like to set security policy manually?")
        inp = input('Enter "YES" or skip to load default settings: ')
        if inp.lower() == 'yes':
            self.security_policy_manual_configuration()
        else:
            self.security_policy_default_configuration()
            
            
    def get_security_policy(self):
        '''
        Returns data from security_policy table.
        
        '''
        self.make_sql_query("SELECT * FROM security_policy")       
        return self.get_output()
    
            
    def security_policy_manual_configuration(self):
        '''
        Fills security_policy table with user-supplied values
        (Table needs to be empty).
        Do not stop program while configuration does not finished.
        
        '''
        print(("\nPLease, enter the requested values \n"
               "for passwords of different importance.\n" 
               "(3 - highest importance, 0 - lowest importance)"))
        for importance in range(4):
            print("\nNow confgurating importance {}.\n".format(importance))
            
            while True:
                length = input("Enter minimum password length (< 31): ")
                try:
                    length = int(length)
                    assert length in range(31)
                    break
                except:
                    print("Incorrect value. Try again")
                    
            while True:
                life = input("Enter password lifetime in months "
                             "(0 means unlimited lifetime): ")
                try:
                    life = int(life)
                    assert life >= 0
                    break
                except:
                    print("Incorrect value. Try again")
                    
            while True:
                numbers = input(("Password must contain numbers? "
                                 "If yes, enter 1, else 0: "))
                try:
                    numbers = int(numbers)
                    assert numbers in range(2)
                    break
                except:
                    print("Incorrect value. Try again")
                    
            while True:
                uppercase = input(("Password must contain uppercase letters? "
                                   "If yes, enter 1, else 0: "))
                try:
                    uppercase = int(uppercase)
                    assert uppercase in range(2)
                    break
                except:
                    print("Incorrect value. Try again")
                
            while True:
                characters = input(("Password must contain special characters? "
                                    "If yes, enter 1, else 0: "))
                try:
                    characters = int(characters)
                    assert characters in range(2)
                    break
                except:
                    print("Incorrect value. Try again")                
            
            while True:
                repeats = input(("Сan the same password be assigned twice "
                                 "for one account? "
                                 "If yes, enter 1, else 0: "))
                try:
                    repeats = int(repeats)
                    assert repeats in range(2)
                    break
                except:
                    print("Incorrect value. Try again")  
                    
            self.make_sql_query(('INSERT INTO security_policy VALUES '
                                 '({}, {}, {}, {}, {}, {}, {})'
                                ).format(importance, length, numbers,
                                         uppercase, characters, life, repeats))
            
        self.connection.commit()
        print("Security policy set successfully.")
    
    
    
    def security_policy_default_configuration(self):
        '''
        Fills security_policy table with default values
        (Table needs to be empty).
        Do not stop program while configuration does not finished.
        
        '''
        self.make_sql_query(('INSERT INTO security_policy VALUES '
                             '(3, 20, 1, 1, 0, 6, 0)'))
        self.make_sql_query(('INSERT INTO security_policy VALUES '
                             '(2, 15, 1, 1, 0, 12, 0)'))
        self.make_sql_query(('INSERT INTO security_policy VALUES '
                             '(1, 10, 1, 0, 0, 36, 1)'))
        self.make_sql_query(('INSERT INTO security_policy VALUES '
                             '(0, 0, 0, 0, 0, 0, 1)'))
        self.connection.commit()
        print("Security policy set successfully.")  
        
        
    def check_security_policy(self):
        '''
        Checks security_table. If some row is missing
        runs reset function.
        
        '''
        for i in range(4):
            self.make_sql_query(('SELECT * FROM security_policy '
                                 'WHERE importance = {}'.format(i)))
            
            if len(self.get_output()) == 0:
                print('Something wrong with security policy!')
                print('Repair initialization...')
                self.set_security_policy() 
                
        
    def add_account(self, service_name, login, password, 
                    upd_date='NULL', importance=2, info='NULL'):
        '''
        Adds new row in "accounts" table. Arguments are table wields.
        If accounts with same "service_name" and "login" values
        already in the table raise ValueError.
        
        The argument "service_name" is str type with max length = 15;
        The argument "login" is str type with max length = 25;
        The argument "password" is str type with max length = 30;
        The argument "upd_date" is str type in "YYYY-MM-DD" format;
        The argument "importance" is int = 0, 1, 2 or 3;
        The argument "info" is str type with max length = 100.
        
        '''
        try: 
            self.get_account(service_name, login)
        except ValueError:  # if account not found
            self.make_sql_query("SELECT service_name FROM services")

            if (service_name,) not in self.get_output():
                self.make_sql_query(('INSERT INTO services '
                                     'VALUES (NULL, "{}")').format(service_name))

            self.make_sql_query(('SELECT service_id FROM services ' 
                                 'WHERE service_name = "{}"').format(service_name))

            service_id = self.get_output()[0][0]

            if upd_date != "NULL":
                upd_date = '"{}"'.format(upd_date)

            if info != "NULL":
                info = '"{}"'.format(info)

            self.make_sql_query(('INSERT INTO accounts VALUES '
                                 '(NULL, "{}", "{}", "{}", {}, {}, {})'
                                ).format(service_id, login, password,
                                         upd_date, importance, info))
            self.connection.commit()
        else:
            raise ValueError('Account already exists.')
        
        
    def delete_account(self, service, login):
        '''
        Removes row from "accounts" table. Also removes following
        data from "history" table.
        If accounts with according "service_name" and "login" values
        does not exists in accounts table raise ValueError.
        
        The argument "service" is str type with max length = 15.
        It's accounts service name;
        The argument "login" is str type with max length = 25;
        
        '''
        self.get_account(service, login)
        
        self.make_sql_query(('DELETE FROM history '
                             'WHERE account_id = ('
                             'SELECT account_id FROM '
                             'accounts WHERE service_id = (' 
                             'SELECT service_id FROM '
                             'services WHERE service_name = '
                             '"{}") AND login="{}")'
                             ).format(service, login))
        
        self.make_sql_query(('DELETE FROM accounts '
                             'WHERE login = "{}" AND '
                             'service_id = (SELECT service_id FROM '
                             'services WHERE service_name = "{}")'
                             ).format(login, service))
        
        self.make_sql_query(('SELECT * FROM accounts '
                             'WHERE service_id = ( '
                             'SELECT service_id FROM services '
                             'WHERE service_name = "{}")'
                            ).format(service))
        
        if len(self.get_output()) == 0:
            self.make_sql_query(('DELETE FROM services '
                                 'WHERE service_name = "{}"'
                                ).format(service))
        
        self.connection.commit()
                
            
    def get_account(self, service_name, login):
        '''
        Returns tuple of account row in "accounts" table.
        If account with according "service_name" and "login" values
        does not exists raise ValueError.
        
        The argument "service_name" is str type with max length = 15;
        The argument "login" is str type with max length = 25;
         
        '''
        self.make_sql_query(('SELECT * FROM accounts '
                             'WHERE login = "{}" AND '
                             'service_id = (SELECT service_id '
                             'FROM services WHERE '
                             'service_name = "{}")'
                            ).format(login, service_name))
        account = self.get_output()
        if not account: raise ValueError("Account not found.")
        return account[0]
    
    
    def get_all_accounts(self):
        '''
        Returns list of tuples of all account rows in "accounts" table.
        Tuple also contain service name (index = 7).
        
        '''
        self.make_sql_query(("SELECT accounts.account_id, "
                             "accounts.service_id, accounts.login, "
                             "accounts.password, accounts.upd_date, "
                             "accounts.importance, accounts.info, "
                             "services.service_name "
                             "FROM accounts, services "
                             "WHERE accounts.service_id = "
                             "services.service_id"))
        return self.get_output()
    
    
    def get_account_history_list(self, account_id):
        '''
        Returns list of all old passwords of accaunt with id = "account_id".
        
        '''
        self.make_sql_query("SELECT password FROM history " 
                            "WHERE account_id = {}".format(account_id))
        history_list = [i[0] for i in self.get_output()]
        if not history_list:
            return None
        return history_list
        
            
    def print_full_table(self):
        '''
        Prints "account" table in extended format.
         
        '''
        self.make_sql_query(("SELECT services.service_name, accounts.login, "
                             "accounts.password, accounts.upd_date, "
                             "accounts.importance "
                             "FROM services, accounts "
                             "WHERE services.service_id = accounts.service_id"))
        print("{:<16}{:<26}{:<31}{:<11}{:<3}".format(
            "SERVICE", "LOGIN", "PASSWORD", "LASTUPD", "IMP"))
        for row in self.get_output():
            print("{:<16}{:<26}{:<31}{:<11}{:<3}".format(*list(map(str, row))))
            
            
    def export_full_table(self, file_path):
        '''
        Write "accounts" table in extended format into file.
        
        '''
        self.make_sql_query(("SELECT services.service_name, accounts.login, "
                             "accounts.password, accounts.upd_date, "
                             "accounts.importance "
                             "FROM services, accounts "
                             "WHERE services.service_id = accounts.service_id"))
        with open(file_path, "w") as file:
            file.write("{:<16}{:<26}{:<31}{:<11}{:<3}".format(
                "SERVICE", "LOGIN", "PASSWORD", "LASTUPD", "IMP") + "\n")
            for row in self.get_output():
                file.write("{:<16}{:<26}{:<31}{:<11}{:<3}".format(
                    *list(map(str, row))) + "\n")
            
            
    def print_cut_table(self):
        '''
        Prints "account" table in cut format.
         
        '''
        self.make_sql_query(("SELECT services.service_name, accounts.login, "
                             "accounts.password FROM services, accounts "
                             "WHERE services.service_id = accounts.service_id"))
        print("{:<16}{:<26}{:<31}".format(
            "SERVICE", "LOGIN", "PASSWORD"))
        for row in self.get_output():
            print("{:<16}{:<26}{:<31}".format(*list(map(str, row))))

            
    def export_cut_table(self, file_path):
        '''
        Write "accounts" table in cut format into file.
        
        '''
        self.make_sql_query(("SELECT services.service_name, accounts.login, "
                             "accounts.password FROM services, accounts "
                             "WHERE services.service_id = accounts.service_id"))
        with open(file_path, "w") as file:
            file.write("{:<16}{:<26}{:<31}".format(
                "SERVICE", "LOGIN", "PASSWORD") + "\n")
            for row in self.get_output():
                file.write("{:<16}{:<26}{:<31}".format(
                    *list(map(str, row))) + "\n")
                
                
    def print_secure_table(self):
        '''
        Prints "account" table in cut format with hidden passwords.
         
        '''
        self.make_sql_query(("SELECT services.service_name, accounts.login, "
                             "accounts.password FROM services, accounts "
                             "WHERE services.service_id = accounts.service_id"))
        print("{:<16}{:<26}{:<31}".format(
            "SERVICE", "LOGIN", "PASSWORD"))
        for row in self.get_output():
            service, login, password = list(map(str, row))
            password = ''.join(['*' for character in password])
            print("{:<16}{:<26}{:<31}".format(service, login, password))
    
    
    def print_security_policy_table(self):
        '''
        Prints "security_policy" table.
        
        '''
        self.make_sql_query("SELECT * FROM security_policy")       
        print("{:<4}{:<4}{:<4}{:<10}{:<5}{:<5}{:<8}".format(
            "IMP", "LEN", "NUM", "UPPERCASE", "CHAR", "LIFE", "REPEATS"))
        for row in self.get_output():
            print("{:<4}{:<4}{:<4}{:<10}{:<5}{:<5}{:<8}".format(
                *list(map(str, row))))
        
        
    def print_history_for_account(self, account_id):
        '''
        Prints password history for account with id = "account_id".
        
        '''
        self.make_sql_query(('SELECT password, reset_date '
                            'FROM history WHERE account_id = {}'
                            ).format(account_id))
        print("{:<30}{:<11}".format("PASSWORD", "RESET DATE"))
        for row in self.get_output():
            print("{:<30}{:<11}".format(*list(map(str, row))))
        

    def export_history_for_account(self, file_path, account_id):
        '''
        Exports password history for account with id = "account_id"
        into file.
        
        '''
        self.make_sql_query(('SELECT password, reset_date '
                            'FROM history WHERE account_id = {}'
                            ).format(account_id))
        with open(file_path, "w") as file:
            file.write("{:<30}{:<11}".format("PASSWORD", "RESET DATE") + "\n")
            for row in self.get_output():
                file.write("{:<30}{:<11}".format(*list(map(str, row))) + "\n")
            
            
    def change_password(self, service, login, new_password):
        '''
        Changes password for account and puts old password into
        "history" table.
        If account does not exists raise ValueError.
        
        The argument "service" is str type with max length = 15.
        It's account service name;
        The argument "login" is str type with max length = 25;
        The argument "new_password" is str type with max length = 30;
        
        '''
        account = self.get_account(service, login)
        
        old_password = account[3]
        account_id = account[0]
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        self.make_sql_query(('UPDATE accounts ' 
                             'SET password="{}", upd_date="{}" ' 
                             'WHERE login="{}" AND ' 
                             'service_id=(SELECT service_id '
                             'FROM services WHERE service_name="{}")'
                            ).format(new_password, today, login, service))
        
        self.make_sql_query(('INSERT INTO history VALUES ' 
                             '(NULL, {}, "{}", "{}")'
                            ).format(account_id, old_password, today))
        self.connection.commit()
