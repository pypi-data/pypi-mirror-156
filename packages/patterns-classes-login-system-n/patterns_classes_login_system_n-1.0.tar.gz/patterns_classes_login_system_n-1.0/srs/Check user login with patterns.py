import copy
import json

class User:

    def __init__(self):
        self.choice_user_type = str(input('1:admin_user/2:user/3:server_admin_users/4:support_users'))
        self.login = str(input("Input your login !!!or if not in our list - you will be added!!!"))          #check login or registration new at list
        self.password = str(input("Input your password !!!or if not in our list - you will be added!!!"))    #check password or registration new at lis
        self.get_login()
              
    def get_login(self):     

        file_content = json.load(open("C:/Users/m.shevchuk/Desktop/Авторизация.json","r"))
        log_dic_help = {'1': 'admin_users', '2':'users', '3': 'server_admin_users','4': 'support_users'}
        check = log_dic_help[self.choice_user_type]                                                          # select category user dict                                    
        users = file_content[check].keys()                                                                   # chek all logins(keys) from users category                                
        
        if self.login in users and self.password == file_content[check].get(self.login):                     #Login part 1
            print(f"hello {self.login}")
            self.login = True

            if self.choice_user_type == '2':                                                                 # if user is user - user action 
                def user_action():
                    print('USER action 1')
                    return self.login, self.password                                                         # Для получения логина
                                                                                                             # Для получения password 
                user_action()

        elif self.login not in users:
            file_content[check].update({self.login:self.password})                                           #Registration part 2       
            print(file_content)
            with open("C:/Users/m.shevchuk/Desktop/Авторизация.json","w") as file:
                file.write(json.dumps(file_content))
        else:                                                                                                #error login part 3
            print("wrong login or password")   
        
class Admin(User):
    def __init__(self):
        super().__init__()
        
        if self.login == True: 
            print("hello admin")
            self.admin_menu()  
            copy.deepcopy(self)

    def admin_menu(self):

        def admin_action1():
            print("Admin_action1")
            return User

        def admin_action2():
            print("Admin_action2")
            return User
   
        def admin_action3():
            print("Admin_action3")
            return User

        actions_dict = {'1': admin_action1, '2': admin_action2, '3': admin_action3}
        choice_action = str(input("Choice wahat you want : 1/2/3"))
        return  actions_dict[choice_action]()
    
class Support_user(User):
    pass

class Server_admin_user(User):
    pass

def func_login():      
    choice_user_type = str(input('1:admin_user/2:user/3:server_admin_users/4:support_users'))
    user_types = {'1': Admin, '2': User, '3': Support_user, '4': Server_admin_user}
    user_types = user_types[choice_user_type]()
    
print(User)
func_login()