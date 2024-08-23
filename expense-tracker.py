import time
import argparse
import pandas as pd
from pathlib import Path
import csv
import subprocess

csv_filename = Path(Path(__file__).parent,"Expense Tracker.csv")
budget_store = Path(Path(__file__).parent,"budget.txt")

def main():
    check_file_exists()
    args = arg_parser()
    arg_sort(args)
    
def arg_parser():
    parser = argparse.ArgumentParser(description="A tool to manage expenses")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    add_parser = subparsers.add_parser("add", help="Add a specific amount")
    add_parser.add_argument("description", type=str, help="Description of expense")
    add_parser.add_argument("amount", type=int, help="Amount of expense")
    add_parser.add_argument("-c", "--category",type=str, default="none", help="Category of expense")

    list_parser = subparsers.add_parser("list", help="Display list of expenses")
    list_parser.add_argument("-m", "--month", type=int, default=None, help="Specify a month for the list")

    summary_parser = subparsers.add_parser("summary", help="Summary of expenses")
    summary_parser.add_argument("-m", "--month", type=int, default=None, help="Specify a month for the summary")

    delete_parser = subparsers.add_parser("delete", help="Delete expense by ID number")
    delete_parser.add_argument("task_id", type=int, help="ID of the transaction to delete")

    update_parser = subparsers.add_parser("update", help="Update expense")
    update_parser.add_argument("task_id", type=int, help="Task ID to update")
    update_parser.add_argument("-d", "--description", type=str, help="New description")
    update_parser.add_argument("-a", "--amount", type=int, help="New amount")
    update_parser.add_argument("-c", "--category", type=str, help="Update the category of a task")

    budget_parser = subparsers.add_parser("budget", help="Set or view budget")
    budget_parser.add_argument("-s", "--set", type=int, help="Set a monthly budget")

    export_csv_parser = subparsers.add_parser("export", help="Export CSV")
    export_csv_parser.add_argument("directory", type=str, help="Directory to export to")

    return parser.parse_args()

def arg_sort(args):

    if args.command == "add":
        add_expense(args)
    elif args.command == "list":
        list_expense(args)
    elif args.command == "summary":
        summary_expense(args)
    elif args.command == "delete":
        delete_expense(args)
    elif args.command == "update":
        update_expense(args)
    elif args.command == "budget":
        budget_expense(args)
    elif args.command == "export":
        export_csv(args)

def add_expense(args):
    timestr = time.strftime("%m-%d-%Y")
    next_id = get_id()
    data = [
            [next_id, args.description, args.amount, args.category, timestr]
        ]
    with open(csv_filename, 'a', newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)
    print(f"# Expense added successfully (ID: {next_id})")

def list_expense(args):
    if args.month != None:
        i = 0
        with open(csv_filename, 'r') as file:
            df = pd.read_csv(file)
        dates = df[['Date']].to_string(index=False, header=False).split()
        while i < len(dates):
            x = dates[i][:2].replace('0','')
            if int(x) == args.month:
                print(df.iloc[i].to_string())
                print("-------------------------")
            i += 1
    else:
        with open(csv_filename, 'r') as file:
            df = pd.read_csv(file)
        print(df.to_string(index=False))

def summary_expense(args):
    if args.month != None:
        i = 0
        month_total = 0
        with open(csv_filename, 'r') as file:
            df = pd.read_csv(file)
        dates = df[['Date']].to_string(index=False, header=False).split()
        while i < len(dates):
            x = dates[i][:2].replace('0','')
            if int(x) == args.month:
                month_total += df.iat[i, 2]
            i += 1
        print(f"Total expenses for the month of {get_month(args.month)}: ${month_total}")
    else:
        with open(csv_filename, 'r') as file:
            df = pd.read_csv(file)
        print(f"# Total expenses: ${df['Amount'].sum()}")
        
def delete_expense(args):
    with open(csv_filename, 'r') as file:
            df = pd.read_csv(file)
    df = df.drop([args.task_id - 1])
    df.to_csv(csv_filename, index=False)

def update_expense(args):
    with open(csv_filename, 'r') as file:
        df = pd.read_csv(file)
        if args.description != None:
            df.iat[args.task_id - 1, 1] = args.description
        if args.amount != None:
            df.iat[args.task_id - 1, 2] = args.amount
        if args.category != None:
            df.iat[args.task_id - 1, 3] = args.category
    df.to_csv(csv_filename, index=False)

def budget_expense(args):
    if args.set != None:
        with open(budget_store, 'r+') as file:
            file.write(str(args.set))
        print(f"# Monthly budget is set to : {args.set}")
    else:
        current_month = time.strftime("%m")
        i = 0
        month_total = 0
        with open(csv_filename, 'r') as file:
            df = pd.read_csv(file)
        dates = df[['Date']].to_string(index=False, header=False).split()
        while i < len(dates):
            x = dates[i][:2].replace('0','')
            if int(x) == int(current_month):
                month_total += df.iat[i, 2]
            i += 1
        print(f"# You have current spent ${month_total} of your ${get_budget()} monthly budget for the month of {get_month(int(current_month))}")

def export_csv(args):
    file = open(csv_filename, "r")
    export = open(Path(args.dir, "w"))
    export.write(file)
    file.close()
    export.close()
                  
def check_file_exists():
    if csv_filename.is_file():
        pass
    else:
        data = [
            ["ID", "Description", "Amount", "Category", "Date"]
        ]
        with open(csv_filename, 'x', newline="") as file:
            writer = csv.writer(file)
            writer.writerows(data)
    if budget_store.is_file():
        return
    else:
        with open(budget_store, 'x') as file:
            file.write("")
        subprocess.run(["attrib", "+H", budget_store], check=True)
    return

def get_id():
    id = 1
    with open(csv_filename, 'r') as file:
        df = pd.read_csv(file)
        for index in df.ID:
            id += 1
    return id

def get_budget():
    with open(budget_store, 'r') as file:
        x = file.read().strip()
        return int(x)

def get_month(month):
    if month == 1:
        return 'January'
    elif month == 2:
        return 'February'
    elif month == 3:
        return 'March'
    elif month == 4:
        return 'April'
    elif month == 5:
        return 'May'
    elif month == 6:
        return 'June'
    elif month == 7:
        return 'July'
    elif month == 8:
        return 'August'
    elif month == 9:
        return 'September'
    elif month == 10:
        return 'October'
    elif month == 11:
        return 'November'
    elif month == 12:
        return 'December'

if __name__ == "__main__":
    main()