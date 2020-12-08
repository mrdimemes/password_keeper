import datetime

import numpy as np


class PasswordOperator():
    '''
    Class for generating passwords.
    
    '''

    def __init__(self, security_policy):
        self.set_security_policy(security_policy)
    
    
    def set_security_policy(self, security_policy):
        '''
        Copies security policy to self.security_policy dict attribute.
        This is necessary in order not to overload the code with 
        SQL-requests.
        
        The argument "security_policy" is the contents of 
        the "security policy" table 
        (SQLProcessor.get_security_policy() output).
        
        '''
        self.security_policy = dict()
        for (importance, length, numbers, uppercase, characters, 
             life, repeats) in security_policy:
            self.security_policy[importance] = {
                'length': length,
                'numbers': numbers,
                'uppercase': uppercase,
                'characters': characters,
                'life': life,
                'repeats': repeats
            }
            
            
    def generate_password_by_policy(self, importance):
        '''
        Generates and returns a password string in accordance 
        with security policy requirements.
        
        The argument "importance" is int = 0, 1, 2 or 3.
        It's importance of account from "accounts" table.
        
        '''
        policy = self.security_policy[importance]
        return self.generate_password(**policy)
    
    
    def generate_password(self, length=20, numbers=True, 
                          uppercase=True, characters=False, **args):
        '''
        Generates and returns a password string in accordance 
        with argument requirements.
        
        The argument "length" is int type. It's length of new password;
        The argument "numbers" is bool type 
        (or other, but used as bool). If True new password will
        contain numbers;
        The argument "uppercase" is bool type. If True new password 
        will contain uppercase letters;        
        The argument "characters" is bool type. If True new password 
        will contain special characters;
        **args are not used. Needed for generate_password_by_policy().
        
        If number of True bool arguments < argument "length"
        raise ValueError.
        
        '''
        min_length = numbers + uppercase + characters + 1
        
        # correction for accounts with zero minimum password length
        if length == 0: length += 10
            
        if length < min_length:
            raise ValueError(
                "The password is too short for the specified flags.")

        abc = [i for i in range(97, 123)]

        if numbers:
            abc.extend([i for i in range(48, 58)])

        if uppercase:
            abc.extend([i for i in range(65, 91)])

        if characters:
            abc.extend([i for i in range(33, 48)])
            abc.extend([i for i in range(91, 97)])
            abc.extend([i for i in range(123, 127)])

        while True:
            password = np.random.choice(abc, length)
            
            # checking against arguments
            if self.check_password(password, numbers, uppercase, characters):
                return ''.join([chr(i) for i in password])
                
                
    def check_password_by_policy(self, password, importance, 
                                 upd_date=None, history_list=None):
        '''
        Checking password in accordance with 
        security policy requirements.
        Returns True if password is nice, else False.
        
        The argument "password" is string of your password;
        The argument "importance" is int = 0, 1, 2 or 3.
        It's importance of account from "accounts" table;
        The argument "upd_date" is datetime.date object or None.
        It's date of password last update;
        The argument "history_list" is list type or None.
        It's list of all passwords that was stored for this account. 
        
        '''
        
        policy = self.security_policy[importance]
        
        if len(password) < policy['length']:
            return False
        
        if (not upd_date is None) and policy['life'] != 0:
            lifetime = datetime.timedelta(30 * policy['life'])
            today = datetime.datetime.now()
            upd_date = datetime.datetime.combine(upd_date, 
                datetime.datetime.min.time())
            if (today - upd_date) > lifetime:
                return False
            
        if (not history_list is None) and (not policy['repeats']):
            if password in history_list:
                return False
        
        password = [ord(i) for i in password]
        return self.check_password(password, **policy)
        

    def check_password(self, password, numbers=True,
                       uppercase=True, characters=False, **args):
        '''
        Checking password in accordance with argument requirements.
        Returns True if password is nice, else False.

        The argument "numbers" is bool type 
        (or other, but used as bool). If True password must
        contain numbers;
        The argument "uppercase" is bool type. If True password 
        must contain uppercase letters;        
        The argument "characters" is bool type. If True password 
        must contain special characters;
        **args are not used. Needed for check_password_by_policy().
        
        '''
        for c in password:
            if c >= 97 and c <= 122:
                break
        else:
            return False

        if numbers:
            for c in password:
                if c >= 48 and c <= 57:
                    break
            else:
                return False

        if uppercase:
            for c in password:
                if c >= 65 and c <= 90:
                    break
            else:
                return False

        if characters:
            for c in password:
                if ((c >= 33 and c <= 47) or
                    (c >= 91 and c <= 96) or
                    (c >= 123 and c <= 126)):
                    break
            else:
                return False

        return True
