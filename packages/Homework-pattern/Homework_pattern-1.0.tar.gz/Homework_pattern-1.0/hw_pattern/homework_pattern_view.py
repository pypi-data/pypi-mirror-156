"""Меню пользователей

Attributes:
    menus (dict): Все возможные виды меню в зависимости от пользователей
    user_type (str): Тип пользователя
"""
from homework_pattern_presenter import login, registration, user_action, admin_action, admin_check

user_type = 'user'


def user_menu(user):
    """Меню пользователя
    
    Args:
        user (obj): Пользователь который вошел в систему
    """
    print('Hello You are user')
    while True:
        choice = input('1 user_action 2 exit: ')
        if choice == '1':
            user_action(user)
        if choice == '2':
            break


@admin_check
def admin_menu(user):
    """Меню администратора
    
    Args:
        user (obj): пользователь с правами администратора
    """
    print('Hello You are admin')
    while True:
        choice = input('1 admin_action 2 exit: ')
        if choice == '1':
            admin_action(user)
        if choice == '2':
            break


def support_menu(user):
    """Меню службы поддержки
    
    Args:
        user (obj): Пользователь службы поддержки
    """
    pass


def server_admin_menu(user):
    """Меню сисадмина
    
    Args:
        user (obj): Пользователь с правами сисадмина
    """
    pass

# 
menus = {'user':user_menu, 'admin':admin_menu, 'support':support_menu, 'server_admin': server_admin_menu}

def main_menu():
    """Меню входа и регистрации
    """
    global user_type
    while True:
        choice = input('1 - registration, 2 - login, 3 - exit: ')
        if choice == '3':
            break
        choose_type = input('1-admin, 2 -user, 3- support, 4 - server admin: ')
        types = {'1':'admin','2':'user','3':'support','4':'server_admin'}
        user_type = types.get(choose_type)
        if choice == '1':
            registration(user_type)
        if choice == '2':
            user = login(user_type)
            menus[user_type](user)
        

main_menu()
