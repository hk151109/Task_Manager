import pandas as pd
import re
from datetime import datetime
import smtplib
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import os

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize dataframes
        if os.path.exists("./users.csv"):
            self.df_users = pd.read_csv("./users.csv")
        else:
            self.df_users = pd.DataFrame(columns=["user_email", "user_password", "user_name"])
            self.df_users.to_csv("./users.csv", index=False)
            
        if os.path.exists("./task_manager.csv"):
            self.df_task_manager = pd.read_csv("./task_manager.csv")
        else:
            self.df_task_manager = pd.DataFrame(columns=["user_email", "task_name", "task_start_date", 
                                                        "task_start_time", "task_end_date", "task_end_time", 
                                                        "task_status"])
            self.df_task_manager.to_csv("./task_manager.csv", index=False)
        
        self.current_user_email = None
        self.current_user_name = None
        
        # Create login frame
        self.create_login_frame()
    
    def create_login_frame(self):
        # Clear any existing frames
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.login_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.login_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        # Header
        tk.Label(self.login_frame, text="Task Manager Login", font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=20)
        
        # Email field
        tk.Label(self.login_frame, text="Email:", font=("Arial", 12), bg="#f0f0f0").pack(anchor="w", pady=(10, 0))
        self.email_var = tk.StringVar()
        tk.Entry(self.login_frame, textvariable=self.email_var, font=("Arial", 12), width=40).pack(fill="x", pady=(0, 10))
        
        # Password field
        tk.Label(self.login_frame, text="Password:", font=("Arial", 12), bg="#f0f0f0").pack(anchor="w", pady=(10, 0))
        self.password_var = tk.StringVar()
        tk.Entry(self.login_frame, textvariable=self.password_var, font=("Arial", 12), width=40, show="*").pack(fill="x", pady=(0, 10))
        
        # Name field (initially hidden)
        self.name_label = tk.Label(self.login_frame, text="Name:", font=("Arial", 12), bg="#f0f0f0")
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(self.login_frame, textvariable=self.name_var, font=("Arial", 12), width=40)
        
        # Login button
        login_button = tk.Button(self.login_frame, text="Login / Register", font=("Arial", 12, "bold"),
                                bg="#4CAF50", fg="white", command=self.process_login)
        login_button.pack(pady=20)
    
    def process_login(self):
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        
        # Validate email format
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.match(email_regex, email):
            messagebox.showerror("Error", "Invalid email format. Please try again.")
            return
        
        # Check if user exists
        if len(self.df_users) == 0 or email not in list(self.df_users['user_email']):
            # New user - show name field if not already showing
            if not self.name_label.winfo_ismapped():
                self.name_label.pack(anchor="w", pady=(10, 0))
                self.name_entry.pack(fill="x", pady=(0, 10))
                messagebox.showinfo("Registration", "New user detected. Please enter your name.")
                return
            
            # Process registration
            name = self.name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Name cannot be empty.")
                return
                
            # Add new user
            user_dict = {
                "user_email": email,
                "user_password": password,
                "user_name": name
            }
            self.df_users = pd.concat([self.df_users, pd.DataFrame([user_dict])], ignore_index=True)
            self.df_users.to_csv("./users.csv", index=False)
            messagebox.showinfo("Success", "Registration successful!")
            
            self.current_user_email = email
            self.current_user_name = name
            self.show_task_dashboard()
        else:
            # Existing user - authenticate password
            user_data = self.df_users[self.df_users['user_email'] == email]
            stored_password = user_data['user_password'].iloc[0]
            stored_name = user_data['user_name'].iloc[0]
            
            if password != stored_password:
                messagebox.showerror("Error", "Incorrect password. Please try again.")
                return
                
            messagebox.showinfo("Success", f"Welcome back, {stored_name}!")
            self.current_user_email = email
            self.current_user_name = stored_name
            self.show_task_dashboard()
    
    def show_task_dashboard(self):
        # Clear any existing frames
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main dashboard
        self.dashboard_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.dashboard_frame.pack(fill="both", expand=True)
        
        # Header with user info
        header_frame = tk.Frame(self.dashboard_frame, bg="#4CAF50")
        header_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(header_frame, text=f"Welcome, {self.current_user_name}", 
                font=("Arial", 16, "bold"), bg="#4CAF50", fg="white").pack(side="left", padx=20, pady=10)
        
        logout_btn = tk.Button(header_frame, text="Logout", font=("Arial", 12), 
                              command=self.create_login_frame)
        logout_btn.pack(side="right", padx=20, pady=10)
        
        # Create sidebar for actions
        sidebar_frame = tk.Frame(self.dashboard_frame, width=200, bg="#dcdcdc")
        sidebar_frame.pack(side="left", fill="y", padx=(0, 20))
        
        # Make sure sidebar maintains width
        sidebar_frame.pack_propagate(False)
        
        # Action buttons
        actions = [
            ("Add Task", self.show_add_task),
            ("Delete Task", self.show_delete_task),
            ("Modify Task", self.show_modify_task),
            ("View Tasks", self.show_view_tasks),
            ("Email Tasks", self.email_tasks)
        ]
        
        for text, command in actions:
            btn = tk.Button(sidebar_frame, text=text, font=("Arial", 12), 
                           width=15, command=command)
            btn.pack(pady=10, padx=10)
        
        # Content area (initially shows tasks)
        self.content_frame = tk.Frame(self.dashboard_frame, bg="white")
        self.content_frame.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=(0, 20))
        
        # Show tasks by default
        self.show_view_tasks()
    
    def clear_content_frame(self):
        # Clear the content frame for new content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_add_task(self):
        self.clear_content_frame()
        
        # Set up the add task form
        tk.Label(self.content_frame, text="Add New Task", font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        
        form_frame = tk.Frame(self.content_frame, bg="white")
        form_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Task name
        tk.Label(form_frame, text="Task Name:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="w", pady=10)
        task_name_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=task_name_var, font=("Arial", 12), width=30).grid(row=0, column=1, sticky="w", pady=10)
        
        # Start date
        tk.Label(form_frame, text="Start Date:", font=("Arial", 12), bg="white").grid(row=1, column=0, sticky="w", pady=10)
        start_date_cal = DateEntry(form_frame, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        start_date_cal.grid(row=1, column=1, sticky="w", pady=10)
        
        # Start time
        tk.Label(form_frame, text="Start Time (HH:MM):", font=("Arial", 12), bg="white").grid(row=2, column=0, sticky="w", pady=10)
        start_time_var = tk.StringVar()
        start_time_var.set("09:00")
        tk.Entry(form_frame, textvariable=start_time_var, font=("Arial", 12), width=10).grid(row=2, column=1, sticky="w", pady=10)
        
        # End date
        tk.Label(form_frame, text="End Date:", font=("Arial", 12), bg="white").grid(row=3, column=0, sticky="w", pady=10)
        end_date_cal = DateEntry(form_frame, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        end_date_cal.grid(row=3, column=1, sticky="w", pady=10)
        
        # End time
        tk.Label(form_frame, text="End Time (HH:MM):", font=("Arial", 12), bg="white").grid(row=4, column=0, sticky="w", pady=10)
        end_time_var = tk.StringVar()
        end_time_var.set("17:00")
        tk.Entry(form_frame, textvariable=end_time_var, font=("Arial", 12), width=10).grid(row=4, column=1, sticky="w", pady=10)
        
        # Submit button
        submit_btn = tk.Button(form_frame, text="Add Task", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
                              command=lambda: self.process_add_task(
                                  task_name_var.get(),
                                  start_date_cal.get_date(),
                                  start_time_var.get(),
                                  end_date_cal.get_date(),
                                  end_time_var.get()
                              ))
        submit_btn.grid(row=5, column=0, columnspan=2, pady=20)
    
    def process_add_task(self, task_name, start_date, start_time, end_date, end_time):
        # Validate input
        if not task_name:
            messagebox.showerror("Error", "Task name cannot be empty")
            return
            
        # Validate time format
        time_regex = r'^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$'
        if not re.match(time_regex, start_time) or not re.match(time_regex, end_time):
            messagebox.showerror("Error", "Time must be in HH:MM format")
            return
        
        # Create the task
        task_dict = {
            "user_email": self.current_user_email,
            "task_name": task_name,
            "task_start_date": start_date,
            "task_start_time": datetime.strptime(start_time, '%H:%M'),
            "task_end_date": end_date,
            "task_end_time": datetime.strptime(end_time, '%H:%M'),
            "task_status": "Upcoming"
        }
        
        # Add to dataframe and save
        self.df_task_manager = pd.concat([self.df_task_manager, pd.DataFrame([task_dict])], ignore_index=True)
        self.df_task_manager.to_csv("./task_manager.csv", index=False)
        
        messagebox.showinfo("Success", "Task added successfully")
        self.show_view_tasks()
    
    def show_delete_task(self):
        self.clear_content_frame()
        
        # Filter tasks for current user
        user_tasks = self.df_task_manager[self.df_task_manager['user_email'] == self.current_user_email]
        
        if len(user_tasks) == 0:
            tk.Label(self.content_frame, text="You don't have any tasks to delete", 
                    font=("Arial", 14), bg="white").pack(pady=50)
            return
            
        tk.Label(self.content_frame, text="Delete Task", font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        
        # Create a listbox of tasks
        tk.Label(self.content_frame, text="Select a task to delete:", font=("Arial", 12), bg="white").pack(anchor="w", padx=20, pady=(20, 10))
        
        task_listbox = tk.Listbox(self.content_frame, font=("Arial", 12), width=50, height=10)
        task_listbox.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Populate listbox
        task_names = user_tasks['task_name'].tolist()
        for name in task_names:
            task_listbox.insert(tk.END, name)
            
        # Delete button
        delete_btn = tk.Button(self.content_frame, text="Delete Selected Task", 
                              font=("Arial", 12, "bold"), bg="#FF5722", fg="white",
                              command=lambda: self.process_delete_task(task_listbox, task_names))
        delete_btn.pack(pady=20)
    
    def process_delete_task(self, listbox, task_names):
        # Get selected task
        selected_indices = listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select a task to delete")
            return
            
        selected_index = selected_indices[0]
        task_to_delete = task_names[selected_index]
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{task_to_delete}'?")
        if not confirm:
            return
            
        # Delete the task
        self.df_task_manager = self.df_task_manager[
            ~((self.df_task_manager['user_email'] == self.current_user_email) & 
              (self.df_task_manager['task_name'] == task_to_delete))
        ]
        
        # Save changes
        self.df_task_manager.to_csv("./task_manager.csv", index=False)
        
        messagebox.showinfo("Success", "Task deleted successfully")
        self.show_delete_task()  # Refresh the delete task view
    
    def show_modify_task(self):
        self.clear_content_frame()
        
        # Filter tasks for current user
        user_tasks = self.df_task_manager[self.df_task_manager['user_email'] == self.current_user_email]
        
        if len(user_tasks) == 0:
            tk.Label(self.content_frame, text="You don't have any tasks to modify", 
                    font=("Arial", 14), bg="white").pack(pady=50)
            return
            
        tk.Label(self.content_frame, text="Modify Task", font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        
        # Step 1: Select task
        frame1 = tk.Frame(self.content_frame, bg="white")
        frame1.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.Label(frame1, text="Step 1: Select a task to modify:", font=("Arial", 12), bg="white").pack(anchor="w", pady=(10, 5))
        
        task_listbox = tk.Listbox(frame1, font=("Arial", 12), width=50, height=6)
        task_listbox.pack(fill="both", expand=True, pady=5)
        
        # Populate listbox
        task_names = user_tasks['task_name'].tolist()
        for name in task_names:
            task_listbox.insert(tk.END, name)
        
        # Step 2: Select what to modify
        frame2 = tk.Frame(self.content_frame, bg="white")
        frame2.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.Label(frame2, text="Step 2: Select what to modify:", font=("Arial", 12), bg="white").pack(anchor="w", pady=(10, 5))
        
        modification_var = tk.StringVar()
        modification_var.set("task_name")
        
        options = [
            ("Task Name", "task_name"),
            ("Start Date", "task_start_date"),
            ("Start Time", "task_start_time"),
            ("End Date", "task_end_date"),
            ("End Time", "task_end_time"),
            ("Task Status", "task_status")
        ]
        
        for text, value in options:
            tk.Radiobutton(frame2, text=text, variable=modification_var, value=value, 
                          font=("Arial", 12), bg="white").pack(anchor="w", pady=2)
        
        # Step 3: Enter new value
        frame3 = tk.Frame(self.content_frame, bg="white")
        frame3.pack(fill="both", expand=True, padx=20, pady=10)
        
        tk.Label(frame3, text="Step 3: Enter new value:", font=("Arial", 12), bg="white").pack(anchor="w", pady=(10, 5))
        
        # Frame for different input types
        input_frame = tk.Frame(frame3, bg="white")
        input_frame.pack(fill="x", pady=5)
        
        # Input variables for different types
        self.new_value_var = tk.StringVar()
        self.new_date_cal = DateEntry(input_frame, width=12, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.status_var = tk.StringVar()
        self.status_var.set("Upcoming")
        
        # Default input (text entry)
        self.current_input = tk.Entry(input_frame, textvariable=self.new_value_var, font=("Arial", 12), width=30)
        self.current_input.pack(side="left", pady=5)
        
        # Function to update input type based on selected modification
        def update_input_type(*args):
            # Remove current input
            for widget in input_frame.winfo_children():
                widget.pack_forget()
                
            selected = modification_var.get()
            
            if selected in ["task_start_date", "task_end_date"]:
                self.new_date_cal.pack(side="left", pady=5)
                self.current_input = self.new_date_cal
            elif selected in ["task_status"]:
                status_menu = tk.OptionMenu(input_frame, self.status_var, "Upcoming", "Ongoing", "Completed")
                status_menu.config(font=("Arial", 12), width=10)
                status_menu.pack(side="left", pady=5)
                self.current_input = status_menu
            else:
                self.current_input = tk.Entry(input_frame, textvariable=self.new_value_var, font=("Arial", 12), width=30)
                self.current_input.pack(side="left", pady=5)
                
                # Set placeholder based on field
                if selected == "task_start_time" or selected == "task_end_time":
                    self.new_value_var.set("HH:MM")
        
        # Set up trace on the modification variable
        modification_var.trace("w", update_input_type)
        
        # Submit button
        submit_btn = tk.Button(self.content_frame, text="Apply Changes", 
                              font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
                              command=lambda: self.process_modify_task(
                                  task_listbox, task_names, modification_var.get()))
        submit_btn.pack(pady=20)
    
    def process_modify_task(self, listbox, task_names, modification_field):
        # Get selected task
        selected_indices = listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select a task to modify")
            return
            
        selected_index = selected_indices[0]
        task_to_modify = task_names[selected_index]
        
        # Get new value based on modification type
        if modification_field in ["task_start_date", "task_end_date"]:
            new_value = self.new_date_cal.get_date()
        elif modification_field == "task_status":
            new_value = self.status_var.get()
        else:
            new_value = self.new_value_var.get().strip()
            
            # Validate time format for time fields
            if modification_field in ["task_start_time", "task_end_time"]:
                time_regex = r'^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$'
                if not re.match(time_regex, new_value):
                    messagebox.showerror("Error", "Time must be in HH:MM format")
                    return
                new_value = datetime.strptime(new_value, '%H:%M')
        
        # Validate task name is not empty
        if modification_field == "task_name" and not new_value:
            messagebox.showerror("Error", "Task name cannot be empty")
            return
        
        # Update the dataframe
        task_index = self.df_task_manager[
            (self.df_task_manager['user_email'] == self.current_user_email) & 
            (self.df_task_manager['task_name'] == task_to_modify)
        ].index
        
        self.df_task_manager.loc[task_index, modification_field] = new_value
        
        # Save changes
        self.df_task_manager.to_csv("./task_manager.csv", index=False)
        
        messagebox.showinfo("Success", "Task modified successfully")
        self.show_view_tasks()
    
    def show_view_tasks(self):
        self.clear_content_frame()
        
        # Filter tasks for current user
        user_tasks = self.df_task_manager[self.df_task_manager['user_email'] == self.current_user_email]
        
        # Create a canvas with scrollbar for the tasks
        canvas_frame = tk.Frame(self.content_frame)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(canvas_frame, bg="white")
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        # Configure scrollbar
        scrollable_frame = tk.Frame(canvas, bg="white")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title
        tk.Label(scrollable_frame, text="Your Tasks", font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        
        if len(user_tasks) == 0:
            tk.Label(scrollable_frame, text="You don't have any tasks yet", 
                    font=("Arial", 14), bg="white").pack(pady=50)
            return
        
        # Create task cards for each task
        for _, task in user_tasks.iterrows():
            task_frame = tk.Frame(scrollable_frame, bg="white", bd=1, relief=tk.SOLID)
            task_frame.pack(fill="x", pady=10, padx=20)
            
            # Status color indicator
            status_colors = {
                "Upcoming": "#FFC107",  # Yellow
                "Ongoing": "#2196F3",   # Blue
                "Completed": "#4CAF50"  # Green
            }
            
            status_color = status_colors.get(task['task_status'], "#FFC107")
            
            status_indicator = tk.Frame(task_frame, bg=status_color, width=5)
            status_indicator.pack(side="left", fill="y")
            
            # Task details
            details_frame = tk.Frame(task_frame, bg="white")
            details_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            
            # Task name (bold)
            tk.Label(details_frame, text=task['task_name'], font=("Arial", 14, "bold"), 
                    bg="white", anchor="w").pack(fill="x")
            
            # Format dates and times
            try:
                start_date = str(task['task_start_date']).split()[0] if isinstance(task['task_start_date'], str) else task['task_start_date']
                start_time = str(task['task_start_time']).split()[1] if isinstance(task['task_start_time'], str) and " " in str(task['task_start_time']) else task['task_start_time']
                end_date = str(task['task_end_date']).split()[0] if isinstance(task['task_end_date'], str) else task['task_end_date']
                end_time = str(task['task_end_time']).split()[1] if isinstance(task['task_end_time'], str) and " " in str(task['task_end_time']) else task['task_end_time']
            except:
                # Fallback if date parsing fails
                start_date = task['task_start_date']
                start_time = task['task_start_time']
                end_date = task['task_end_date']
                end_time = task['task_end_time']
            
            # Create info text
            info_text = f"Start: {start_date} {start_time} | End: {end_date} {end_time} | Status: {task['task_status']}"
            tk.Label(details_frame, text=info_text, font=("Arial", 10), 
                    bg="white", anchor="w").pack(fill="x")
    
    def email_tasks(self):
        # Check if user has tasks
        user_tasks = self.df_task_manager[self.df_task_manager['user_email'] == self.current_user_email]
        
        if len(user_tasks) == 0:
            messagebox.showinfo("No Tasks", "You don't have any tasks to email.")
            return
            
        try:
            # Email sending process
            task_manager_email = "gmail id"
            task_manager_password = "password"
            
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(task_manager_email, task_manager_password)
            
            message = f"""Subject : Task reminder\n\n
Dear {self.current_user_name},\n
Please find below the list of tasks created by you\n"""
            
            for _, task in user_tasks.iterrows():
                message += "------------------------------------------------------------------------------\n"
                message += f"""
Task Name : {task['task_name']}
Task Start Date : {str(task['task_start_date']).split(" ")[0] if isinstance(task['task_start_date'], str) else task['task_start_date']}
Task Start Time : {str(task['task_start_time']).split(" ")[1] if isinstance(task['task_start_time'], str) and " " in str(task['task_start_time']) else task['task_start_time']}
Task End Date : {str(task['task_end_date']).split(" ")[0] if isinstance(task['task_end_date'], str) else task['task_end_date']}
Task End Time : {str(task['task_end_time']).split(" ")[1] if isinstance(task['task_end_time'], str) and " " in str(task['task_end_time']) else task['task_end_time']}
Task Status : {task['task_status']}
\n\n"""
            
            s.sendmail(task_manager_email, self.current_user_email, message)
            s.quit()
            
            messagebox.showinfo("Success", "Tasks successfully emailed to you!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")

# Main application runner
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()