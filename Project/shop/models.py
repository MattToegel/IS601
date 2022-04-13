from base_model import db
from sqlalchemy import CheckConstraint
from sqlalchemy.exc import SQLAlchemyError


class Item(db.Model):
    name = db.Column(db.String(30), index=True, unique=True)
    description = db.Column(db.Text, default="")
    cost = db.Column(db.Integer, default=0)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.Text, default="https://via.placeholder.com/100")
    CheckConstraint("cost >= 0", name="cost_check")
    CheckConstraint("stock >= 0", name="stock_check")
    carts = db.relationship("Cart", back_populates="item")


class Cart(db.Model):
    __table_args__ = (db.UniqueConstraint('user_id', 'item_id'),)
    item_id = db.Column(db.Integer, db.ForeignKey("is601_item.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("is601_user.id"))
    quantity = db.Column(db.Integer)
    item = db.relationship("Item", back_populates="carts", uselist=False)

    @staticmethod
    def add_to_cart(item_id, user_id, q_to_add=1):
        # since not all DBs support INSERT ... ON DUPLICATE UPDATE...
        # I'll implement a basic hack to do it at the cost of 3 queries if a duplicate is thrown
        # definitely not ideal, but it does the job
        cart = Cart(user_id=user_id, quantity=q_to_add)
        item = Item.query.get(item_id)
        cart.item = item
        print(cart.item)
        print(cart.__dict__)
        db.session.add(cart)
        try:
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            print("Potential duplicate")
            print(e)
            cart = Cart.query.filter(Cart.item_id == item_id, Cart.user_id == user_id).first()
            print(cart)
            if cart is not None:
                cart.quantity += int(q_to_add)
                # no need to add to session as the db is aware of it from the select/fetch above
                # db.session.add(cart)
                try:
                    db.session.commit()
                    return True
                except SQLAlchemyError as e:
                    print("Error updating cart")
                    print(e)
                    return False
            return False

    @staticmethod
    def get_user_cart(user_id):
        return Cart.query.filter(Cart.user_id == user_id).all()


# replicating item data in case an item is later removed we still maintain the order history
class OrderHistory(db.Model):
    order_id = db.Column(db.Integer)  # manually increment this
    name = db.Column(db.String(30), index=True)
    description = db.Column(db.Text, default="")
    cost = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)
    image = db.Column(db.Text, default="https://via.placeholder.com/100")
    user_id = db.Column(db.Integer, db.ForeignKey("is601_user.id"))
    user = db.relationship("User", back_populates="orders")

    def map_cart_item(self, cart_item, order_id, user):
        self.order_id = order_id
        self.name = cart_item.item.name
        self.description = cart_item.item.description
        self.cost = cart_item.item.cost
        self.quantity = cart_item.quantity
        self.image = cart_item.item.image
        self.user = user
        db.session.add(self)
