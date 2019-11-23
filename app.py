# import the Flask class from the flask module
from flask import Flask, render_template,request,redirect, url_for,session
from flaskext.mysql import MySQL
from forms.login_form import LoginForm

# create the application object
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'jaypatel'
app.config['MYSQL_DATABASE_DB'] = 'bidding-app'
mysql = MySQL(app)

def invalid_confirm_password(password, confirm_password):
    if not password or not confirm_password:
        return True
    elif confirm_password != password:
        return True
    else:
        return False


@app.route('/')
def home():
    return "Hello, World!"  # return a string

@app.route('/login', methods=['GET','POST'])
def login():
    if session.get('username'):
        return redirect(url_for('index'))
    login_form = LoginForm()
    error = None
    if request.method =='POST':
        if login_form.validate_on_submit():
            connection = mysql.connect()
            cur = connection.cursor()
            cur.execute("select * from users where email = %s and  password = %s", (login_form.username, login_form.password))
            user = cur.fetchone()
            if user is None:
                return redirect(url_for('login'))
            elif user.password == login_form.password:
                session['username'] = user.username
                return redirect(url_for('index'))
            else:
                return redirect(url_for('login'))

    render_template('login.html',
                    title='Login',
                    login_form=login_form,
                    session=session.get('username'))
    return render_template('login.html',error=error)

@app.route('/signup', methods=['GET','POST'])
def signup():
    error = None
    if request.method =='POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if first_name and last_name and email and password and confirm_password == password:
            connection = mysql.connect()
            cur = connection.cursor()
            rows = cur.execute("SELECT * FROM users WHERE email = %s", email)
            if rows:
                return render_template("signup.html", error= "Username is already taken")
            else:
                cur.execute("INSERT INTO users(first_name, last_name, email, password) VALUES (%s, %s, %s, %s)",
                            (first_name, last_name, email, password))
                connection.commit()
                cur.close()
            error = 'You have signed up successfully.'
        elif invalid_confirm_password(password, confirm_password):
            error = 'Enter correct password.'
        else:
            error = 'Inputs cannot be empty.'
    return render_template('signup.html', error=error)

@app.route('/product_registration', methods = ['GET','POST'])
def product_registration():
    error = None
    if request.method == 'POST':
        uploaded_files = request.files.getlist('files')
        Category = request.form['Category']
        Name = request.form['Name']
        Description = request.form['Description']
        Base_price = request.form['Base_price']
        Is_bidable = request.form['Is_bidable']
        connection = mysql.connect()
        cur = connection.cursor()
        cur.execute("INSERT INTO product(Category, Name, Description, Base_price, Is_bidable) VALUES (%s, %s, %s, %d, %d)",
                    (Category, Name, Description, Base_price, Is_bidable))
        connection.commit()
        cur.close()

    else:
        return render_template('product_registration.html')

@app.route('/product-description')
def product_description():
    connection=mysql.connect()
    cur = connection.cursor()
    cur.execute("select * from product ")
    cur.fetchone()
    return render_template("/product_description.html")



# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)