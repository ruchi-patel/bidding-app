import datetime

from sqlalchemy import and_
from flask import Flask, render_template, request, redirect, url_for, session
from flask_apscheduler import APScheduler

from forms.login_form import LoginForm
from forms.order_form import OrderForm
from forms.product_registration_form import ProductRegistrationForm
from forms.search_form import SearchForm
from forms.signup_form import SignupForm
from mapper import *
from models import db
from models.bid import Bid

# create the application object
app = Flask(__name__)
app.config['SECRET_KEY'] = 'very very secret'
# app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:jaypatel@localhost/bidding-app'
db.init_app(app)
db.app = app

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


def evaluate_bids():
    print("-----------------")
    products = Product.query.filter(and_(Product.is_biddable==True, Product.is_active == True)).all()
    for product in products:
        if(datetime.datetime.combine(product.end_day, product.end_time) < datetime.datetime.now()):
            bids = Bid.query.filter_by(product_id=product.product_id).all()
            if (len(bids) > 0):
                max_amount = 0
                max_bid = None
                for bid in bids:
                    if bid.bid_amount > max_amount:
                        max_bid = bid
                        max_amount = bid.bid_amount
                print('selected bid_id: ' + str(max_bid.bid_id) + ' with amount: ' + str(max_amount) + ' for product_id: ' + str(product.product_id))
                order = Order.query.filter_by(bid_id=max_bid.bid_id).first()
                if order is not None:

                    print('selected order_id: ' + str(order.order_id))

                order_confirmation = convert_to_order_confirmation_from(product.product_id,
                                                                        order.payment_id,
                                                                        order.address_id,
                                                                        max_bid.bidder_id,
                                                                        order.order_id,
                                                                        max_bid.bid_amount)
                product.is_active = False
                db.session.add(order_confirmation)
                db.session.flush()
                print('marking product with done for product_id: ' + str(product.product_id))
                db.session.commit()
            #     add same bid and product to final_confirmation and mark the product not active
            else:
                print('marking product for not bidding for product_id: ' + str(product.product_id))
                product.is_biddable = False
                db.session.commit()

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
    products = Product.query.filter_by(is_active=True).order_by(Product.product_id.desc()).all()
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
        return redirect(url_for('home'))
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
        if session.get('username') is None:
            return redirect(url_for('login'))
        else:
            return render_template('product_registration.html', product_registration_form=product_registration_form)


@app.route('/product-detail', methods = ['GET', 'POST'])
def product_details():
    if request.method == 'POST':
        bid_id = request.form.get('bid_id')
        if bid_id:
            bid = Bid.query.filter_by(bid_id=bid_id).first()
            bid.bid_amount=request.form['bid_amount']
            db.session.commit()
            product = Product.query.filter_by(product_id=request.form.get('product_id')).first()
            session['from_page'] = 'product_detail'
            session['product_id'] = product.product_id
            session['bid_id'] = bid_id
            return render_template('bid_update_confirmation.html')
        else:
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
            product = Product.query.filter(and_(Product.product_id==request_product_id, Product.is_active == True)).first()
            if product is None:
                return redirect(url_for('home'))
            user = User.query.filter_by(email=product.seller_id).first()
            product.views += 1
            db.session.commit()
            bids = Bid.query.filter_by(product_id=request_product_id).all()
            no_of_offers = 0
            bid_id = None
            bid_amount = None
            buyer_equals_seller = False
            if product.seller_id == session.get('username'):
                buyer_equals_seller = True
            if bids:
                no_of_offers = len(bids)
                if session.get('username'):
                    for bid in bids:
                        if session.get('username') == bid.bidder_id:
                            bid_id = bid.bid_id
                            bid_amount = bid.bid_amount
            return render_template('product_detail.html',
                                   title='Product Detail | Bidding App',
                                   product=product,
                                   user=user,
                                   no_of_offers=no_of_offers, session=session.get('username'),
                                   bid_id=bid_id, bid_amount=bid_amount,
                                   buyer_equals_seller=buyer_equals_seller)
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
        session['product_name'] = Product.query.filter_by(product_id=product_id).first().name
        return redirect(url_for('order_confirmation'))
    else:
        product_id = session.get('product_id')
        bid_id = session.get('bid_id')
        product = Product.query.filter_by(product_id=product_id).first()
        bid = Bid.query.filter_by(bid_id=bid_id).first()
        return render_template("product_order.html", product=product, bid= bid, order_form=order_form)


@app.route('/order-confirmation')
def order_confirmation():
    return render_template('order_confirmation.html', order_id=session.get('order_id'), product_name=session.get('product_name'))


@app.route('/search', methods=['POST'])
def search():
    search_form = SearchForm()
    product_name = search_form.product_name.data
    product_category = search_form.category.data
    like_string = "%{}%".format(product_name)
    if product_name and product_category:
        products = Product.query.filter(and_(Product.name.like(like_string), Product.category.like(product_category), Product.is_active == True)).all()
        return render_template('search.html', title='Search | Bidding App', session=session.get('username'),
                               products=products, search_form=search_form)
    elif product_name and not product_category:
        products = Product.query.filter(Product.name.like(like_string), Product.is_active == True).all()
        return render_template('search.html', title='Search | Bidding App', session=session.get('username'),
                               products=products, search_form=search_form)
    elif not product_name and product_category:
        products = Product.query.filter(Product.category.like(product_category), Product.is_active == True).all()
        return render_template('search.html', title='Search | Bidding App', session=session.get('username'),
                               products=products, search_form=search_form)
    else:
        return redirect(url_for('home'))


@app.route('/product-buy', methods=['GET', 'POST'])
def product_buy():
    order_form = OrderForm()
    if request.method == 'POST':
        user_id = session.get('username')
        product_id = request.args.get('product_id')
        address = convert_to_address_from(order_form, user_id)
        payment = convert_to_payment_from(order_form, user_id)
        db.session.add(address)
        db.session.add(payment)
        db.session.flush()
        db.session.commit()
        latest_order = OrderConfirmation.query.order_by(OrderConfirmation.order_id.desc()).first()
        product = Product.query.filter_by(product_id=product_id).first()
        order = convert_to_order_confirmation_from(product_id, payment.payment_id, address.address_id, user_id, latest_order.order_id+1, product.base_price)
        product.is_active = False
        db.session.add(order)
        db.session.flush()
        db.session.commit()
        session['order_id'] = order.order_id
        return redirect(url_for('order_confirmation'))
    else:
        product_id = request.args.get('product_id')
        product = Product.query.filter_by(product_id=product_id).first()
        return render_template("product_buy.html", product=product, order_form=order_form)


@app.route('/list-bids')
def list_bids():
    user_id = session.get('username')
    if user_id is not None:
        list_of_bids = Bid.query.filter_by(bidder_id=user_id)
        list = []
        for bid in list_of_bids:
            product = Product.query.filter_by(product_id=bid.product_id).first()
            list.append((product, bid))
        joined_results = db.session.query(Product).join(Bid).filter(Bid.bidder_id == user_id).all()
        print(len(joined_results))
        return render_template('list_bids.html', products=list)
    else:
        return redirect(url_for('login'))


@app.route('/list-products')
def list_products():
    user_id = session.get('username')
    if user_id is not None:
        products = Product.query.filter_by(seller_id=user_id).all()
        return render_template('list_products.html', products=products)
    else:
        return redirect(url_for('login'))


@app.route('/list-ordered-products')
def list_ordered_products():
    user_id = session.get('username')
    if user_id is not None:
        products = []
        orders = OrderConfirmation.query.filter_by(user_id=user_id)
        if orders:
            for order in orders:
                products.append(Product.query.filter_by(product_id=order.product_id).first())
        # products = Product.query.filter_by(seller_id=user_id).all()
        return render_template('list_ordered_products.html', products=products)
    else:
        return redirect(url_for('login'))


# @app.route('/profile')
# def profile():
#     user_id = session.get('username')
#     if user_id:
#         user = User.query.filter_by(email=user_id).first()
#         products_that_user_is_selling = Product.query.filter_by(seller_id=user_id).all()
#         joined_results = session.query(Product).join(Bid).filter(Bid.bidder_id == user_id)
#
#     else:
#         return redirect(url_for('login'))



@app.errorhandler(500)
def internal_server_error(e):
    return render_template('page-500.html'), 500


# start the server with the 'run()' method
if __name__ == '__main__':
    # scheduler = BackgroundScheduler()
    # scheduler.add_job(func=evaluate_bids, trigger="interval", seconds=5)
    # scheduler.start()

    app.apscheduler.add_job(func=evaluate_bids, trigger='interval', seconds=60, id='1')

    # Shut down the scheduler when exiting the app
    # atexit.register(lambda: scheduler.shutdown())
    app.run(debug=True)
