# import the Flask class from the flask module
from flask import Flask, render_template,request,redirect, url_for,session
from flaskext.mysql import MySQL
from forms.login_form import LoginForm
from forms.order_form import OrderForm
from forms.search_form import SearchForm
from forms.signup_form import SignupForm
from forms.product_registration_form import ProductRegistrationForm
from models.product import Product
from models.user import User
from models.bid import Bid
from models import db
from util import *
from mapper import *
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
import datetime


# create the application object
app = Flask(__name__)
app.config['SECRET_KEY'] = 'very very secret'
# app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:jaypatel@localhost/bidding-app'
# db = SQLAlchemy()
db.init_app(app)
db.app = app

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


def evaluate_bids():
    products = Product.query.filter_by(is_biddable=True).all()
    print("-----------------")
    for product in products:
        if(datetime.datetime.combine(product.end_day, product.end_time) > datetime.datetime.now()):
            bids = Bid.query.filter_by(product_id=product.product_id).all()
            print(product.product_id)
            if (len(bids) > 0):
                max_amount = 0
                max_bidder_user_id = None
                bid_id = None
                for bid in bids:
                    if(bid.bid_amount > max_amount):
                        max_amount = bid.bid_amount
                        max_bidder_user_id = bid.bidder_id
                        bid_id = bid.bid_id
                print(max_bidder_user_id)
                print(max_amount)
                print('selected_bid_id: ' + str(bid_id))
            #     add same bid and product to final_confirmation and mark the product not active
            else:
                print('marking product for not bidding')

    print("-----------------")
    db.session.commit()

def invalid_confirm_password(password, confirm_password):
    if not password or not confirm_password:
        return True
    elif confirm_password != password:
        return True
    else:
        return False


@app.route('/')
def home():
    products = Product.query.order_by(Product.product_id.desc()).limit(5).all()
    return render_template('home.html', title='Home | Bidding App', session=session.get('username'),
                           products=products, search_form=SearchForm())


@app.route('/login', methods=['GET','POST'])
def login():
    if session.get('username'):
        return redirect(url_for('home'))
    login_form = LoginForm()
    if request.method =='POST':
        if login_form.validate_on_submit():
            user = User.query.filter_by(email=login_form.username.data, password=login_form.password.data).first()
            if user is None:
                return redirect(url_for('login'))
            else:
                session['username'] = login_form.username.data
                return redirect(url_for('home'))

    return render_template('login.html',
                    title='Login | Bidding App',
                    login_form=login_form,
                    session=session.get('username'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

def create_user(signup_form):
    new_user = convert_signup_form(signup_form)
    db.session.add(new_user)
    db.session.commit()


@app.route('/signup', methods=['GET','POST'])
def signup():
    if session.get('username'):
        return redirect(url_for('index'))
    signup_form = SignupForm()
    if request.method =='POST':
        if signup_form.validate_on_submit():
            user = User.query.filter_by(email=signup_form.email.data).first()
            if user:
                print('user already exists!')
                return render_template("signup.html", error="Username is already taken", signup_form=signup_form,
                                       title='Signup | Bidding App', session=session.get('username'))
            else:
                create_user(signup_form)
                session['username'] = signup_form.email.data
                return redirect(url_for('home'))
        else:
            return render_template("signup.html", signup_form=signup_form,
                                   title='Signup | Bidding App',
                                   session=session.get('username'))
    return render_template('signup.html',
                           signup_form=signup_form,
                           title='Signup | Bidding App',
                           session=session.get('username'))


@app.route('/product-registration', methods = ['GET','POST'])
def product_registration():
    product_registration_form = ProductRegistrationForm()
    if request.method == 'POST':
        if product_registration_form.validate_on_submit():
            current_user = User.query.filter_by(email=session.get('username')).first()
            # end_day = product_registration_form.bid_end_day.data
            if current_user is not None:
                new_product = convert_to_product_from(product_registration_form, current_user.email)
                # TODO: remove this
                # new_product = Product(name=product_registration_form.name.data,
                #                         category=product_registration_form.category.data,
                #                         is_biddable=str_to_bool(product_registration_form.is_biddable.data),
                #                         base_price=product_registration_form.base_price.data,
                #                         product_image="name",
                #                         end_day=end_day,
                #                         end_time=product_registration_form.bid_end_time.data,
                #                         description=product_registration_form.description.data,
                #                         seller_id=current_user.email
                #                       )
                db.session.add(new_product)
                db.session.flush()
                product_registration_form.article_image.data.save('static/product_images/' + product_registration_form.article_image.data.filename)
                product_id = new_product.product_id
                db.session.commit()
                # return render_template('product_registration_success.html', product_id=new_product.product_id)
                session['from_page'] = 'successful_product_registration'
                session['product_id'] = product_id
                return redirect(url_for('product_registration_success'))
    else:
        return render_template('product_registration.html', product_registration_form=product_registration_form)

@app.route('/product-detail', methods = ['GET', 'POST'])
def product_details():
    if request.method == 'POST':
        user = User.query.filter_by(email=session.get('username')).first()
        new_bid = Bid(product_id=request.form.get('product_id'), bidder_id=user.email, bid_amount=request.form['bid_amount'])
        db.session.add(new_bid)
        db.session.flush()
        bid_id = new_bid.bid_id
        db.session.commit()
        product = Product.query.filter_by(product_id=request.form.get('product_id')).first()
        session['from_page'] = 'product_detail'
        session['product_id'] = product.product_id
        session['bid_id'] = bid_id
        return redirect(url_for('product_order'))
    else:
        request_product_id = request.args.get('product_id')
        if request_product_id:
            product = Product.query.filter_by(product_id=request_product_id).first()
            user = User.query.filter_by(email=product.seller_id).first()
            product.views += 1
            db.session.commit()
            bids = Bid.query.filter_by(product_id=request_product_id).all()
            no_of_offers = 0
            if bids:
                no_of_offers = len(bids)
            return render_template('product_detail.html',
                                   title='Product Detail | Bidding App',
                                   product=product,
                                   user=user,
                                   no_of_offers=no_of_offers)
        else:
            return redirect(url_for('home'))

@app.route('/product-registration-success')
def product_registration_success():
    product_id = session.get('product_id')
    product = Product.query.filter_by(product_id=product_id).first()
    return render_template("product_registration_success.html", product=product)

@app.route('/product-order', methods=['GET', 'POST'])
def product_order():
    order_form = OrderForm()
    if request.method == 'POST':
        user_id = session.get('username')
        product_id = session.get('product_id')
        bid_id = session.get('bid_id')
        address = convert_to_address_from(order_form, user_id)
        payment = convert_to_payment_from(order_form, user_id)
        db.session.add(address)
        db.session.add(payment)
        db.session.flush()
        db.session.commit()
        order = convert_to_order_from(product_id, payment.payment_id, address.address_id, bid_id)
        db.session.add(order)
        db.session.flush()
        db.session.commit()
        session['order_id'] = order.order_id
        return redirect(url_for('order_confirmation'))
    else:
        product_id = session.get('product_id')
        bid_id = session.get('bid_id')
        product = Product.query.filter_by(product_id=product_id).first()
        bid = Bid.query.filter_by(bid_id=bid_id).first()
        return render_template("product_order.html", product=product, bid= bid, order_form=order_form)


@app.route('/order-confirmation')
def order_confirmation():
    return render_template('order_confirmation.html', order_id=session.get('order_id'))

@app.route('/search', methods=['POST'])
def search():
    search_form = SearchForm()
    product_name = search_form.product_name.data
    product_category = search_form.category.data
    if (product_name and product_category):
        products = Product.query.filter_by(name=product_name).limit(5).all()
        return render_template('search.html', title='Search | Bidding App', session=session.get('username'),
                               products=products, search_form=search_form)
    elif (product_name and not product_category):
        products = Product.query.filter_by(product_name=product_name).limit(5).all()
        return render_template('search.html', title='Search | Bidding App', session=session.get('username'),
                               products=products, search_form=search_form)
    elif (not product_name and product_category):
        products = Product.query.filter_by(product_name=product_name).limit(5).all()
        return render_template('search.html', title='Search | Bidding App', session=session.get('username'),
                               products=products, search_form=search_form)
    else:
        return redirect(url_for('home'))
    # return 'On search page!' + search_form.category.data + search_form.product_name.data

# @app.route('/search')
# def product(resp):
#     _article = Article.query.filter_by(id=resp['articleId']).first()
#     offers = Offer.query.filter_by(article_id=_article.id).order_by(Offer.price.desc()).limit(3).all()
#     max_offer = []
#     for offer in offers:
#         user = User.query.filter_by(id=offer.user_id).first()
#         _offer = {'username': user.username, 'price': offer.price}
#         max_offer.append(_offer)
#
#     article_resp = {'id': _article.id, 'views': _article.views,
#                     'offers': max_offer}
#     emit('articleResponse' + str(article_resp['id']), article_resp, broadcast=True)


# @app.errorhandler(500)
# def internal_server_error(e):
#     return render_template('page-500.html'), 500


# start the server with the 'run()' method
if __name__ == '__main__':
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(func=evaluate_bids, trigger="interval", seconds=5)
    # scheduler.start()

    # app.apscheduler.add_job(func=evaluate_bids, trigger='interval', seconds=5, id='1')

    # Shut down the scheduler when exiting the app
    # atexit.register(lambda: scheduler.shutdown())
    app.run(debug=True)
