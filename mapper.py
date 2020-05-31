from models.user import User
from models.product import Product
from models.address import Address
from models.payment import Payment
from models.order import Order
from models.order_confirmation import OrderConfirmation
from util import *


def convert_signup_form(signup_form):
    user = User(email = signup_form.email.data,
                first_name = signup_form.first_name.data,
                last_name = signup_form.last_name.data,
                password = signup_form.password.data)
    return user


def convert_to_product_from(product_registration_form, seller_id):
    new_product = Product(name=product_registration_form.name.data,
                          category=product_registration_form.category.data,
                          is_biddable=str_to_bool(product_registration_form.is_biddable.data),
                          base_price=product_registration_form.base_price.data,
                          product_image=product_registration_form.article_image.data.filename,
                          end_day=product_registration_form.bid_end_day.data,
                          end_time=product_registration_form.bid_end_time.data,
                          description=product_registration_form.description.data,
                          seller_id=seller_id
                          )
    return new_product


def convert_to_address_from(order_form, user_id):

    new_address = Address(address_name=order_form.address_name.data,
                          address_1=order_form.address_1.data,
                          address_2=order_form.address_2.data,
                          city=order_form.city.data,
                          state=order_form.state.data,
                          zip_code=order_form.zip_code.data
                          )
    return new_address


def convert_to_payment_from(order_form, user_id):

    new_payment = Payment(name=order_form.payment_name.data,
                          year=order_form.year.data,
                          month=order_form.month.data,
                          card_no=order_form.card_number.data,
                          payment_type=order_form.payment_type.data,
                          payment_user_id=user_id,
                          name_on_card=order_form.name_on_card.data
                          )
    return new_payment


def convert_to_order_from(product_id, payment_id, address_id, bid_id):
    new_order = Order(product_id=product_id,
                      payment_id=payment_id,
                      address_id=address_id,
                      bid_id=bid_id
                      )
    return new_order

def convert_to_order_confirmation_from(product_id, payment_id, address_id, user_id, order_id, amount):
    new_order = OrderConfirmation(product_id=product_id,
                                  payment_id=payment_id,
                                  address_id=address_id,
                                  user_id=user_id,
                                  order_id=order_id,
                                  amount=amount
                                 )
    return new_order