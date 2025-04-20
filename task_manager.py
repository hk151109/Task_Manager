import pandas as pd
import re
from datetime import datetime
import smtplib

df_users = pd.read_csv("./users.csv")
df_task_manager = pd.read_csv("./task_manager.csv")


def user_login(df_users, df_task_manager):
    print("Welcome to Task manager! To get started please enter your email ID")
    user_email = input("Email ID : ").strip()
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    while re.match(email_regex, user_email) == None:
        print("Sorry the email ID is incorrect. Please try again")
        user_email = input("Email ID : ").strip()
    if len(df_users.index) == 0:
        user_name = input("Enter your name :").strip()
        user_name_stored = user_name
        user_password = input("Enter your password : ").strip()
        user_dict = {
            "user_email" : user_email,
            "user_password" : user_password,
            "user_name" : user_name 
        }
        df_users = pd.concat([df_users, pd.DataFrame([user_dict])], ignore_index=True)
        df_users.to_csv("./users.csv", index=False)
        print("You are now a registered user")
    elif len(df_users.index) != 0 and user_email not in list(df_users['user_email']):
        user_name = input("Enter your name : ").strip()
        user_name_stored = user_name
        user_password = input("Enter your password : ").strip()
        user_dict = {
            "user_email" : user_email,
            "user_password" : user_password,
            "user_name" : user_name 
        }
        df_users = pd.concat([df_users, pd.DataFrame([user_dict])], ignore_index=True)
        df_users.to_csv("./users.csv", index=False)
        print("You are now a registered user")
    else:
        user_password_stored = df_users.loc[df_users['user_email'] == user_email, 'user_password'].iloc[0]
        user_name_stored = df_users.loc[df_users['user_email'] == user_email, 'user_name'].iloc[0]
        user_password = input("Enter your password to authenticate : ").strip()
        while user_password != user_password_stored:
            print("Sorry this is not the right password. Please try again.")
            user_password = input("Enter your password to authenticate : ").strip()
        print("Hello {0}. Welcome back to task manager".format(user_name_stored))
    task_manager(df_users, df_task_manager, user_email, user_name_stored)
        
def task_manager(df_users, df_task_manager, user_email, user_name):
    while True:
        print("""Select an option from the below list and type the number against it as an input.
        1 - Add a task
        2 - Delete a task
        3 - Modify a task
        4 - View my tasks
        5 - Email my tasks
        6 - Exit
        """)
        user_input = int(input("Enter you selection here : ").strip())
        if user_input == 1:
            print("Please enter the following task details")
            task_name = input("Enter the task name : ").strip()
            # task_start_date = datetime.strptime(input("Enter the task start date in YYYY-MM-DD format : ").strip(), '%Y-%m-%d')
            # task_start_time = datetime.strptime(input("Enter the task start time in HH:MM format : ").strip(), '%H:%M')
            # task_end_date = datetime.strptime(input("Enter the task end date in YYYY-MM-DD format : ").strip(), '%Y-%m-%d')
            # task_end_time = datetime.strptime(input("Enter the task end time in HH:MM format : ").strip(), '%H:%M')
            task_start_date = validate_date_and_time("task start date")
            task_start_time = validate_date_and_time("task start time")
            task_end_date = validate_date_and_time("task end date")
            task_end_time = validate_date_and_time("task end time")
            task_status = "Upcoming"
            task_dict = {
                "user_email" : user_email,
                "task_name" : task_name,
                "task_start_date" : task_start_date,
                "task_start_time" : task_start_time,
                "task_end_date" : task_end_date,
                "task_end_time" : task_end_time,
                "task_status" : task_status
            }
            df_task_manager = pd.concat([df_task_manager, pd.DataFrame([task_dict])], ignore_index=True)
            df_task_manager.to_csv("./task_manager.csv", index=False)
            print("Task added successfully")
        elif user_input == 2:
            if len(df_task_manager.loc[df_task_manager['user_email'] == user_email, 'task_name']) > 0:
                print("Here is the list of your tasks. Please type the task name as input to delete it")
                print(df_task_manager.loc[df_task_manager['user_email'] == user_email, 'task_name'])
                task_to_be_deleted = input("Enter the task name to be deleted from the list above : ")
                df_task_manager = df_task_manager[df_task_manager['task_name'] != task_to_be_deleted]
                df_task_manager.to_csv("./task_manager.csv", index=False)
                print("Task deleted successfully")
            else:
                print("You do not have any tasks to be deleted")
        elif user_input == 3:
            if len(df_task_manager.loc[df_task_manager['user_email'] == user_email, 'task_name']) > 0:
                print("Here is the list of your tasks. Please type the task name as input to modify it")
                print(df_task_manager.loc[df_task_manager['user_email'] == user_email, 'task_name'])
                task_to_be_modified = input("Enter the task name to be modified from the list above : ")
                print("""Which of the following needs to be modified?
                1 - Task name
                2 - Start date
                3 - Start time
                4 - End date
                5 - End time
                6 - Task status
                """)
                user_modification_input = int(input("Select an option from the above list and type the number against it as an input : ").strip())
                if user_modification_input == 1:
                    new_task_name = input("Enter new task name : ").strip()
                    df_task_manager.loc[df_task_manager.task_name == task_to_be_modified, 'task_name'] = new_task_name
                    df_task_manager.to_csv("./task_manager.csv", index=False)
                    print("Task name modified successfully")
                elif user_modification_input == 2:
                    new_start_date = input("Enter new task start date in YYYY-MM-DD format : ").strip()
                    df_task_manager.loc[df_task_manager.task_name == task_to_be_modified, 'task_start_date'] = new_start_date
                    df_task_manager.to_csv("./task_manager.csv", index=False)
                    print("Task start date modified successfully")
                elif user_modification_input == 3:
                    new_start_time = input("Enter new task start time in HH:MM format : ").strip()
                    df_task_manager.loc[df_task_manager.task_name == task_to_be_modified, 'task_start_time'] = new_start_time
                    df_task_manager.to_csv("./task_manager.csv", index=False)
                    print("Task start time modified successfully")
                elif user_modification_input == 4:
                    new_end_date = input("Enter new task end date in YYYY-MM-DD format : ").strip()
                    df_task_manager.loc[df_task_manager.task_name == task_to_be_modified, 'task_end_date'] = new_end_date
                    df_task_manager.to_csv("./task_manager.csv", index=False)
                    print("Task end date modified successfully")
                elif user_modification_input == 5:
                    new_end_time = input("Enter new task end time in HH:MM format : ").strip()
                    df_task_manager.loc[df_task_manager.task_name == task_to_be_modified, 'task_end_time'] = new_end_time
                    df_task_manager.to_csv("./task_manager.csv", index=False)
                    print("Task end time modified successfully")
                elif user_modification_input == 6:
                    print("""What should be the new status of the task?
                    1 - Ongoing
                    2 - Completed
                    """)
                    new_task_status = int(input("Select an option from the above list and type the number against it as an input : ").strip())
                    if new_task_status == 1:
                        df_task_manager.loc[df_task_manager.task_name == task_to_be_modified, 'task_status'] = "Ongoing"
                        df_task_manager.to_csv("./task_manager.csv", index=False)
                        print("Task status modified successfully")
                    elif new_task_status == 2:
                        df_task_manager.loc[df_task_manager.task_name == task_to_be_modified, 'task_status'] = "Completed"
                        df_task_manager.to_csv("./task_manager.csv", index=False)
                        print("Task status modified successfully")
                    else:
                        print("You have made a wrong choice. Redirecting you to the main menu")
                else:
                    print("You have made a wrong choice. Redirecting you to the main menu")
            else:
                print("You do not have any tasks to be modified")
        elif user_input == 4:
            print("Here are all your tasks : ")
            for index in range(0, len(df_task_manager)):
                if df_task_manager['user_email'][index] == user_email:
                    print("------------------------------------------------------------------------------")
                    print(f"""
Task Name : {df_task_manager['task_name'][index]}
Task Start Date : {str(df_task_manager['task_start_date'][index]).split(" ")[0]}
Task Start Time : {str(df_task_manager['task_start_time'][index]).split(" ")[1]}
Task End Date : {str(df_task_manager['task_end_date'][index]).split(" ")[0]}
Task End Time : {str(df_task_manager['task_end_time'][index]).split(" ")[1]}
Task Status : {df_task_manager['task_status'][index]}
""")
        elif user_input == 5:
            task_manager_email = "gmail id"
            task_manager_password = "password"
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(task_manager_email, task_manager_password)
            message = f"""Subject : Task reminder\n\n
Dear {user_name},\n
Please find below the list of tasks created by you\n"""
            for index in range(0, len(df_task_manager)):
                if df_task_manager['user_email'][index] == user_email:
                    message += "------------------------------------------------------------------------------\n"
                    message += f"""
Task Name : {df_task_manager['task_name'][index]}
Task Start Date : {str(df_task_manager['task_start_date'][index]).split(" ")[0]}
Task Start Time : {str(df_task_manager['task_start_time'][index]).split(" ")[1]}
Task End Date : {str(df_task_manager['task_end_date'][index]).split(" ")[0]}
Task End Time : {str(df_task_manager['task_end_time'][index]).split(" ")[1]}
Task Status : {df_task_manager['task_status'][index]}
\n\n"""
            s.sendmail(task_manager_email, user_email, message)
            
            s.quit()
            print("Tasks successfully mailed to user")
            
        elif user_input == 6:
            print("Thank you for using task manager. Have a good day!")
            exit()
        else:
            print("You have made a wrong choice, please try again.")

def validate_date_and_time(req):
    date_regex = r'^(\d{4})-(0[1-9]|1[0-2]|[1-9])-([1-9]|0[1-9]|[1-2]\d|3[0-1])$'
    time_regex = r'^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$'
    if req.find("date") != -1:
        req_date = input(f"Enter the {req} in YYYY-MM-DD format : ").strip()
        while re.match(date_regex, req_date) == None:
            print("Sorry the date is not in the required format or it is not a valid date. Please provide a valid input in YYYY-MM-DD format")
            req_date = input(f"Enter the {req} in YYYY-MM-DD format : ").strip()
        return datetime.strptime(req_date, '%Y-%m-%d')
    else:
        req_time = input(f"Enter the {req} in HH:MM format : ").strip()
        while re.match(time_regex, req_time) == None:
            print("Sorry the time is not in the required format or it is not a valid time. Please provide a valid input in HH:MM format")
            req_time = input(f"Enter the {req} in HH:MM format : ").strip()
        return datetime.strptime(req_time, '%H:%M')
        

user_login(df_users, df_task_manager)
    
    