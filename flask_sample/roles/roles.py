from flask import Blueprint, flash, render_template, request, redirect, url_for
from sql.db import DB
from roles.forms import RoleForm
from werkzeug.datastructures import MultiDict
from roles.permissions import admin_permission
roles = Blueprint('roles', __name__, url_prefix='/roles',template_folder='templates')

# uses admin_permission from roles.permissions (flask_principal way)
# https://stackoverflow.com/a/20069821 (for http_exception)

@roles.route("/add", methods=["GET","POST"])
@admin_permission.require(http_exception=403)
def add():
    form = RoleForm()
    if form.validate_on_submit():
        try:
            result = DB.insertOne("INSERT INTO IS601_Roles (name, description, is_active) VALUES (%s, %s, %s)",
            form.name.data, form.description.data, 1 if form.is_active else 0)
            if result.status:
                flash(f"Created role {form.name.data}", "success")
        except Exception as e:
            flash(f"Error creating role {e}", "danger")
    return render_template("role_form.html", form=form, type="Create")

@roles.route("/edit", methods=["GET", "POST"])
@admin_permission.require(http_exception=403)
def edit():
    form = RoleForm()
    id = request.args.get("id")
    if id is None:
        flash("Missing id", "danger")
        return redirect(url_for("roles.list"))
    if form.validate_on_submit() and id:
        try:
            result = DB.insertOne("UPDATE IS601_Roles set name = %s, description = %s, is_active = %s WHERE id = %s",
            form.name.data, form.description.data, 1 if form.is_active.data else 0, id)
            if result.status:
                flash(f"Updated role {form.name.data}", "success")
        except Exception as e:
            flash(f"Error updating role {e}", "danger")
    try:
        result = DB.selectOne("SELECT name, description, is_active from IS601_Roles WHERE id = %s", id)
        if result.status and result.row:
            print(result.row)
            # https://stackoverflow.com/a/37125336
            form = RoleForm(MultiDict(result.row))
    except Exception as e:
        print("Error getting role", e)
        flash("Error looking up role", "danger")
    return render_template("role_form.html", form=form, type="Edit")

@roles.route("/list", methods=["GET"])
@admin_permission.require(http_exception=403)
def list():
    rows = [] 
    try:
        result = DB.selectAll("SELECT id,name, description, is_active FROM IS601_Roles LIMIT 100",)
        if result.status and result.rows:
            rows = result.rows
    except Exception as e:
        print(e)
        flash("Error getting roles", "danger")
    return render_template("roles_list.html", rows=rows)

@roles.route("/delete", methods=["GET"])
@admin_permission.require(http_exception=403)
def delete():
    id = request.args.get("id")
    # make a mutable dict
    args = {**request.args}
    if id:
        try:
            result = DB.delete("DELETE FROM IS601_Roles WHERE id = %s", id)
            if result.status:
                flash("Deleted role", "success")
        except Exception as e:
            print(e)
            # TODO make this user-friendly
            flash(e, "danger")
        # TODO pass along feedback

        # remove the id args since we don't need it in the list route
        # but we want to persist the other query args
        del args["id"]
    else:
        flash("No id present", "warning")
    return redirect(url_for("roles.list", **args))