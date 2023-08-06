class User:

    """Описание пользователей 
    
    Attributes:
        login (str): Description
        password (str): Description
    """
    
    def __init__(self):
        """Инициализация данных для входа в систему
        """
        self.login = input('login:')
        self.password = input('password:')
    def check_login(self,login,password):
        """Вход в систему
        
        Args:
            login (str): имя пользователя
            password (str): пароль
        
        Returns:
            bool: Вошли или не вошли в систему
        """
        if self.login == login and self.password == password:
            return True
        else:
            return False
    

class Admin(User):

    """Пользователь с правами администратора
    
    Attributes:
        is_admin (bool): добавление прав администратора
    """
    
    def __init__(self):
        """Инициализация прав администратора
        """
        super().__init__()
        self.is_admin = True
    def info(self):
        """Информация о администраторе
        
        Returns:
            dict: Словарь с инфо о пользователе
        """
        return self.__dict__

class Support_user(User):

    """Пользователь с правами поддержки
    
    Attributes:
        is_support_user (bool): добавление прав поддержки
    """
    
    def __init__(self):
        """Инициализация прав службы поддержки
        """
        super().__init__()
        self.is_support_user =True

class Server_admin_user(User):

    """Пользователь с правами сисадмина
    
    Attributes:
        is_server_admin_user (bool): добавление прав сисадмина
    """
    
    def __init__(self):
        """Инициализация прав сисадмина
        """
        super().__init__()
        self.is_server_admin_user =True


user_types = {'admin':Admin, 'support':Support_user,
            'server_admin':Server_admin_user, 'user':User}


def user_creator(user_type='user'):
    """Создание пользователя согласно его типу
    
    Args:
        user_type (str, optional): Тип пользователя
    
    Returns:
        cls: Класс пользователя с определенными правами
    """
    return user_types[user_type]

