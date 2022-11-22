from flask import flash


def handle_duplicate_column(error):
    if "UNIQUE constraint" in error:
        col = error.split(".")[1]
        flash(f"{col.capitalize()} already exists, please try another", "warning")
        return True
    return False
