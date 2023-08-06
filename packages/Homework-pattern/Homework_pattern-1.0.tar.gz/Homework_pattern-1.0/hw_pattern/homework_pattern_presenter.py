"""Действия пользователей

Attributes:
    database (dict): База пользователей
"""
from homework_pattern_model import User, Admin, Server_admin_user, Support_user, user_creator
from sys import getsizeof

database = {'user':[],'server_admin':[],
            'support':[],'admin':[]}

def admin_check(func):
    """Декоратор по проверке наличия прав администратора
    
    Args:
        func (func): действие администратора
    
    Returns:
        func: Действие которое может выполнить только администратор
    """
    def wrapper(user):
        if user.__dict__.get('is_admin'):
            return func(user)
        else:
            print('wrong user')
    return wrapper

# 
def login(auth_type='user'):
    """Вход пользователей
    
    Args:
        auth_type (str, optional): Тип пользователя
    
    Returns:
        obj: Пользователя согласно введенным данным
    """
    login = input('enter login: ')
    password = input('enter password: ')
    if database[auth_type]:
        for user in database[auth_type]:
            if user.check_login(login,password):
                return user
    else:
        print('неверный логин или пароль')
        return False        

# 
def registration(auth_type='user'):
    """Регистрация пользователей
    
    Args:
        auth_type (str, optional): Тип пользователя
    """
    user = user_creator(auth_type)()
    if user.login not in [user.login for user in database[auth_type]]:
        database[auth_type].append(user)
    else:
        print('Такой пользователь уже есть')
        

def user_action(user):
    """Действие пользователя
    
    Args:
        user (obj): Пользователь который вошел в систему
    """
    print(f'''
        USER action 1
        login is {user.login} 
        size is {getsizeof(user)}
        password is {user.password}''')
    # ---------- Тут что то будет ........

@admin_check
def admin_action(user):
    """Действия администратора"""
    choose_action = int(input('1-action1, 2-action2, 3-action3: '))
    action = dict(enumerate(['action 1', 'action 2','action 3'],1))
    print(f'''
        admin {action[choose_action]}
        {user.info()}''')