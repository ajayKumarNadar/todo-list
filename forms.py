from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    
    
class AddTodo(FlaskForm):
    todo = StringField("Todo", validators=[DataRequired()])
    submit = SubmitField("Add")


class NewTodoList(FlaskForm):
    title = StringField("TITLE", validators=[DataRequired()])
    todo_1 = StringField("Todo", validators=[DataRequired()])
    todo_2 = StringField("Todo")
    todo_3 = StringField("Todo")
    todo_4 = StringField("Todo")
    todo_5 = StringField("Todo")
    submit = SubmitField("Create")
