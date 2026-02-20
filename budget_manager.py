import customtkinter as ctk
from tkinter import messagebox
import json
import os
import datetime
import requests

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_DATA_DIR = os.path.join(os.path.expanduser("~"), ".budget_manager")
if not os.path.exists(APP_DATA_DIR):
    os.makedirs(APP_DATA_DIR)
DATA_FILE = os.path.join(APP_DATA_DIR, "budget_manager.json")

class BudgetApp(ctk.CTk):
    
    DEVELOPER_CATEGORIES = ["Food", "Travel","Rent", "Health", 
                                      "Bill", "Technology"]
    
    DEVELOPER_CURRENCY_SETTİNGS = ["TRY" , "USD" , "EUR"]
    
    def __init__(self):
        super().__init__()

        
        self.api_key = "74c37d25f08e14a85f184930"
        self.current_balance = 0.0
        self.transactions = []
        self.user_categories = []
        self.incomes = 0.0
        self.today_str = datetime.date.today().strftime("%d.%m.%Y")
        self.selected_currency = "TRY"
        
        self.title("Budget Manager")
        self.geometry("900x600")
        
        try:
            
            self.iconbitmap("budgetikon.ico")
            pass
        
        except:
            pass
        
        self.withdraw() 

        if self.load_data():
            self.init_main_ui()
            self.refresh_history_ui()
            self.after(200, self.deiconify)
        else:
            self.show_onboarding()

    
    def get_exchange_rates(self, base_currency="TRY"):
        
        url = f"https://v6.exchangerate-api.com/v6/74c37d25f08e14a85f184930/latest/{base_currency}"   
        
        try:
            response = requests.get(url)
            data = response.json()

            if data["result"] == "success":
                usd_rate = data["conversion_rates"].get("USD", 1.0)
                eur_rate = data["conversion_rates"].get("EUR", 1.0)
                return {"USD": usd_rate, "EUR": eur_rate}
            else:
                messagebox.showwarning("Warning", "Failed to fetch exchange rates. Using default rates.")
                return {"USD": 0.05, "EUR": 0.045}
        except:
            messagebox.showwarning("Warning", "Error fetching exchange rates. Using default rates.")
            return {"USD": 0.05, "EUR": 0.045}
            
    
    def save_data(self):
        data = {
            "balance": self.current_balance,
            "transactions": self.transactions,
            "user_categories": self.user_categories , 
            "incomes" : self.incomes , 
            "currency": self.selected_currency
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.current_balance = float(data.get("balance", 0.0))
                    self.transactions = data.get("transactions", [])
                    self.user_categories = data.get("user_categories" , [])
                    self.incomes = float(data.get("incomes" , 0.0))
                    self.selected_currency = data.get("currency" , "TRY")
                    return True
            except:
                return False
        return False
    
    def get_all_categories(self):
        return self.DEVELOPER_CATEGORIES + self.user_categories
    
    def get_all_currency_settings(self):
        return self.DEVELOPER_CURRENCY_SETTİNGS

    def show_onboarding(self):
        
        self.setup_win = ctk.CTkToplevel(self)
        self.setup_win.title("Entrance")
        self.setup_win.geometry("500x350")
        self.setup_win.attributes("-topmost", True)
        self.setup_win.protocol("WM_DELETE_WINDOW", self.quit)

        ctk.CTkLabel(self.setup_win, text="Welcome to Budget Manager", font=("Arial", 20, "bold")).pack(pady=20)
        ctk.CTkLabel(self.setup_win, text="Enter your starting currency and balance" , 
                                        font=("Arial" , 15 , "normal")).pack(pady=10)
        
        self.initial_currency_option_menu = ctk.CTkOptionMenu(self.setup_win, values=self.get_all_currency_settings(),
                                                                 command=self.update_currency , width=100)
        self.initial_currency_option_menu.pack(pady=20)

        self.initial_balance_entry = ctk.CTkEntry(self.setup_win, placeholder_text="e.g. 5000")
        self.initial_balance_entry.pack(pady=5)
        
        ctk.CTkButton(self.setup_win, text="Start Application", command=self.complete_setup , font=("Arial" , 15 , "normal")).pack(pady=30)

    def complete_setup(self):
        val = self.initial_balance_entry.get()
        currency_val = self.initial_currency_option_menu.get()
        
        if val.replace('.', '', 1).isdigit():
            
            amount = float(val)

            if currency_val != "TRY":
                rates = self.get_exchange_rates(base_currency="TRY")
                rate = rates.get(currency_val, 1.0)
                amount = amount / rate

            
            self.current_balance = amount
            
            self.selected_currency = currency_val
            self.save_data()
            self.setup_win.destroy()
            self.init_main_ui()
            self.deiconify()
        else:
            messagebox.showwarning("Warning", "Please enter a valid number!")

    def init_main_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        #-----LEFT SİDEBAR-----
        
        ctk.CTkLabel(self.sidebar, text="ADD EXPENSE", font=("Inter", 20, "bold")).pack(pady=20)

        self.date_input = ctk.CTkEntry(self.sidebar, placeholder_text="Date")
        self.date_input.pack(padx=20, pady=25, fill="x")

        self.category_menu = ctk.CTkOptionMenu(self.sidebar, values=self.get_all_categories(),
                                                                 
                                                                      width=100)
        self.category_menu.place(x=20 , y=140)

        self.add_category_button = ctk.CTkButton(self.sidebar , text="+" , width=40 ,
                                          font=("Arial" , 20 ,"bold") , fg_color="green" , hover_color="#2ecc71",
                                            command=self.add_category)
        self.add_category_button.place(x=130 ,y=140)
        
        self.name_entry = ctk.CTkEntry(self.sidebar , placeholder_text="Name")
        self.name_entry.pack(padx=20 , pady=37 , fill="x")

        self.amount_input = ctk.CTkEntry(self.sidebar, placeholder_text="Amount")
        self.amount_input.place(x=20 , y=230)
        
        self.add_btn = ctk.CTkButton(self.sidebar, text="ADD", fg_color="green", font=("Arial" , 15 ,"normal") ,
                                     command=self.add_transaction)
        self.add_btn.pack(padx=20, pady=25, fill="x")

        #-----RİGHT MAİN CONTENT-----
        
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.balance_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.balance_container.pack(pady=20)
        
        self.balance_label = ctk.CTkLabel(self.main_content, text=f"Total Balance: {self.current_balance:.2f} TL", font=("Arial", 28, "bold"))
        self.balance_label.pack(pady=5)

        self.income_btn = ctk.CTkButton(self.balance_container, text="+", width=40, font=("Arial", 20, "bold"),
                                         fg_color="green", hover_color="#2ecc71", command=self.add_income)
        self.income_btn.pack(side="left")
        
        self.currency_option_menu = ctk.CTkOptionMenu(self.balance_container, values=self.get_all_currency_settings(), 
                                                                            command=self.update_currency ,width=100)
        self.currency_option_menu.pack(side="left", padx=20)

        self.currency_option_menu.set(self.selected_currency)
        self.update_currency(self.selected_currency)

        self.history_frame = ctk.CTkScrollableFrame(self.main_content, label_text="Transaction History")
        self.history_frame.pack(fill="both", expand=True, pady=10)

        self.delete_button = ctk.CTkButton(self.main_content , text="Reset All" , fg_color="#c0392b", hover_color="#e74c3c" ,
                                           font=("Arial" , 15 , "normal")
                                           ,command=self.delete_and_start_again)
        self.delete_button.pack(padx=20 , pady=20 , side="bottom")

    def add_transaction(self):
        amt = self.amount_input.get()
        
        if not amt or not amt.replace('.', '', 1).isdigit():
            messagebox.showerror("Error", "Invalid amount! Please enter a number.")
            return
        
        amt_val = float(amt)

        rates = self.get_exchange_rates(base_currency="TRY")
        rate = rates.get(self.selected_currency, 1.0)

        amount_in_try = amt_val / rate

        if amount_in_try > self.current_balance:
            messagebox.showerror("Error", "Insufficient balance for this expense.")
            return
        
        self.current_balance -= amount_in_try

        self.update_currency(self.selected_currency)

                                

        entry = {
                "date": self.date_input.get(), 
                "category": self.category_menu.get(),
                "name": self.name_entry.get(), 
                "amount": amount_in_try,
                "original_amount" : amt_val , 
                "original_currency" : self.selected_currency
            }
            
        self.transactions.append(entry)
        self.save_data()
        self.add_to_history_ui(entry)
            
        self.date_input.delete(0, 'end')
        self.name_entry.delete(0, 'end')
        self.amount_input.delete(0, 'end')
            
        
    def add_income(self):
        
        dialog = ctk.CTkInputDialog(text="Enter income amount:", title="Add Income")
        income_val = dialog.get_input()
        
        if income_val and income_val.replace('.', '', 1).isdigit():
            
            amt_val = float(income_val)
            
            rates = self.get_exchange_rates(base_currency="TRY")
            rate = rates.get(self.selected_currency, 1.0)

            amount_in_try = amt_val / rate

            self.current_balance += amount_in_try
            
            self.update_currency(self.selected_currency)

            entry = {
               "date":self.today_str,
                "category":"Income",
                "name":"Deposit",
                "amount": amount_in_try, 
                "original_amount" : amt_val ,
                "original_currency" : self.selected_currency

            }
            
            self.transactions.append(entry) 
            self.save_data()
            self.add_to_history_ui(entry)
        
        elif income_val is not None:
            messagebox.showwarning("Warning", "Please enter a valid number!")
    
    
    def add_category(self):

        category = ctk.CTkInputDialog(text="Enter new category:" , title="Add category")
        new_category = category.get_input()

        if new_category and new_category.strip():
            
            new_category = new_category.strip()

            if new_category.isdigit():
                
                messagebox.showwarning("Warning" , "Category name cannot be only numbers.")
                return
            
            if new_category in self.get_all_categories():
                
                messagebox.showinfo("Info" , "This category already exists!")
                return

            self.user_categories.append(new_category)
            
            
            self.category_menu.configure(values=self.get_all_categories())
            self.category_menu.set(new_category) 
            
            self.save_data()   

        elif new_category is not None:
            messagebox.showwarning("Attention", "Please enter a valid category name.")

        
    def update_currency(self, selected_currency):
        self.selected_currency = selected_currency 
        self.save_data() 

        rates = self.get_exchange_rates(base_currency="TRY")
        rate = rates.get(selected_currency, 1.0)

        
        converted_balance = self.current_balance * rate
        
        self.balance_label.configure(text=f"Total Balance: {converted_balance:.2f} {selected_currency}")
          
    
    def add_to_history_ui(self, entry):
        
        name_display = f"({entry.get('name', '')})" if entry.get('name') else ""

        display_amount = entry.get("original_amount", entry["amount"])
    
        display_currency = entry.get("original_currency", self.selected_currency)
        
        
        if entry.get("category") == "Income":
            txt = f"{entry['date']} | {entry['category']} {name_display} | +{display_amount:.2f} {display_currency}"
                                                                                                   
            text_color = "#2ecc71" 
        else:
            txt = f"{entry['date']} | {entry['category']} {name_display} | -{display_amount:.2f} {display_currency}"
            text_color = "#e74c3c" 

        ctk.CTkLabel(
            self.history_frame, 
            text=txt, 
            font=("Consolas", 14), 
            text_color=text_color
        ).pack(pady=2, anchor="w")

    def refresh_history_ui(self):
        
        for entry in self.transactions:
            self.add_to_history_ui(entry)

    def delete_and_start_again(self):
        
        confirm = messagebox.askyesno("Confirm Reset" , "Are you sure? This will delete all your data and restart the app.")

        if confirm:

            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)

            self.current_balance = 0.0
            self.transactions = []
            self.user_categories = []

            for widget in self.winfo_children():
                widget.destroy()

            self.withdraw()
            self.show_onboarding()


if __name__ == "__main__":
    app = BudgetApp()
    app.mainloop()