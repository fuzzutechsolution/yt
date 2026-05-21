import tkinter as tk

from tkinter import messagebox

import json



class TodoApp:

    def __init__(self, root):

        self.root = root

        self.root.title("Modern To-Do List - Developed By Fuzail Developer")

        self.root.geometry("400x500")

        self.root.config(bg="#2c3e50")



        self.tasks = []

        self.load_tasks()



        tk.Label(root, text="📝 To-Do List", font=("Arial", 20, "bold"), bg="#2c3e50", fg="white").pack(pady=10)



        entry_frame = tk.Frame(root, bg="#2c3e50")

        entry_frame.pack(pady=10)

        

        self.task_entry = tk.Entry(entry_frame, font=("Arial", 14), width=20)

        self.task_entry.grid(row=0, column=0, padx=10)

        

        tk.Button(entry_frame, text="Add", font=("Arial", 12), bg="#27ae60", fg="white", command=self.add_task).grid(row=0, column=1)



        self.listbox = tk.Listbox(root, font=("Arial", 14), width=30, height=10, selectmode=tk.SINGLE)

        self.listbox.pack(pady=10)

        self.update_listbox()



        button_frame = tk.Frame(root, bg="#2c3e50")

        button_frame.pack(pady=10)



        tk.Button(button_frame, text="Delete", font=("Arial", 12), bg="#c0392b", fg="white", command=self.delete_task).grid(row=0, column=0, padx=10)

        tk.Button(button_frame, text="Complete", font=("Arial", 12), bg="#2980b9", fg="white", command=self.complete_task).grid(row=0, column=1, padx=10)



    def add_task(self):

        task = self.task_entry.get().strip()

        if task:

            self.tasks.append({"task": task, "completed": False})

            self.task_entry.delete(0, tk.END)

            self.update_listbox()

            self.save_tasks()

        else:

            messagebox.showwarning("Input Error", "Please enter a task.")



    def delete_task(self):

        selected = self.listbox.curselection()

        if selected:

            del self.tasks[selected[0]]

            self.update_listbox()

            self.save_tasks()

        else:

            messagebox.showwarning("Selection Error", "Please select a task to delete.")



    def complete_task(self):

        selected = self.listbox.curselection()

        if selected:

            task = self.tasks[selected[0]]

            task["completed"] = not task["completed"]

            self.update_listbox()

            self.save_tasks()

        else:

            messagebox.showwarning("Selection Error", "Please select a task.")



    def update_listbox(self):

        self.listbox.delete(0, tk.END)

        for task in self.tasks:

            display = f"✔️ {task['task']}" if task["completed"] else task['task']

            self.listbox.insert(tk.END, display)



    def load_tasks(self):

        try:

            with open("tasks.json", "r") as file:

                self.tasks = json.load(file)

        except FileNotFoundError:

            self.tasks = []



    def save_tasks(self):

        with open("tasks.json", "w") as file:

            json.dump(self.tasks, file, indent=4)



if __name__ == "__main__":

    root = tk.Tk()

    TodoApp(root)

    root.mainloop()

 