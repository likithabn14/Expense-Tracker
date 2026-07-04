from flask import Flask, render_template, request, redirect, send_file
import pandas as pd
from datetime import date
import os

app = Flask(__name__)

CSV_FILE = "expenses.csv"

# ---------------- CREATE CSV ----------------

if not os.path.exists(CSV_FILE):

    df = pd.DataFrame(columns=[
        "Date",
        "Category",
        "Description",
        "Amount"
    ])

    df.to_csv(CSV_FILE, index=False)


# ---------------- HOME ----------------

@app.route("/")
def home():

    df = pd.read_csv(CSV_FILE)

    if df.empty:

        total = 0
        highest = 0
        lowest = 0
        average = 0
        count = 0

        top_category = "None"
        top_category_total = 0

        highest_category = "-"
        highest_description = "-"

        lowest_category = "-"
        lowest_description = "-"

    else:

        total = float(df["Amount"].sum())
        highest = float(df["Amount"].max())
        lowest = float(df["Amount"].min())
        average = round(float(df["Amount"].mean()),2)
        count = len(df)

        category_summary = df.groupby("Category")["Amount"].sum()

        top_category = category_summary.idxmax()

        top_category_total = float(category_summary.max())

        highest_row = df.loc[df["Amount"].idxmax()]

        highest_category = highest_row["Category"]
        highest_description = highest_row["Description"]

        lowest_row = df.loc[df["Amount"].idxmin()]

        lowest_category = lowest_row["Category"]
        lowest_description = lowest_row["Description"]

    search = request.args.get("category","All")

    if search != "All":

        display_df = df[df["Category"] == search]

    else:

        display_df = df

    return render_template(

        "index.html",

        expenses=display_df.reset_index().to_dict(orient="records"),

        total=f"{total:,.2f}",

        highest=f"{highest:,.2f}",

        lowest=f"{lowest:,.2f}",

        average=f"{average:,.2f}",

        count=count,

        top_category=top_category,

        top_category_total=f"{top_category_total:,.2f}",

        highest_category=highest_category,

        highest_description=highest_description,

        lowest_category=lowest_category,

        lowest_description=lowest_description,

        today=date.today().strftime("%Y-%m-%d"),

        search=search

    )


# ---------------- ADD EXPENSE ----------------

@app.route("/add", methods=["POST"])
def add_expense():

    expense_date = request.form["date"]

    amount = float(request.form["amount"])

    category = request.form["category"]

    if category == "Other":

        custom = request.form["custom_category"].strip()

        if custom:

            category = custom

    description = request.form["description"]

    new_row = pd.DataFrame({

        "Date":[expense_date],

        "Category":[category],

        "Description":[description],

        "Amount":[amount]

    })

    df = pd.read_csv(CSV_FILE)

    df = pd.concat([df,new_row],ignore_index=True)

    df.to_csv(CSV_FILE,index=False)

    return redirect("/")


# ---------------- DELETE ----------------

@app.route("/delete/<int:index>")
def delete(index):

    df = pd.read_csv(CSV_FILE)

    if index < len(df):

        df = df.drop(index)

        df.reset_index(drop=True,inplace=True)

        df.to_csv(CSV_FILE,index=False)

    return redirect("/")
# ---------------- EDIT EXPENSE ----------------

@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit(index):

    df = pd.read_csv(CSV_FILE)

    if index >= len(df):
        return redirect("/")

    expense = df.iloc[index]

    if request.method == "POST":

        expense_date = request.form["date"]

        amount = float(request.form["amount"])

        category = request.form["category"]

        if category == "Other":

            custom = request.form["custom_category"].strip()

            if custom:
                category = custom

        description = request.form["description"]

        df.at[index, "Date"] = expense_date
        df.at[index, "Category"] = category
        df.at[index, "Description"] = description
        df.at[index, "Amount"] = amount

        df.to_csv(CSV_FILE, index=False)

        return redirect("/")

    return render_template(
        "edit.html",
        expense=expense,
        index=index
    )


# ---------------- DOWNLOAD CSV ----------------

@app.route("/download")
def download():

    return send_file(
        CSV_FILE,
        as_attachment=True,
        download_name="expenses.csv"
    )


# ---------------- RESET ----------------

@app.route("/reset")
def reset():

    df = pd.DataFrame(columns=[
        "Date",
        "Category",
        "Description",
        "Amount"
    ])

    df.to_csv(CSV_FILE, index=False)

    return redirect("/")


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)