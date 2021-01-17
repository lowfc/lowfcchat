from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)  # приложение flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'  # задаем параметры бд для приложения
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)  # объявляем объект для работы с бд, передаем ему приложение


class User(db.Model):  # класс объявляет таблицу в бд
    id = db.Column(db.Integer, primary_key=True)  # поля таблицы
    login = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    firstname = db.Column(db.String(40), nullable=False)
    lastname = db.Column(db.String(40), nullable=False)
    regDate = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):  # при получении объекта класса автоматически возвращается его id
        return '<User %r>' % self.id


class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # поля таблицы
    chatid = db.Column(db.Integer, nullable=False)
    sendby = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(200), nullable=False)
    dateofsend = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):  # при получении объекта класса автоматически возвращается его id
        return '<Message %r>' % self.id


class Chats(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # поля таблицы
    chatname = db.Column(db.String(50), nullable=False)
    dateofcreation = db.Column(db.DateTime, default=datetime.utcnow)
    fuserid = db.Column(db.Integer, nullable=False)
    suserid = db.Column(db.Integer, nullable=False)

    def __repr__(self):  # при получении объекта класса автоматически возвращается его id
        return '<Chat %r>' % self.id


class UserChats(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # поля таблицы
    userid = db.Column(db.Integer, nullable=False)
    chatid = db.Column(db.Integer, nullable=False)

    def __repr__(self):  # при получении объекта класса автоматически возвращается его id
        return '<UserChat %r>' % self.id


@app.route('/')
def index():  # вызывается при переходе на ссыль
    if 'logged_user_id' in session:
        return render_template('index.html')
    else:
        return redirect('/login')


@app.route('/chat')
def chat():
    if 'logged_user_id' in session:
        userchats = UserChats.query.filter(UserChats.userid == session['logged_user_id']).all()
        chats = []
        for i in userchats:
            chats.append(Chats.query.filter(Chats.id == i.chatid).first())
        return render_template('chat.html', userchats=chats)
    else:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    errors = []
    if request.method == 'POST':
        login = request.form['login']  # получаем в переменные значения полей из формы
        password = request.form['password']
        users = User.query.order_by(User.id).all()
        for i in users:
            if i.login == login:
                if check_password_hash(i.password, password):
                    session['logged_user_id'] = i.id
                    return redirect('/')
                else:
                    errors.append("Пароль введен неверно")
                    return render_template('login.html', errors=errors)
        errors.append("Учетная запись с таким логином не найдена")
        return render_template('login.html', errors=errors)
    else:
        session.pop('logged_user_id', None)
        return render_template('login.html')


@app.route('/admin-chat-users')
def adminchatusers():
    if 'logged_user_id' in session and session['logged_user_id'] == 0:
        userchats = UserChats.query.order_by(UserChats.id).all()
        return render_template('adminchatusers.html', userchats=userchats)
    else:
        return redirect('/login')


@app.route('/register', methods=['POST', 'GET'])
def register():
    errors = []
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        repassword = request.form['repassword']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        if User.query.filter(User.login == login).first() is not None:
            errors.append('Такой логин уже существует')
        if password != repassword:
            errors.append('Пароли не совпадают')
        if len(password) < 8:
            errors.append('Пароль должен содержать от 8 символов')
        if len(errors) == 0:
            user = User(login=login, password=generate_password_hash(password),
                        firstname=firstname, lastname=lastname)  # создаем экземпляр класса
            try:  # Пробуем добавить запись в таблицу
                db.session.add(user)
                db.session.commit()  # Применяем изменения в бд
                session['logged_user_id'] = user.id
                return redirect('/')  # Редиректим на главную
            except:
                return 'Обнаружены ошибки бэкэнда'
        return render_template('register.html', errors=errors)
    else:
        return render_template('register.html')


@app.route('/findpeople', methods=['GET', 'POST'])
def fp():
    if 'logged_user_id' in session:
        if request.method == 'GET':
            return render_template('findPeople.html')
        else:
            if len(request.form['search'].split()) == 2:
                name = request.form['search'].split()
                logins = User.query.filter((((User.firstname == name[0]) & (User.lastname == name[1])) | (
                            (User.firstname == name[1]) & (User.lastname == name[0]))) & (
                                                       User.id != session['logged_user_id'])).all()
            else:
                logins = User.query.filter(((User.firstname == request.form['search']) | (
                            User.lastname == request.form['search']) | (User.login == request.form['search'])) & (
                                                       User.id != session['logged_user_id'])).all()
            return render_template('findPeople.html', logins=logins)
    else:
        return redirect('/login')


@app.route('/admin-add-chat')
def adminaddchat():
    if 'logged_user_id' in session and session['logged_user_id'] == 0:
        chats = Chats.query.order_by(Chats.id).all()
        return render_template('adminaddchat.html', chats=chats)
    else:
        return redirect('/login')


@app.route('/admin-add-chat/delete/<int:chatid>')
def admindeletechat(chatid):
    if 'logged_user_id' in session and session['logged_user_id'] == 0:
        chat = Chats.query.get_or_404(chatid)
        try:
            db.session.delete(chat)
            db.session.commit()
            return redirect('/admin-add-chat')
        except:
            return 'Обнаружены ошибки бэкэнда.'
    else:
        return redirect('/login')


@app.route('/admin-add-user/delete/<int:id>')
def adminremovetheuser(id):
    if 'logged_user_id' in session and session['logged_user_id'] == 0:
        user = User.query.get_or_404(id)
        try:
            db.session.delete(user)
            db.session.commit()
            return redirect('/admin-add-user')
        except:
            return 'Обнаружены ошибки бэкэнда.'
    else:
        return redirect('/login')


@app.route('/admin-add-user', methods=['POST', 'GET'])  # Дополнительно указываем методы для работы со страницей
def adminadduser():
    if 'logged_user_id' in session and session[
        'logged_user_id'] == 0:  # 'logged_user_id' in session and session['logged_user_id'] == 1:
        if request.method == 'POST':  # если на страницу перешли с методом POST
            if 'isEdit' not in request.form:
                login = request.form['login']  # получаем в переменные значения полей из формы
                password = request.form['password']
                firstname = request.form['firstname']
                lastname = request.form['lastname']

                user = User(login=login, password=generate_password_hash(password),
                            firstname=firstname, lastname=lastname)  # создаем экземпляр класса
                # User, передавая ему заполненные ранее переменные в качестве полей для записи в БД

                try:  # Пробуем добавить запись в таблицу
                    db.session.add(user)  # через db.session.add добавляем экземпляр класса User с заполненными полями
                    db.session.commit()  # Применяем изменения в бд
                    return redirect('/admin-add-user')  # Редиректим на главную
                except:
                    return 'Error'
            else:
                user = User.query.get_or_404(request.form['currentId'])
                try:
                    user.id = request.form['id']
                    user.login = request.form['login']
                    if request.form.get('passRec') is not None:
                        user.password = generate_password_hash(request.form['password'])
                    user.firstname = request.form['firstname']
                    user.lastname = request.form['lastname']
                    db.session.commit()
                    return redirect('/admin-add-user')
                except:
                    return 'Обнаружены ошибки бэкэнда.'
        else:

            """
                query - запрос данных из бд, обращаться нужно к классу, отвечающему за таблицу
                order_by(<Класс> . <имя поля>) - сортировка по выбранному полю
                all / first / last - получить все / первое / последнее значение из таблицы
            """

            users = User.query.order_by(User.id).all()  # Получение записей из бд
            return render_template('adminadduser.html', users=users)  # Если обратились с методом GET, то просто
            # отображаем страницу
    else:
        return redirect('/login')


@app.route('/createchatwith', methods=['POST'])
def createchatwith():
    if 'logged_user_id' in session:
        chatname = request.form['chatname']
        suserid = request.form['userid']
        chat = Chats(chatname=chatname, fuserid=session['logged_user_id'], suserid=suserid)
        try:
            db.session.add(chat)
            db.session.commit()
        except:
            return 'Обнаружены ошибки бэкэнда'
        try:
            userchats = UserChats(userid=session['logged_user_id'], chatid=chat.id)
            userchats2 = UserChats(userid=suserid, chatid=chat.id)
            db.session.add(userchats)
            db.session.add(userchats2)
            db.session.commit()
        except:
            return 'Обнаружены ошибки бэкэнда'
        return redirect('/')
    else:
        return redirect('/login')


@app.route('/chatroom/<int:chatid>', methods=['POST', 'GET'])
def chatroom(chatid):
    if 'logged_user_id' in session:
        uchats = UserChats.query.filter(UserChats.userid == session['logged_user_id']).all()
        access = False
        for i in uchats:
            if i.chatid == chatid:
                access = True
        if access:
            if request.method == 'POST':
                try:
                    newmessage = Messages(chatid=request.form['chatid'], sendby=session['logged_user_id'],
                                          content=request.form['message'])
                    db.session.add(newmessage)
                    db.session.commit()
                except:
                    return 'ошибки бэкэнда'
                return 'lololo'
            else:
                return render_template('messenger.html', chatid=chatid)
        else:
            return redirect('/chat')
    else:
        return redirect('/login')


@app.route('/getallmessages', methods=['POST'])
def getallmessage():
    if 'logged_user_id' in session:
        messages = Messages.query.filter(Messages.chatid == request.form['chatid']).all()
        if len(messages) > 0:
            return render_template('messages.html', messages=messages)
        else:
            first = Messages(sendby=0, content='Напишите что нибудь!', chatid=request.form['chatid'])
            return render_template('messages.html', messages=[first])
    else:
        return redirect('/login')


@app.route('/addmessage', methods=['POST'])
def addmessage():
    if 'logged_user_id' in session:
        if request.method == 'POST':
            try:
                newmessage = Messages(chatid=request.form['chatid'], sendby=session['logged_user_id'],
                                      content=request.form['message'])
                db.session.add(newmessage)
                db.session.commit()
            except:
                return 'ошибки бэкэнда'
            return '''<div class="list-group" id={}> <p class="list-group-item list-group-item-action 
            list-group-item-secondary">[{}] {} (<a onclick="deleteMessage({})">Удалить</a>)</p> </div> 
            '''.format(newmessage.id, session['logged_user_id'], request.form['message'], newmessage.id)
    else:
        return redirect('/login')


@app.route('/deletemessage', methods=['POST'])
def deletemessage():
    if 'logged_user_id' in session:
        message = Messages.query.get_or_404(request.form['messageid'])
        try:
            if message.sendby == session['logged_user_id']:
                db.session.delete(message)
                db.session.commit()
                return '''
                <p class="list-group-item list-group-item-action list-group-item-warning">Сообщение удалено</p>
                '''
            else:
                return '''
                <p class="list-group-item list-group-item-action list-group-item-danger">Это сообщение нельзя удалить</p>
                '''
        except:
            return 'Сообщение уже удалено.'
    else:
        return redirect('/login')


@app.route('/returnlastid', methods=['POST'])
def return_last_id():
    if 'logged_user_id' in session:
        message = Messages.query.order_by(Messages.id).filter(Messages.chatid == request.form['chatid']).all()[::-1]
        return str(message[0].id)
    else:
        return redirect('/login')


@app.route('/returnafterupdate', methods=['POST'])
def return_after_update():
    if 'logged_user_id' in session:
        lastmessage = Messages.query.filter(Messages.id == request.form['lastmessageid']).first()
        messages = []
        if lastmessage is not None:
            messages = Messages.query.filter(Messages.dateofsend > lastmessage.dateofsend,
                                             Messages.sendby != session['logged_user_id']).all()
        return render_template('messages.html', messages=messages)
    else:
        return redirect('/login')


if __name__ == '__main__':
    app.secret_key = 'abcd1234'
    app.permanent_session_lifetime = timedelta(hours=1)
    app.run(debug=True)
