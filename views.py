import csv
from flask import render_template, request, redirect, session, flash, url_for, send_from_directory, send_file
from models import Cadastro, Usuario
from dao import GesterDao, UsuarioDao, RelatoriosDao
from gester import app
from config import db
from datetime import date, datetime
import bcrypt

cadastro_dao = GesterDao(db)
usuario_dao = UsuarioDao(db)
relatorios_dao = RelatoriosDao(db)

#Rotas de autenticação
@app.route('/')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)


@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Nenhum usuário logado!')
    return redirect(url_for('login'))


@app.route('/autenticar', methods=['POST', ])
def autenticar():
    usuario = usuario_dao.buscar_por_id(request.form['usuario'])
    if usuario:
        if bcrypt.hashpw(request.form['senha'].encode('utf8'), usuario.senha.encode('utf8')) == usuario.senha.encode('utf8'):
            #usuario.senha == cripSenha:
            session['usuario_logado'] = usuario.usuario
            flash(usuario.nome + ' logado com sucesso!')
            proxima_pagina = request.form['proxima']
            return redirect(proxima_pagina)
        else:
            flash('Senha Incorreta!')
            return redirect(url_for('login'))
    else:
        flash('Usuário ou senha incorretos!')
        return redirect(url_for('login'))



#Rotas de Cadastro de Terceiros

@app.route('/index')
def index():
    lista = cadastro_dao.listar()
    return render_template('lista.html', titulo='Gestão de Terceiros', cadastros=lista)

@app.route('/indexSearch', methods=['POST',])
def indexSearch():
    search = request.form['search'].upper()
    searchRadio = request.form['searchRadio'].upper()

    if search is None or search == '':
        return redirect(url_for('index'))
    elif searchRadio == 'TERCEIRO':
        lista = cadastro_dao.listarSearch(search)
        return render_template('lista.html', titulo='Gestão de Terceiros', cadastros=lista)
    else:
        lista = cadastro_dao.listarSearchResp(search)
        return render_template('lista.html', titulo='Gestão de Terceiros', cadastros=lista)


@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    return render_template('novo.html', titulo='Cadastro Terceiro')


@app.route('/criar', methods=['POST',])
def criar():
    chamado = request.form['chamado']
    nome = request.form['nome'].upper()
    cpf = request.form['cpf'].replace('-','').replace('.','')
    email = request.form['email'].upper()
    empresa = request.form['empresa'].upper()
    cnpj = request.form['cnpj'].replace('-','').replace('.','').replace('/','')
    responsavel = request.form['responsavel'].upper()
    cpf_responsavel = request.form['cpf_responsavel'].replace('-','').replace('.','')
    data_criacao = int(date.today().strftime('%Y%m%d'))
    data_fim_contrato = int(request.form['data_fim_contrato'].replace('-',''))
    status = 'ATIVO'

    cadastro = Cadastro(nome,cpf,email,empresa,cnpj,responsavel,cpf_responsavel,data_criacao,data_fim_contrato, chamado, status)
    cadastro = cadastro_dao.salvar(cadastro)
    return redirect(url_for('index'))


@app.route('/editar/<int:id>')
def editar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('editar')))
    cadastro = cadastro_dao.busca_por_id(id)
    return render_template('editar.html', titulo='Editar Terceiro', cadastro=cadastro, idcad=id)


@app.route('/atualizar', methods=['POST',])
def atualizar():
    chamado = request.form['chamado']
    nome = request.form['nome'].upper()
    cpf = request.form['cpf'].replace('-','').replace('.','')
    email = request.form['email'].upper()
    empresa = request.form['empresa'].upper()
    cnpj = request.form['cnpj'].replace('-','').replace('.','').replace('/','')
    responsavel = request.form['responsavel'].upper()
    cpf_responsavel = request.form['cpf_responsavel'].replace('-','').replace('.','')
    data_criacao = 0
    data_fim_contrato = int(request.form['data_fim_contrato'].replace('-',''))
    status = 'ATIVO'
    if int(request.form['data_fim_contrato'].replace('-','')) < int(date.today().strftime('%Y%m%d')):
        status = 'INATIVO'

    cadastro = Cadastro(nome,cpf,email,empresa,cnpj,responsavel,cpf_responsavel,data_criacao,data_fim_contrato, chamado, status, id=request.form['id'])
    cadastro_dao.salvar(cadastro)
    return redirect(url_for('index'))


@app.route('/deletar/<int:id>')
def deletar(id):
    cadastro_dao.deletar(id)
    flash('Terceiro removido com sucesso!')
    return redirect(url_for('index'))


#Rotas de Usuários

@app.route('/usuarios')
def usuarios():
    lista = usuario_dao.listarUsuarios()
    return render_template('listaUsuarios.html', titulo='Usuários', usuarios=lista)


@app.route('/novoUsuario')
def novoUsuario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novoUsuario')))
    return render_template('novoUsuario.html', titulo='Cadastro Usuário')


@app.route('/criarUsuario', methods=['POST',])
def criarUsuario():
    user = usuario_dao.buscar_por_id(request.form['usuario'].upper())
    if user is None:
        user = 'None'
    else:
        user = user.usuario

    if user != request.form['usuario'].upper():
        if request.form['senha'] == request.form['confirmaSenha']:
            usuario = request.form['usuario'].upper()
            nome = request.form['nome'].upper()
            email = request.form['email'].upper()
            cpf = request.form['cpf'].replace('-','').replace('.','')
            senha = request.form['senha']
            data_criacao = int(date.today().strftime('%Y%m%d'))
            data_revogacao = int(request.form['data_revogacao'].replace('-',''))
            status = 'ATIVO'

            usuario = Usuario(usuario, nome, email, cpf, senha, data_criacao, data_revogacao, status)
            usuario = usuario_dao.salvarUsuario(usuario)
            return redirect(url_for('usuarios'))
        else:
            flash('Senhas não conferem, efetue novamente o cadastro!')
            return render_template('novoUsuario.html', titulo='Cadastro Usuário')
    else:
        flash('Usuário já existe!')
        return render_template('novoUsuario.html', titulo='Cadastro Usuário')


@app.route('/editarUsuario/<int:id>')
def editarUsuario(id):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('editarUsuario')))
    usuario = usuario_dao.busca_por_id_usuario(id)
    return render_template('editarUsuario.html', titulo='Editar Usuário', usuario=usuario, idcad=id)


@app.route('/atualizarUsuario', methods=['POST',])
def atualizarUsuario():
    usuario = request.form['usuario'].upper()
    nome = request.form['nome'].upper()
    email = request.form['email'].upper()
    cpf = request.form['cpf'].replace('-','').replace('.','')
    senha = 0
    data_criacao = 0
    data_revogacao = int(request.form['data_revogacao'].replace('-',''))
    status = 'ATIVO'
    if int(request.form['data_revogacao'].replace('-', '')) < int(date.today().strftime('%Y%m%d')):
        status = 'INATIVO'

    usuario = Usuario(usuario, nome, email, cpf, senha, data_criacao, data_revogacao, status, id=request.form['id'])
    usuario_dao.salvarUsuario(usuario)
    return redirect(url_for('usuarios'))


@app.route('/deletarUsuario/<int:id>')
def deletarUsuario(id):
    usuario_dao.deletarUsuario(id)
    flash('Usuário removido com sucesso!')
    return redirect(url_for('usuarios'))


@app.route('/reset/<int:id>/<username>')
def reset(id,username):
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('usuarios')))
    return render_template('resetUsuario.html', titulo='Reset de Senha', idcad=id, username=username)


@app.route('/resetUpdate', methods=['POST',])
def resetUpdate():
    id = request.form['id']
    username = request.form['usuario']
    if request.form['senha'] == request.form['confirmaSenha']:
        senha = request.form['senha']
        usuario_dao.reset(id,senha)
        flash('Reset de senha efetuado com sucesso!')
        return redirect(url_for('usuarios'))
    else:
        flash('Senhas não conferem!')
        return render_template('resetUsuario.html', titulo='Reset de Senha', idcad=id, username=username)


#Relatorios
@app.route('/relatorios')
def relatorios():
    datetim = datetime.timestamp(datetime.now())
    return render_template('relatorios.html', titulo='Relatórios', conteudo=datetim)

@app.route('/impBlazonNew/<file>')
def impBlazonNew(file):
    impNew = relatorios_dao.importCadBlazon()

    with open('C:/Automations/GestaoTerceiros/reports/ImportarNovosCadastrosSGI.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(["displayName","firstName","email","personalEmail","state"])
        for impNewLines in impNew:
            writer.writerow([impNewLines[0], impNewLines[0].split()[0], impNewLines[2], impNewLines[2], 'ACTIVE'])

    return send_file('C:/Automations/GestaoTerceiros/reports/ImportarNovosCadastrosSGI.csv', as_attachment=True)


@app.route('/impBlazonRevoga/<file>')
def impBlazonRevoga(file):
    impNew = relatorios_dao.importCadBlazonRevoga()
    with open('C:/Automations/GestaoTerceiros/reports/ImportarRevogacaoCadastrosSGI.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(["identifier","username"])
        for impNewLines in impNew:
            writer.writerow([impNewLines[0], impNewLines[1]])

    return send_file('C:/Automations/GestaoTerceiros/reports/ImportarRevogacaoCadastrosSGI.csv', as_attachment=True)