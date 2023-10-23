import tkinter as tk
from datetime import datetime
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import calendar
from PIL import Image, ImageTk  # Import the necessary modules

class BudgetManagementApp:
    def __init__(self):
        # self.balance = 0

        self.history = []

        self.load_history()


        self.root = tk.Tk()
        self.root.title("Budget Management App")
        self.root.geometry("600x600")

        background_image = Image.open("money.jpg")  # Replace with your image file
        self.background_photo = ImageTk.PhotoImage(background_image)
        self.background_label = tk.Label(self.root, image=self.background_photo)
        self.background_label.place(relwidth=1, relheight=1)

        self.balance_label = tk.Label(self.root, text=f"Balance: {self.balance:.2f}€", font=("Arial", 16))
        self.balance_label.config(text=f"Balance: {self.balance:.2f}€")

        self.balance_label.pack(pady=10)

        self.amount_label = tk.Label(self.root, text="Amount:", font=("Arial", 14))
        self.amount_label.pack()
        self.amount_entry = tk.Entry(self.root, font=("Arial", 14))
        self.amount_entry.pack()

        self.description_label = tk.Label(self.root, text="Description:", font=("Arial", 14))
        self.description_label.pack()
        self.description_entry = tk.Entry(self.root, font=("Arial", 14))
        self.description_entry.pack()

        self.add_purchase_button = tk.Button(self.root, text="Outflow", font=("Arial", 14), bg = 'maroon', fg = 'white',
                                             command=self.add_purchase)
        self.add_purchase_button.pack(pady=10)

        self.subtract_purchase_button = tk.Button(self.root, text="Inflow", font=("Arial", 14),bg = 'maroon', fg = 'white',
                                                  command=self.subtract_purchase)
        self.subtract_purchase_button.pack()

        self.show_history_button = tk.Button(self.root, text="Show History", font=("Arial", 14),bg = 'maroon', fg = 'white',
                                             command=self.show_history)
        self.show_history_button.pack(pady=10)

        self.plot_history_button = tk.Button(self.root, text="Plot History", font=("Arial", 14),bg = 'maroon', fg = 'white',
                                             command=self.plot_history)
        self.plot_history_button.pack()

        self.expenses_by_month_button = tk.Button(self.root, text="Monthly income/outcome", font=("Arial", 14),bg = 'maroon', fg = 'white',
                                                  command=self.print_expenses_by_month)
        self.expenses_by_month_button.pack(pady=10)

        self.output_text = tk.Text(self.root, wrap=tk.WORD, font=("Arial", 12))
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=500, pady=100)





    def add_transaction(self, amount, description):
        self.balance += amount
        now = datetime.now()
        self.history.append((now, self.balance, description))
        self.update_balance_label()

    def update_balance_label(self):
        self.balance_label.config(text=f"Balance: {self.balance:.2f}€")

    def add_purchase(self):

        amount = float(self.amount_entry.get())
        description = self.description_entry.get()
        self.add_transaction(-amount, description)
        self.save_history()


    def subtract_purchase(self):

        amount = float(self.amount_entry.get())
        description = self.description_entry.get()
        self.add_transaction(amount, description)
        self.save_history()


    def show_history(self):
        self.output_text.delete(1.0, tk.END)  # Clear previous text
        reversed_history = reversed(self.history)  # Reverse the history list

        for date, balance, description in reversed_history:
            self.output_text.insert(tk.END,
                                    f"Date: {date.strftime('%Y-%m-%d %H:%M:%S')} | Balance: {balance:.2f}€ | Description: {description}\n")

    def plot_history(self):


        dates = [date for date, _, _ in self.history]
        balance_values = [balance for _, balance, _ in self.history]
        descriptions = [description for _, _, description in self.history]
        numeric_dates = np.arange(len(dates))

        fig, ax = plt.subplots()
        ax.plot(numeric_dates, balance_values, marker='o')
        ax.set_xticks(numeric_dates)
        ax.set_xticklabels([date.strftime("%Y-%m-%d") for date in dates], rotation=45, ha="right")
        ax.set_xlabel("Date")
        ax.set_ylabel("Balance  €")
        ax.set_title("Balance History")



        cursor = mplcursors.cursor(hover=True)

        cursor.connect("add", lambda sel: sel.annotation.set_text(descriptions[int(sel.target.index)+1]))
        plt.show()

    def load_history(self):
        try:
            with open("history.txt", "r") as file:
                for line in file:
                    date_str, balance_str, description = line.strip().split("|")
                    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    balance = float(balance_str)
                    self.balance = balance
                    self.history.append((date, balance, description))

        except FileNotFoundError:
            self.balance = 0

           # No history file yet, so ignore

    def save_history(self):
        with open("history.txt", "w") as file:
            for date, balance, description in self.history:
                file.write(f"{date.strftime('%Y-%m-%d %H:%M:%S')}|{balance:.2f}|{description}\n")

    def calculate_expenses_by_month(self):
        expenses_by_month = {}  # Dictionary to store expenses for each month
        income_by_month = {}  # Dictionary to store expenses for each month

        balance_prev = 0

        for date, balance, _ in self.history:
            year_month = (date.year, date.month)
            if year_month not in expenses_by_month:
                expenses_by_month[year_month] = 0
                income_by_month[year_month] = 0

            if (balance - balance_prev)<0:
                expenses_by_month[year_month] += abs(balance-balance_prev)  # Consider only positive balances (expenses)
            else:
                income_by_month[year_month] += abs(balance - balance_prev)

            balance_prev = balance

        return expenses_by_month,income_by_month

    def print_expenses_by_month(self):
        self.output_text.delete(1.0, tk.END)  # Clear previous text
        expenses_by_month, income_by_month = self.calculate_expenses_by_month()

        combined_data = {}
        count = 0
        total_expenses = 0
        total_income = 0

        for (year, month), expenses in expenses_by_month.items():
            if (year, month) in income_by_month:
                income = income_by_month[(year, month)]
                combined_data[(year, month)] = (expenses, income)

        for (year, month), (expenses, income) in combined_data.items():
            month_name = calendar.month_name[month]
            net = income - expenses
            if net>0:
                color = 'green'
            elif net<0:
                color = 'red'
            elif net==0:
                color= 'black'

            self.output_text.tag_configure(color, foreground=color)
            self.output_text.tag_configure("bold", font=("Arial", 12, "bold"))


            text = f"{month_name} {year}:\n"
            self.output_text.insert(tk.END,text,"bold")

            text1 = f" Expenses: {expenses:.2f}€       "
            text2 = f"Income: {income:.2f}€        "

            text3 = f"   Net: {net:.2f}€\n"

            # self.output_text.insert(tk.END,text,"black")
            self.output_text.insert(tk.END,text1,"red")
            self.output_text.insert(tk.END,text2,"green")

            arrow_symbol = "→"
            self.output_text.insert(tk.END, arrow_symbol, "center")
            self.output_text.insert(tk.END,text3,color)
            self.output_text.insert(tk.END, "\n")

            # print(f"{month_name} {year}: Expenses: €{expenses:.2f} | Income: €{income:.2f} | Net: €{net:.2f}")
            total_expenses +=expenses
            total_income +=income
            count +=1

        mean_monthly_expenses = total_expenses / count
        mean_monthly_income = total_income / count

        self.output_text.insert(tk.END,"\n")
        self.output_text.insert(tk.END,"\n")


        self.output_text.insert(tk.END,f"Mean monthly expenses: {mean_monthly_expenses}\n")
        self.output_text.insert(tk.END,f"Mean monthly income: {mean_monthly_income}\n")




    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = BudgetManagementApp()
    app.run()
