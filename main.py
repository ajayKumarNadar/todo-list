from forms import RegisterForm, LoginForm, NewTodoList, AddTodo
from flask import Flask, render_template, url_for, redirect, flash
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todos.db"

Bootstrap(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# noinspection PyUnresolvedReferences
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    todo = relationship("Todo", back_populates="user")
    todo_list = relationship("TodoList", back_populates="parent_user")


# noinspection PyUnresolvedReferences
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="todo")
    active = db.Column(db.Boolean, default=False)
    title = db.Column(db.String(250), nullable=False)
    todo_list = relationship("TodoList", back_populates="parent_todo")


# noinspection PyUnresolvedReferences
class TodoList(db.Model):
    __tablename__ = 'todo_list'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    todo_id = db.Column(db.Integer, db.ForeignKey("todos.id"))
    parent_user = relationship("User", back_populates="todo_list")
    parent_todo = relationship("Todo", back_populates="todo_list")
    todo = db.Column(db.String(250), nullable=False)
    todo_type = db.Column(db.String(5), nullable=False)

db.create_all()

add__form = None
new__form = None
active_todo = None
all_todo = None


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    global add__form, active_todo, all_todo
    username = current_user.name.title()
    username_list = username.split(" ")
    if len(username_list) == 1:
        logo = username[0]
    elif len(username_list) >= 1:
        logo = username_list[0][0] + username_list[1][0]

    active_todo = Todo.query.filter_by(user_id=current_user.id, active=True).first()
    try:
        todo_list = TodoList.query.filter_by(user_id=current_user.id, todo_id=active_todo.id)
    except AttributeError:
        todo_list = None

    return render_template("index.html", logo=logo, add_form=add__form, new_form=new__form, todo=active_todo,
                           todo_list=todo_list, all_todo=all_todo)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(name=form.name.data, email=form.email.data, password=hash_and_salted_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))

    return render_template("register.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form)


@app.route("/add", methods=["POST", "GET"])
def add():
    global add__form, active_todo
    form = AddTodo()
    add__form = form
    if form.validate_on_submit():
        add__form = None
        new_todo_item = TodoList(user_id=current_user.id, todo_id=active_todo.id, todo_type="todo", todo=form.todo.data)
        db.session.add(new_todo_item)
        db.session.commit()
        return redirect(url_for('home'))

    return redirect(url_for('home'))


@app.route("/new", methods=["POST", "GET"])
def new():
    global new__form, active_todo
    form = NewTodoList()
    new__form = form
    if form.validate_on_submit():
        new__form = None
        try:
            prew_active_todo = Todo.query.filter_by(active=True).first()
            prew_active_todo.active = False
            db.session.commit()
        except AttributeError:
            pass
        todo = Todo(user_id=current_user.id, active=True, title=form.title.data)
        db.session.add(todo)
        db.session.commit()
        active_todo = Todo.query.filter_by(active=True).first()

        todo_1 = TodoList(user_id=current_user.id, todo_id=active_todo.id, todo=form.todo_1.data, todo_type="todo")
        db.session.add(todo_1)
        if form.todo_2.data != "":
            todo_2 = TodoList(user_id=current_user.id, todo_id=active_todo.id, todo=form.todo_2.data, todo_type="todo")
            db.session.add(todo_2)
        if form.todo_3.data != "":
            todo_3 = TodoList(user_id=current_user.id, todo_id=active_todo.id, todo=form.todo_3.data, todo_type="todo")
            db.session.add(todo_3)
        if form.todo_4.data != "":
            todo_4 = TodoList(user_id=current_user.id, todo_id=active_todo.id, todo=form.todo_4.data, todo_type="todo")
            db.session.add(todo_4)
        if form.todo_5.data != "":
            todo_5 = TodoList(user_id=current_user.id, todo_id=active_todo.id, todo=form.todo_5.data, todo_type="todo")
            db.session.add(todo_5)
        db.session.commit()
        return redirect(url_for('home'))

    return redirect(url_for('home'))


@app.route('/open/<todo_id>', methods=['GET', 'POST'])
def open_todo(todo_id):
    global all_todo, active_todo
    if todo_id != "0":
        Todo.query.filter_by(active=True, user_id=current_user.id).first().active = False
        db.session.commit()
        active_todo = Todo.query.get(todo_id)
        active_todo.active = True
        db.session.commit()
        all_todo = None
        return redirect(url_for('home'))
    else:
        all_todo = Todo.query.filter_by(user_id=current_user.id)
        return redirect(url_for('home'))


@app.route('/delete/<todo_id>')
def delete(todo_id):
    todo_id = int(todo_id)
    todo_to_delete = TodoList.query.get(todo_id)
    if todo_to_delete.user_id == current_user.id and todo_to_delete.todo_id == active_todo.id:
        db.session.delete(todo_to_delete)
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/doing/<todo_id>')
def doing(todo_id):
    todo_id = int(todo_id)
    todo_to_delete = TodoList.query.get(todo_id)
    if todo_to_delete.user_id == current_user.id and todo_to_delete.todo_id == active_todo.id:
        todo_to_delete.todo_type = "doing"
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/done/<todo_id>')
def done(todo_id):
    todo_id = int(todo_id)
    todo_to_delete = TodoList.query.get(todo_id)
    if todo_to_delete.user_id == current_user.id and todo_to_delete.todo_id == active_todo.id:
        todo_to_delete.todo_type = "done"
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
