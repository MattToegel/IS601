from flask import Blueprint, flash, render_template, request, url_for
from flask_principal import Permission, RoleNeed
from sqlalchemy.exc import SQLAlchemyError

from admin.forms import CreateRoleForm
from auth.models import Role, User, UserRoles
from base_model import db
from helpers import handle_duplicate_column
from werkzeug.utils import redirect

admin = Blueprint('admin', __name__, template_folder='templates', url_prefix='/admin')

# Create a permission with a single Need, in this case a RoleNeed.
admin_permission = Permission(RoleNeed('Admin'))


@admin.route("/roles/create", methods=["GET", "POST"])
@admin_permission.require(403)
def create_role():
    form = CreateRoleForm()
    if form.validate_on_submit():
        role = Role()
        form.populate_obj(obj=role)
        db.session.add(role)
        try:
            db.session.commit()
            flash("Successfully created role {}".format(role.name), "success")
        except SQLAlchemyError as e:
            print(e)
            handle_duplicate_column(str(e.orig))
            db.session.rollback()
    return render_template("create_role.html", form=form)


@admin.route("/roles/list", methods=["GET"])
@admin_permission.require(403)
def list_roles():
    roles = Role.query.all()
    return render_template("list_roles.html", roles=roles)


@admin.route("/role/delete", methods=["POST"])
@admin_permission.require(403)
def delete_role():
    role_id = request.form.get("role_id", 0, type=int)

    if role_id > 0:
        role = Role.query.get(role_id)
        if role.name == "Admin":
            flash("Prevented the deletion of Admin", "danger")
        else:
            for assoc in role.users:
                db.session.delete(assoc)
            db.session.delete(role)
            try:
                db.session.commit()
                flash("Deleted role {}".format(role.name), "success")
            except SQLAlchemyError as e:
                db.session.rollback()
                print(e)
                flash("Error deleting role, check the logs", "danger")
    else:
        flash("Invalid role", "danger")
    return redirect(url_for("admin.list_roles"))


@admin.route("/roles/assign", methods=["GET", "POST"])
@admin_permission.require(403)
def assign_roles():
    if request.method == 'POST':
        role_ids = request.form.getlist("role_id[]")
        user_ids = request.form.getlist("user_id[]")
        print(role_ids)
        print(user_ids)
        users = User.query.filter(User.id.in_(user_ids)).all()
        print(users)
        roles = Role.query.filter(Role.id.in_(role_ids)).all()
        for user in users:
            for role in roles:
                ur = UserRoles()
                ur.role = role
                user.roles.append(ur)
                db.session.add(user)
                try:
                    db.session.commit()
                    flash(f"Added role {role.name} to {user.username}", "success")
                except SQLAlchemyError as e:
                    db.session.rollback()
                    print(e)
                    flash(f"User {user.username} already has role {role.name}", "danger")
    roles = Role.query.all()
    search = request.form.get("username", "")
    if not search:
        # TODO look for query parameter of username
        pass
    if search:
        like_search = "%{}%".format(search)
        users = User.query.filter(User.username.like(like_search)).limit(10).all()
    else:
        users = User.query.limit(10).all()
    return render_template("assign_roles.html", roles=roles, users=users, username=search)


@admin.route("/role/unassign", methods=["POST"])
@admin_permission.require(403)
def unassign_role():
    user_id = request.form.get("user_id", 0, type=int)
    role_id = request.form.get("role_id", 0, type=int)
    search = request.form.get("username", "")
    if user_id <= 0 or role_id <= 0:
        flash("Invalid user or role selected", "danger")
    else:
        user = User.query.get(user_id)
        if not user:
            flash("Error looking up user", "danger")
        else:
            for assoc in user.roles:
                if assoc.role.id == role_id:
                    db.session.delete(assoc)
                    try:
                        db.session.commit()
                        flash(f"Removed role {assoc.role.name} from {user.username}", "success")
                    except SQLAlchemyError as e:
                        print(e)
                        db.session.rollback()
                        flash(f"An error occurred removing the role {assoc.role.name} from {user.username}", "danger")
                    break
    return redirect(url_for("admin.assign_roles", username=search))
