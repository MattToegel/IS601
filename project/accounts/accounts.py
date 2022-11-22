from sql.db import DB
from flask import flash
def get_or_create_account(user_id):
    account = {"id":-1, "balance":0}
    try:
        result = DB.selectOne("SELECT id, balance FROM IS601_S_Accounts WHERE user_id = %s", user_id)
        if result.status and result.row:
            account["id"] = result.row["id"]
            account["balance"] = result.row["balance"]
            return account
    except Exception as e:
        print("Error getting account" ,e)
        flash("Error fetching account", "danger")
    try:
        result = DB.insertOne("INSERT INTO IS601_S_Accounts (user_id) values (%s)", user_id)
        if result.status:
            account["id"] = DB.db.fetch_eof_status()["insert_id"]
            flash("Account created", "success")
            return account
    except Exception as e:
        print("error creating account", e)
        flash("Error creating account", "danger")
    return None # shouldn't occur