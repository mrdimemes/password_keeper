import datetime

import getpass
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
import numpy as np
import pyperclip

from SQLProcessor import SQLProcessor
from PasswordOperator import PasswordOperator


HOST_NAME = 'localhost'
DB_NAME = 'pswd_keeper_db'


class PasswordKeeper():
    '''
    Main class of application.
    Implements the user interface.
    
    '''
    main_menu_msg = ("1. Accounts\n"
                     "2. Security\n"
                     "3. Passwords\n"
                     "0. Log out\n")
        
    accounts_menu_msg = ("1. View your accounts\n" 
                         "2. Add new account\n" 
                         "3. Remove account\n"
                         "4. Change password\n"
                         "5. Copy password to clipboard\n"
                         "6. View password history\n"
                         "7. Export\n"
                         "0. Back\n")
        
    security_menu_msg = ("1. View security policy\n"
                         "2. Change security policy\n"
                         "3. Check passwords\n"
                         "4. Change bad passwords\n"
                         "5. Clear clipboard\n"
                         "6. Backup\n"
                         "0. Back\n")
       
    passwords_menu_msg = ("1. Generate password\n" 
                               "0. Back\n")

    
    def __init__(self):
        print("PasswordKeeper on duty! Please, autorize at your MySQL server\n")
        
        while True:
            user_name = input("user:     ")
            user_password = getpass.getpass("password: ")
            print()
            try:
                self.sql_processor = SQLProcessor(HOST_NAME, user_name,
                                                 user_password, DB_NAME)
                break
            except ValueError as e:
                print(e, '\n')
            
        self.password_operator = PasswordOperator(
            self.sql_processor.get_security_policy())
        
        self.main_menu()
        

    def main_menu(self):
        while True:
            print()
            print(self.main_menu_msg)
            cmd = input(">> ")
            if cmd == "1": self.accounts_menu()
            elif cmd == "2": self.security_menu()
            elif cmd == "3": self.passwords_menu()
            elif cmd == "0": self.logout()
    
    
    def accounts_menu(self):
        while True:
            print()
            print(self.accounts_menu_msg)
            cmd = input(">> ")
            if cmd == "1": self.cmd_view_accounts()
            elif cmd == "2": self.cmd_add_account()
            elif cmd == "3": self.cmd_remove_account()
            elif cmd == "4": self.cmd_change_password()
            elif cmd == "5": self.cmd_account_password_to_clipboard()
            elif cmd == "6": self.cmd_view_history()
            elif cmd == "7": self.cmd_export()
            elif cmd == "0": break
    
    
    def security_menu(self):
        while True:
            print()
            print(self.security_menu_msg)
            cmd = input(">> ")
            if cmd == "1": self.cmd_view_security_policy()
            elif cmd == "2": self.cmd_change_security_policy()
            elif cmd == "3": self.cmd_check_passwords()
            elif cmd == "4": self.cmd_change_bad_passwords()
            elif cmd == "5": self.cmd_clear_clipboard()
            elif cmd == "6": self.cmd_backup()
            elif cmd == "0": break
    
    
    def passwords_menu(self):
        while True:
            print()
            print(self.passwords_menu_msg)
            cmd = input(">> ")
            if cmd == "1": self.cmd_generate_password()
            elif cmd == "0": break
    
    
    def logout(self):
        self.sql_processor.close_connection()
        print("\nPlease, autorize at your MySQL server\n")
        while True:
            user_name = input("user:     ")
            user_password = getpass.getpass(prompt="password: ")
            print()
            try:
                self.sql_processor.connect_to_database(
                    HOST_NAME, user_name, user_password, DB_NAME)
                break
            except ValueError as e:
                print(e, '\n')
            
    
    def cmd_view_accounts(self):
        while True:
            print()
            print(("1. View cut table\n" 
                   "2. View full table\n"
                   "3. View in secure mode\n"
                   "0. Back\n"))
            cmd = input(">> ")
            print()
            if cmd == "1":
                self.sql_processor.print_cut_table()
                input()
                break
            elif cmd == "2":
                self.sql_processor.print_full_table()
                input()
                break
            elif cmd == "3":
                self.sql_processor.print_secure_table()
                input()
                break
            elif cmd == "0": break
    
    
    def cmd_add_account(self):
        print("\nTo cancel skip the \"service\" or \"login\" field\n")
        
        while True:
            service_name = input("service:     ").lower()
            if not service_name: return
            if len(service_name) > 15:
                print("Input is too long.")
            else:
                break
                
        while True:
            login = input("login:       ")
            if not login: return
            if len(login) > 25:
                print("Input is too long.")
            else:
                break 
        
        while True:
            password = getpass.getpass("password:    ")
            if len(password) > 30:
                print("Input is too long.")
            else:
                break
                
        while True:
            importance = input("importance:  ")
            if not importance: 
                importance = 2
                break
            if importance in ("0", "1", "2", "3"):
                importance = int(importance)
                break
            else:
                print("Value must be 0, 1, 2, 3 or None.")
                
        while True:
            upd_date = input("update date: ")
            if not upd_date: 
                upd_date = "NULL"
                break
            try:
                datetime.datetime.strptime(upd_date, "%Y-%m-%d")
                break
            except ValueError:
                print("Use YYYY-MM-DD format")
            
        info = input("info:        ")
        if not info: info = "NULL"
        
        try:
            self.sql_processor.add_account(service_name, login,
                                           password, upd_date, 
                                           importance, info)
        except ValueError as e:
            print(e)

        
    def cmd_remove_account(self):
        print("\nTo cancel skip the any field\n")
        while True:
            service_name = input("service: ").lower()
            if not service_name: return

            login = input("login:   ")
            if not login: return

            try:
                self.sql_processor.delete_account(service_name, login)
                break
            except ValueError as e:
                print(e)
        print("Account has been deleted.")
            
    
    def cmd_change_password(self, account=None):
        if account is None:
            account = self.get_account()
            if account is None: return
        
        importance = account[5]
        account_id = account[0]
        login = account[2]
        service_name = account[7]
        password_history = self.sql_processor.get_account_history_list(
            account_id)
        upd_date = account[4]
        
        while True:
            print("\nHow do you want change your password?\n")
            print(("1. Manually input\n" 
                   "2. Autogenerate\n"))
            cmd = input(">> ")
            
            if cmd == "1":
                while True:
                    new_password = input("new password: ")
                    if self.password_operator.check_password_by_policy(
                        new_password, importance, upd_date, password_history):
                        break
                    print("Bad password.")
                break
                
            elif cmd == "2":
                new_password = self.password_operator.generate_password_by_policy(
                    importance)
                print("\nyour password is: {}".format(new_password))
                print("Copy it in clipboard? \n")
                print(("1. Yes\n" 
                       "(or skip this for \"No\")\n"))
                if input(">> ") == "1":
                    pyperclip.copy(new_password)
                break
        
        self.sql_processor.change_password(service_name, login, 
                                           new_password)
        print("The password has been changed.")
    
    
    def cmd_view_history(self):
        account = self.get_account()
        if account is None: return
        account_id = account[0]
        print()
        self.sql_processor.print_history_for_account(account_id)
        input()
        
    
    def cmd_account_password_to_clipboard(self):
        account = self.get_account()
        if account is None: return
        pyperclip.copy(account[3])
        print("The password has been copied to the clipboard.")
        
    
    def cmd_export(self):
        while True:
            print()
            print(("1. Export full table\n"
                   "2. Export cut table\n"
                   "3. Export history for account\n"
                   "0. Back\n"))
            cmd = input(">> ")
            
            if cmd == "0": return
            
            print("\nPlease, enter file path\n")
            file_path = input(">> ")
            
            try:
                if cmd == "1": 
                    self.sql_processor.export_full_table(file_path)
                elif cmd == "2":
                    self.sql_processor.export_cut_table(file_path)
                elif cmd == "3":
                    account = self.get_account()
                    if account is None: return
                    account_id = account[0]
                    self.sql_processor.export_history_for_account(
                        file_path, account_id)
                print("Data has been written to the file.")
                return
            except FileNotFoundError as e:
                print(e)
                
    
    def cmd_view_security_policy(self): 
        print()
        self.sql_processor.print_security_policy_table()
        input()
            
            
    def cmd_change_security_policy(self):
        print()
        print("The current security policy will be removed!")
        while True:
            print(("1. Continue configuration\n"
                   "0. Back\n"))
            cmd = input(">> ")
            if cmd == "1": 
                self.sql_processor.set_security_policy()
                break
            elif cmd == "0": return
    
    
    def cmd_check_passwords(self):
        bad_pass_accounts = self.get_accounts_with_bad_password()
        print(("\nThere are {} accounts with bad passwords in the database\n"
              ).format(len(bad_pass_accounts)))
        print("{:<16}{:26}".format("SERVICE", "LOGIN"))
        for account in bad_pass_accounts:
            service_name = account[7]
            login = account[2]
            print("{:<16}{:26}".format(service_name, login))
        input()
        
    
    def cmd_change_bad_passwords(self):
        bad_pass_accounts = self.get_accounts_with_bad_password()
        print(("\nThere are {} accounts with bad passwords in the database\n"
              ).format(len(bad_pass_accounts)))
        for account in bad_pass_accounts:
            service_name = account[7]
            login = account[2]
            print("Processed account is: {} - {}\n".format(service_name, login))
            self.cmd_change_password(account)
        print("Now all passwords are good C:")
    
    def cmd_clear_clipboard(self):
        pyperclip.copy("")
        pyperclip.copy("")
        pyperclip.copy("")
        print("The clipboard has been cleared.")
    
    def cmd_backup(self):
        print("Command not avaiable")

    def cmd_generate_password(self):
        print()
        print("\nTo cancel skip the \"length\"\n")
        
        while True:
            length = input("length:          ")
            try:
                if not length: return
                length = int(length)
                assert length in range(31)
                break
            except:
                print("Incorrect value (need int < 31)")
            
        while True:
            numbers = input("numbers flag:    ")
            try:
                numbers = int(numbers)
                assert numbers in range(2)
                break
            except:
                print("Incorrect value (need 0 or 1)")
                
        while True:
            uppercase = input("uppercase flag:  ")
            try:
                uppercase = int(uppercase)
                assert uppercase in range(2)
                break
            except:
                print("Incorrect value (need 0 or 1)")
                
        while True:
            characters = input("characters flag: ")
            try:
                characters = int(characters)
                assert characters in range(2)
                break
            except:
                print("Incorrect value (need 0 or 1)")
                
        try:              
            password = self.password_operator.generate_password(
                length, numbers, uppercase, characters)
            print("\nyour password is: {}".format(password))
            print("Copy it in clipboard? \n")
            print(("1. Yes\n" 
                   "(or skip this for \"No\")\n"))
            if input(">> ") == "1":
                pyperclip.copy(password)
        except ValueError as e:
            print(e)
    
    
    def get_account(self):
        print("\nTo cancel skip the \"service\" or \"login\" field\n")
        while True:
            service_name = input("service:      ").lower()
            if not service_name: return

            login = input("login:        ")
            if not login: return
            
            try:
                account = self.sql_processor.get_account(
                    service_name, login)
                account = list(account)
                account.append(service_name)
                return account
            except ValueError as e:
                print(e)
                
                
    def get_accounts_with_bad_password(self):
        accounts = self.sql_processor.get_all_accounts()
        bad_pass_accounts = []
        
        for account in accounts:
            account_id = account[0]
            password = account[3]
            importance = account[5]
            upd_date = account[4]
            password_history = self.sql_processor.get_account_history_list(
                account_id)
            
            if not self.password_operator.check_password_by_policy(
                password, importance, upd_date, password_history):
                bad_pass_accounts.append(account)
                
        return bad_pass_accounts
        

if __name__ == "__main__":
    password_keeper = PasswordKeeper()
