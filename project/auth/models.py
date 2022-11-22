from flask_login import UserMixin
from common.utils import JsonSerializable
from accounts.models import Account

class User(UserMixin, JsonSerializable):
    def __init__(self, id, email, username, account = Account(), roles = []):
        self.id = id
        self.email = email
        self.username = username
        if type(account) == dict:
            account = Account(**account)
        self.account = account
        # pseudo-serializer for loading from json (map dict role to Role)
        if roles and type(roles[0]) == dict:
            from roles.models import Role
            roles = [Role(**r) for r in roles]
        self.roles = roles
        self.authenticated = False
    def get_account_id(self):
        return self.account.id if self.account else -1
    def get_balance(self):
        return self.account.balance if self.account else 0
    def is_active(self):
        return self.is_active()
    def is_anonymous(self):
        return False
    def is_authenticated(self):
        return self.authenticated
    def is_active(self):
        return True
    def get_id(self):
        return str(self.id)
    # usable in templates and views to check if user has a role
    def has_role(self, role):
        for r in self.roles:
            if r.name in [role, "Admin"]: # if has Admin role, always allow
                return True
        return False
    def has_one_of_roles(self, roles):
        _roles = [list(roles), "Admin"]
        for r in self.roles:
            if r.name in _roles:
                return True
        return False