# criar os formularios do nosso site
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from fakepinterest.models import Usuario
from fakepinterest import bcrypt


class FormLogin(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(message='email@servidor.com'), Email(message='E-mail inválido.')])
    senha = PasswordField("Senha", validators=[DataRequired()] )
    botao_confirmacao = SubmitField("Fazer Login")

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if not usuario:
            raise ValidationError("Usuário inexistente, crie uma conta")

    def validate_senha(self, senha):
        usuario = Usuario.query.filter_by(email=self.email.data).first()
        if usuario and not bcrypt.check_password_hash(usuario.senha, senha.data):
            raise ValidationError("Senha incorreta. Tente novamente.")

class FormCriarConta(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email(message='E-mail inválido.')])
    username = StringField("Nome de usuário", validators=[DataRequired()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField("Confirmação de Senha", validators=[DataRequired(), EqualTo("senha", message='Confirmação de Senha precisa ser igual a Senha')])
    botao_confirmacao = SubmitField("Criar Conta")

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError("E-mail já cadastrado, faça login para continuar")


class FormFoto(FlaskForm):
    foto = FileField("Foto", validators=[DataRequired()])
    botao_confirmacao = SubmitField("Enviar")