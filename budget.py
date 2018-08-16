#!/usr/bin/python

import numpy as np
from currency_converter import CurrencyConverter
import csv
import datetime
import re
import os
from dateutil.relativedelta import relativedelta
from blessings import Terminal
import operator

term = Terminal()
c = CurrencyConverter()

categories = [["rent", "electricity", "heating", "utilities"], ["car", "public", "taxi"], ["groceries", "health", "supplies"], ["clothes", "cosmetics", "eating out", "electronics", "entertainment", "gifts", "software"], ["flights", "hotels"], ["building", "tip jar"]]



def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def show_accounts():
    for key in accounts:
        print accounts[key][0] + ": " + str(accounts[key][2]) + " " + accounts[key][1]

    sum = 0
    for key in accounts:
        if accounts[key][1] != "EUR":
            sum = sum + c.convert(accounts[key][2], accounts[key][1])
        else:
            sum = sum + accounts[key][2]

    print "TOTAL: " + "{0:.2f}".format(sum) + " EUR"

def show_account(account):
    print accounts[account][0] + ": " + str(accounts[account][2]) + " " + accounts[account][1]

def show_help():
    print "You can try the following commands:"
    print ""
    print term.bold_green("show accounts") + " to show all accounts with their respective balance"
    print term.bold_green("show <account key>") + " to show a specific account"
    print ""
    print term.bold_green("show categories") + " to show all available categories"
    print term.bold_green("add category") + " to add a new category"
    print term.bold_green("remove category") + " to remove a category"
    print ""
    print term.bold_green("new") + " to add a new transaction"
    print term.bold_green("show past <n> transactions") + " to show the past <n> transactions, where <n> is an integer"
    print term.bold_green("show transactions") + " to show transactions in a certain time frame"
    print term.bold_green("balance") + " to show the balance"
    print term.bold_green("test") + " to add a default transaction for testing purposes"
    print ""
    print term.bold_green("quit") + " to quit the program"

def show_categories():
    col_width = max(len(word) for cat in categories for word in cat) + 2
    for cat in categories:
        print "".join(word.ljust(col_width) for word in cat)

def add_category(cat, pos):
    categories[pos].append(cat)

def remove_category(word):
    for cat in categories:
        try:
            cat.remove(word)
            print "Successfully removed."
        except:
            pass

def find_date():
    date_word = raw_input("Booking Date: ")
    now = datetime.datetime.now()

    if date_word == "today":
        date = now.strftime("%d.%m.%Y")

    elif date_word == "yesterday":
        diff = 1
        date = (now - relativedelta(days=diff)).strftime("%d.%m.%Y")

    elif re.match(r"\d+ days ago", date_word):
        diff = re.findall(r"\d+", date_word)
        diff = int(diff[0])
        date = (now - relativedelta(days=diff)).strftime("%d.%m.%Y")

    elif re.match(r"\d+ weeks ago", date_word):
        diff = re.findall(r"\d+", date_word)
        diff = int(diff[0])
        date = (now - relativedelta(weeks=diff)).strftime("%d.%m.%Y")

    else:
        while True:
            try:
                date = datetime.datetime.strptime(date_word,"%d.%m.%Y")
                date = date.strftime("%d.%m.%Y")
                break
            except ValueError:
                print "Incorrect format."
                # date_word = raw_input("Booking Date: ")

    return date

def check_balance():
    accounts = {}
    account_names = []

    bfile = open("balance.csv", "r")
    with bfile:
        reader = csv.reader(bfile, delimiter="\t")
        for row in reader:
            if row[0] not in account_names:
                account_names.append(row[0])

    for account in account_names:
        accounts.update(check_account(account))
        # accounts.update({row[0]: [row[1], row[2], float(row[3]), row[4]]})
    return accounts

def check_account(account):
    # print "Checking current balance"
    bfile = open("balance.csv", "r")
    accounts = {}

    datetimes = []
    tfile = open("transactions.csv", "r+")
    with tfile:
        reader = csv.reader(tfile, delimiter="\t")
        for row in reader:
            if row[1] == account:
                datetimes.append(row[0])

    most_recent = min(datetimes)
    with bfile:
        reader = csv.reader(bfile, delimiter="\t")
        for row in reader:
            if row[0] == account:
                if row[4] > most_recent:
                    accounts.update({row[0]: [row[1], row[2], float(row[3]), row[4]]})
                    most_recent = row[4]
    # print "Old: " + str(accounts)
    return accounts

def update_balance(account, amount, date):
    current_account_stat = check_account(account)
    current_balance = current_account_stat[account][2]

    bfile = open("balance.csv", "a+")
    with bfile:
        writer = csv.writer(bfile, delimiter="\t")
        new_amount = "{0:.2f}".format(current_balance + amount)
        balance = [account, current_account_stat[account][0], current_account_stat[account][1], new_amount, date]
        writer.writerow(balance)

    # bfile = open("balance.csv", "w+")
    # with bfile:
    #     writer = csv.writer(bfile, delimiter="\t")
    #     for row in writer:
    #         if row[0] == account:
    #             if row[4] >= date:
    #                 corrected_amount = "{0:.2f}".format(row[3] + amount)
    #                 balance = [account, current_account_stat[account][0], current_account_stat[account][1], corrected_amount, date]
    #                 writer.writerow(balance)

def new_transaction():

    while True:
        try:
            amount = float(raw_input("Amount: "))
            break
        except ValueError:
            print "Invalid number."

    print "Available accounts: " + ",".join(account_names)
    account = raw_input("Account: ")

    print "Available categories: "
    show_categories()
    category = raw_input("Category: ")

    date = find_date()

    transaction = [date, account, amount, category]

    try:
        tfile = open("transactions.csv", "a+")
        with tfile:
            writer = csv.writer(tfile, delimiter="\t")
            writer.writerow(transaction)

        update_balance(transaction[1], transaction[2], transaction[0])

        print "Successfully added."
    except:
        print "Error. Try again."

def show_transactions(n=100):
    tfile = open("transactions.csv", "r")
    counter = 0
    with tfile:
        reader = csv.reader(tfile, delimiter="\t")
        for row in reader:
            while counter < n:
                print ", ".join(row)
                counter += 1

def get_timeframe():
    date_word = raw_input("Timeframe: ")
    now = datetime.datetime.now()

    datetimes = []
    tfile = open("transactions.csv", "r+")
    with tfile:
        reader = csv.reader(tfile, delimiter="\t")
        for row in reader:
            datetimes.append(row[0])

    if date_word == "today":
        border = now.strftime("%d.%m.%Y")
        # oldest =

    elif date_word == "yesterday":
        diff = 1
        border = (now - relativedelta(days=diff)).strftime("%d.%m.%Y")

    elif re.match(r"last \d+ days", date_word):
        diff = re.findall(r"\d+", date_word)
        diff = int(diff[0])
        border = (now - relativedelta(days=diff)).strftime("%d.%m.%Y")

    elif date_word == "last week":
        diff = 1
        border = (now - relativedelta(weeks=diff)).strftime("%d.%m.%Y")

    elif re.match(r"last \d+ weeks", date_word):
        diff = re.findall(r"\d+", date_word)
        diff = int(diff[0])
        border = (now - relativedelta(weeks=diff)).strftime("%d.%m.%Y")

    elif date_word == "last month":
        diff = 1
        border = (now - relativedelta(month=diff)).strftime("%d.%m.%Y")

    elif re.match(r"last \d+ months", date_word):
        diff = re.findall(r"\d+", date_word)
        diff = int(diff[0])
        border = (now - relativedelta(months=diff)).strftime("%d.%m.%Y")

    elif date_word == "last year":
        diff = 1
        border = (now - relativedelta(year=diff)).strftime("%d.%m.%Y")

    elif re.match(r"last \d+ years", date_word):
        diff = re.findall(r"\d+", date_word)
        diff = int(diff[0])
        border = (now - relativedelta(years=diff)).strftime("%d.%m.%Y")

    else:
        border = min(datetimes)

    above_border = []
    for date in datetimes:
        if datetime.datetime.strptime(date,"%d.%m.%Y") >= datetime.datetime.strptime(border,"%d.%m.%Y"):
            above_border.append(datetime.datetime.strptime(date,"%d.%m.%Y"))
    try:
        oldest = min(above_border)
    except ValueError:
        print "Some kind of error."
        oldest = min(datetimes)
    # print oldest
    return oldest

def show_transactions_from_date(oldest):
    transactions = []
    tfile = open("transactions.csv", "r+")
    with tfile:
        reader = csv.reader(tfile, delimiter="\t")
        for row in reader:
            if datetime.datetime.strptime(row[0],"%d.%m.%Y") >= oldest:
                # transactions.append(row)
                print ", ".join(row)


entry = "start"
cls()
print term.black_on_bright_yellow("Haushaltsbuch")
print ""
print "Welcome to the accounting app."
print "Would you like to add a new transaction ('new'), see all accounts ('show accounts') or categories ('show categories')? For more help, type 'help'."
print ""

while entry != "quit":

    accounts = check_balance()
    account_names = list(accounts.keys())

    entry = raw_input("")
    cls()
    if entry == "show accounts":
        show_accounts()

    for account_name in account_names:
        if entry == "show " + account_name:
            show_account(account_name)

    if entry == "help":
        show_help()

    if entry == "show categories":
        show_categories()

    if entry == "add category":
        cat = raw_input("New category: ")
        pos = int(raw_input("Position: (1: Appt, 2: Transport, 3: Home, 4: Things, 5: Travel, 6: Savings)"))
        add_category(cat, pos)

    if entry == "remove category":
        remove_category(raw_input("Remove category: "))

    if entry == "new":
        new_transaction()

    if entry == "balance":
        print check_balance()

    if entry == "test":
        # update_balance("n26", 1000)
        check_account("n26")

    if re.match(r"show past \d+ transactions", entry):
        n = re.findall(r"\d+", entry)
        n = int(n[0])
        show_transactions(n)

    if entry == "show transactions":
        oldest = get_timeframe()
        show_transactions_from_date(oldest)

    # if entry == "show"
