# criar as rotas do nosso site (os links)
from flask import render_template, url_for, redirect, send_from_directory
from fakepinterest import app, database, bcrypt
from fakepinterest.models import Usuario, Foto
from flask_login import login_required, login_user, logout_user, current_user
from fakepinterest.forms import FormLogin, FormCriarConta, FormFoto
from werkzeug.utils import secure_filename
import os

@app.route("/", methods=["GET", "POST"])
def homepage():
    form_login = FormLogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario)
            return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("homepage.html", form=form_login)

@app.route("/criarconta", methods=["GET", "POST"])
def criar_conta():
    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit():
        senha = bcrypt.generate_password_hash(form_criarconta.senha.data).decode("utf-8")
        usuario = Usuario(username=form_criarconta.username.data,
                          senha=senha, email=form_criarconta.email.data)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("criarconta.html", form=form_criarconta)

@app.route(f'/uploads/<path:filename>')
def download_file(filename):
    print(filename)
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=True)


@app.route("/perfil/<id_usuario>", methods=["GET", "POST"])
@login_required
def perfil(id_usuario):
    if int(id_usuario) == int(current_user.id):
        # o usuário está acessando o próprio perfil
        form_foto = FormFoto()

        if form_foto.validate_on_submit():
            arquivo = form_foto.foto.data
            nome_seguro = secure_filename(arquivo.filename)

            # salvar o arquivo na pasta correta
            caminho = os.path.join(app.config["UPLOAD_FOLDER"], nome_seguro)
            arquivo.save(caminho)

            # criar a instância da Foto com data atual
            nova_foto = Foto(
                imagem=nome_seguro,
                id_usuario=current_user.id,
                # data_upload=datetime.utcnow()  # se ainda não for automático no modelo
            )

            database.session.add(nova_foto)
            database.session.commit()

            return redirect(url_for('perfil', id_usuario=current_user.id))  # evita repost do formulário

        # buscar fotos ordenadas por data (mais recentes primeiro)
        fotos = Foto.query.filter_by(id_usuario=current_user.id).order_by(Foto.data_criacao.desc()).all()

        return render_template("perfil.html", usuario=current_user, form=form_foto, fotos=fotos)

    else:
        # visualizando o perfil de outro usuário
        usuario = Usuario.query.get(int(id_usuario))
        fotos = Foto.query.filter_by(id_usuario=usuario.id).order_by(Foto.data_criacao.desc()).all()

        return render_template("perfil.html", usuario=usuario, form=None, fotos=fotos)



@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


@app.route("/feed")
@login_required
def feed():
    fotos = Foto.query.order_by(Foto.id.desc()).all()
    return render_template("feed.html", fotos=fotos)
