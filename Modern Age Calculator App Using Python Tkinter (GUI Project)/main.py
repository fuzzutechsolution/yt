import tkinter as tk

from tkinter import messagebox

from datetime import datetime



def calculate_age():

    dob_str = dob_entry.get()

    try:

        dob = datetime.strptime(dob_str, '%d-%m-%Y')

        today = datetime.today()

        years = today.year - dob.year

        months = today.month - dob.month

        days = today.day - dob.day



        if days < 0:

            months -= 1

            days += (datetime(today.year, today.month, 1) - datetime(today.year, today.month - 1, 1)).days

        if months < 0:

            years -= 1

            months += 12



        result_label.config(text=f"Your Age: {years} Years, {months} Months, {days} Days")

    except ValueError:

        messagebox.showerror("Invalid Input", "Please enter date in DD-MM-YYYY format.")



# GUI Setup

root = tk.Tk()

root.title("Age Calculator - FuzzuTech")

root.geometry("400x300")

root.config(bg="#2c3e50")



heading = tk.Label(root, text="Age Calculator", font=("Arial", 20, "bold"), bg="#2c3e50", fg="white")

heading.pack(pady=20)



dob_label = tk.Label(root, text="Enter your DOB (DD-MM-YYYY):", font=("Arial", 12), bg="#2c3e50", fg="white")

dob_label.pack(pady=5)



dob_entry = tk.Entry(root, font=("Arial", 12), justify='center')

dob_entry.pack(pady=5)



calculate_btn = tk.Button(root, text="Calculate Age", font=("Arial", 12, "bold"), bg="#1abc9c", fg="white", command=calculate_age)

calculate_btn.pack(pady=10)



result_label = tk.Label(root, text="", font=("Arial", 14, "bold"), bg="#2c3e50", fg="#ecf0f1")

result_label.pack(pady=20)



root.mainloop()