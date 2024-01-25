import sqlite3
import os, math, time
from flask import Flask, render_template, abort, redirect, url_for, jsonify, json, request, flash , g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo

app = Flask(__name__)
app.config['SECRET_KEY'] = '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
app.config.update(dict(DATABASE=os.path.join(app.root_path,'autonsk.db')))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = get_db_connection()
    return g.link_db


dbase = None
@app.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()
    def addUser(self, name, email, hpsw, firm):
      try:
          self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
          res = self.__cur.fetchone()
          if res['count'] > 0:
              print("Пользователь с таким email уже существует")
              return False
          tm = math.floor(time.time())

          if firm:
            self.__cur.execute("INSERT INTO suppliers VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?)", (firm['companyName'],
                                                                                              0,
                                                                                              firm['companyOpf'],
                                                                                              firm['companyAddress'],
                                                                                              firm['companyType'],
                                                                                              firm['companyInn'],
                                                                                              firm['companyKpp'],
                                                                                              firm['companyPhone'],))
            self.__db.commit()
            
            self.__cur.execute("SELECT id FROM suppliers WHERE title=?", (firm['companyName'],))
            res = self.__cur.fetchone()
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, ?, ?)", (name, hpsw, email, tm, res[0]))
            self.__db.commit()
          else:
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, ?, 0)", (name, hpsw, email, tm))
            self.__db.commit()
      except sqlite3.Error as e:
          print("Ошибка добавления пользователя в БД "+str(e))
          return False

      return True
    
    def getUserByEmail(self, email):
      try:
        self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
        res = self.__cur.fetchone()
        if not res:
          print("Пользователь не найден")
          return False
        return res
      except sqlite3.Error as e:
        print("Ошибка получения данных из БД "+str(e))

      return False
    
    def get_goods(self):
      self.__cur.execute(
      '''
      SELECT goods.id AS id, goods.title AS title, MIN(ga.price) AS price, image.path AS img_path
      FROM goods
      JOIN goods_availability AS ga ON goods.id = ga.good_id
      JOIN image ON goods.img_id = image.id
      GROUP BY goods.id
      ORDER BY random()
      LIMIT 4        
      ''')
      res = self.__cur.fetchall()

      return res
    def show_goods(self, id):
      self.__cur.execute(
         '''
          SELECT goods.id AS article, goods.title AS title,
            image.path AS img_path, manufacturer.title AS manufacturer_title,
            MAX(ga.price) AS max_price
          FROM goods
          JOIN image ON goods.img_id = image.id
          JOIN manufacturer ON goods.manufacturer_id = manufacturer.id
          JOIN goods_availability AS ga ON goods.id = ga.good_id
          WHERE goods.id = ?  
          GROUP BY goods.id    
          ''', (id,)
      )
      good = self.__cur.fetchone()
      self.__cur.execute(
        '''
        SELECT good_attribute.name AS name, good_attribute.value AS value
        From good_attribute
        Where good_attribute.good_id = ?
        ''', (id,)
      )
      attributes = self.__cur.fetchall()
      self.__cur.execute(
        '''
          SELECT min_price.price AS min_price, min_price.period AS min_price_period,
            min_period.price AS min_period_price, min_period.period AS min_period   
          FROM (
            SELECT ga.good_id, ga.price, ga.period
            FROM goods_availability  AS ga
            WHERE ga.price = 
              (
                SELECT MIN(ga2.price)
                FROM goods_availability AS ga2
                WHERE ga2.good_id = ? 
                GROUP BY ga2.good_id
              )
            ) AS min_price,
              (
            SELECT ga.good_id, ga.price, ga.period
            FROM goods_availability  AS ga
            WHERE ga.period = 
              (
                SELECT MIN(ga2.period)
                FROM goods_availability AS ga2
                WHERE ga2.good_id = ? 
                GROUP BY ga2.good_id
              ) 
            ) AS min_period ON min_period.good_id = min_price.good_id 
          GROUP BY min_price.good_id
        ''', (id,id))
      offers = self.__cur.fetchone()
      self.__cur.execute(
            '''
            SELECT s.is_atachment as atach, ga.price, ga.amount, ga.period, img.path
            FROM goods_availability AS ga
            JOIN suppliers AS s ON ga.supplier_id = s.id
            JOIN supplier_attachments AS sa ON s.is_atachment = sa.id
            LEFT JOIN image AS img ON sa.img_id = img.id
            WHERE ga.good_id = ?
            ''', (id,))
      table_products = self.__cur.fetchall()

      return good, attributes, offers, table_products
    def getUser(self, user_id):
      try:
          self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
          res = self.__cur.fetchone()
          if not res:
              print("Пользователь не найден")
              return False

          return res
      except sqlite3.Error as e:
          print("Ошибка получения данных из БД "+str(e))

      return False
    def get_goods_option(self):
      goods = self.__cur.execute(
      '''
      SELECT goods.id AS id, goods.title AS title
      FROM goods
      ''')
      res = goods.fetchall()
      return res
       
    
class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def getName(self):
        return self.__user['name'] if self.__user else "Без имени"

    def getEmail(self):
        return self.__user['email'] if self.__user else "Без email"

class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(),
                                                Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])
    remember = BooleanField("Запомнить", default = False)
    submit = SubmitField("Войти")

@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

@app.route('/')
def main():
  goods = dbase.get_goods()
  return render_template('index.html', goods = goods)

@app.route('/goods/<int:id>')
def show_good(id):
  good_dict = {}

  good, attributes, offers, table_products = dbase.show_goods(id)
  good_dict['good'] = good
  good_dict['good_attrs'] = attributes
  good_dict['good_offers'] = offers
  good_dict['table_products'] = table_products

  res = [tuple(table_products[row]) for row in range(len(table_products))]
  json_string = json.dumps(res)

  return render_template('good.html', context=[good_dict, json_string])

@app.route('/register', methods = ['POST', 'GET'])
def register():
  if request.method == 'POST':
    hash = generate_password_hash(request.form['psw'])
    if request.form.get('companyOpf'):
      company_data = {'companyOpf': request.form['companyOpf'],
                      'companyName': request.form['companyName'],
                      'companyInn': request.form['companyInn'],
                      'companyKpp': request.form['companyKpp'],
                      'companyPhone': request.form['companyPhone'],
                      'companyAddress': request.form['companyAddress'],
                      'companyType': request.form['companyType']
                      }
      res = dbase.addUser(request.form['name'], request.form['email'], hash, company_data)
    else:
      res = dbase.addUser(request.form['name'], request.form['email'], hash, False)
    if res:
        return redirect(url_for('login'))
    else:
        flash("Ошибка при добавлении в БД", "error")
  return render_template('register.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main'))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw_hash'], form.psw.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(url_for("main"))

    return render_template("login.html", form=form)

@app.route('/add/good', methods = ['POST', 'GET'])
def add_good():
   goods = dbase.get_goods_option()
   return render_template("addGood.html", goods = goods)
if __name__ == '__main__':
  app.run(host='localhost', port=8000)