
# "render_template" lets us show HTML pages
# "request" lets us read data the user typed into a form
# "redirect" and "url_for" send the user to a different page
from flask import Flask, render_template, request, redirect, url_for
import json  # json lets us save/load data from a file
import os    # os lets us check if a file exists on the computer


app = Flask(__name__)


#  We use a simple .json file instead of a database.
#  It works like a text file that saves a list of transactions.

DATA_FILE = "transactions.json" #Saving the name of the file in this varialble 


#  FUNCTION 1: Load transactions from the file
#  Every time we need the list of transactions, we call this.

def load_transactions():
    # Check if the file exists yet
    if not os.path.exists(DATA_FILE):
        return []  # Return an empty list if no file found

    # Open the file and read it
    with open(DATA_FILE, "r") as file:
        transactions = json.load(file)  # Convert file text -> Python list

    return transactions


#  FUNCTION 2: Save transactions to the file
#  Every time we add or delete, we save the updated list.

def save_transactions(transactions):
    # Open the file and write to it
    
    with open(DATA_FILE, "w") as file:
        json.dump(transactions, file)  # Convert Python list -> file text


#  FUNCTION 3: Calculate totals
#  Adds up all the numbers to get balance, income, expenses

def get_totals(transactions):
    total_income   = 0
    total_expenses = 0

    for t in transactions:
        if t["amount"] > 0:
            # Positive number = income
            total_income = total_income + t["amount"]
        else:
            # Negative number = expense
            total_expenses = total_expenses + t["amount"]

    # Balance = income + expenses (expenses are already negative)
    balance = total_income + total_expenses

    return balance, total_income, total_expenses


#  FUNCTION 4: Format a number as PKR currency
#  Example: 15000  ->  "PKR 15,000.00"
#  Example: -3000  ->  "PKR 3,000.00"

def format_money(amount):
    if amount < 0:
        return f"PKR {abs(amount):,.2f}"
    else:
        return f"PKR {amount:,.2f}"


#  ROUTE 1: Home Page  (shows the tracker)

@app.route("/")
def home():
    # Load all saved transactions from the file
    transactions = load_transactions()

    # Calculate the totals
    balance, total_income, total_expenses = get_totals(transactions)

    # Format the numbers as nice currency strings
    balance_text  = format_money(balance)
    income_text   = format_money(total_income)
    expense_text  = format_money(total_expenses)

    # Build a display-ready version of each transaction
    # We add "css_class" and "amount_text" so the HTML template stays simple and it just prints these values, no logic needed.
    display_transactions = []
    for t in reversed(transactions):  # reversed = newest first
        if t["amount"] > 0:
            css_class   = "income"
        else:
            css_class   = "expense"

        display_transactions.append({
            "id":          t["id"],
            "description": t["description"],
            "amount":      t["amount"],
            "amount_text": format_money(t["amount"]),  # e.g. "PKR 5,000.00"
            "css_class":   css_class,                  # "income" or "expense"
        })

    # Show the HTML page and pass our data into it
    # The HTML file can use these variables like {{ balance }}
    return render_template(
        "index.html",
        transactions = display_transactions,  # the list of all transactions
        balance      = balance_text,          # e.g. "PKR 35,000.00"
        income       = income_text,           # e.g. "PKR 50,000.00"
        expenses     = expense_text,          # e.g. "-PKR 15,000.00"
    )


#  ROUTE 2: Add a Transaction
#  When the user fills in the form and clicks "Add Transaction"
#  the form sends data here (POST request to /add)
@app.route("/add", methods=["POST"])
def add():
    # Read what the user typed into the form fields
    # request.form["name"] matches the input's name="" attribute in HTML
    description = request.form["description"]
    amount      = float(request.form["amount"])  # Convert text -> number

    # Load the existing transactions list from the file
    transactions = load_transactions()

    # Create a new transaction as a Python dictionary
    # We use the length of the list + 1 as a simple unique ID
    new_transaction = {
        "id":          len(transactions) + 1,
        "description": description,
        "amount":      amount,
    }

    # Add the new transaction to the list
    transactions.append(new_transaction)

    # Save the updated list back to the file
    save_transactions(transactions)

    # Send the user back to the home page to see the updated list
    return redirect(url_for("home"))


#  ROUTE 3: Delete a Transaction
#  When the user clicks the delete button next to a transaction
#  it sends them to /delete/3  (where 3 is the transaction's id)
@app.route("/delete/<int:transaction_id>")
def delete(transaction_id):
    # Load the existing transactions list from the file
    transactions = load_transactions()

    # Build a NEW list that includes everything EXCEPT the one to delete
    updated_transactions = []
    for t in transactions:
        if t["id"] != transaction_id:
            updated_transactions.append(t)

    # Save the filtered list back to the file
    save_transactions(updated_transactions)

    # Send the user back to the home page
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
