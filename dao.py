from models import Cadastro, Usuario
import bcrypt
import mysql.connector

SQL_DELETA_CAD = 'delete from cadastro where id = %s'
SQL_CAD_POR_ID = 'SELECT  nome, LPAD(cpf,11,0), email, empresa, LPAD(cnpj,14,0), responsavel, LPAD(cpf_responsavel,11,0), data_criacao, convert(data_fim_contrato, DATE) , chamado, status, id from cadastro where id = %s'
SQL_ATUALIZA_CADASTRO = 'UPDATE cadastro SET nome=%s,cpf=%s,email=%s,empresa=%s,cnpj=%s,responsavel=%s,cpf_responsavel=%s,data_fim_contrato=%s, chamado=%s, status=%s where id = %s'
SQL_BUSCA_CADASTROS = 'SELECT  nome, LPAD(cpf,11,0), email, empresa, LPAD(cnpj,14,0), responsavel, LPAD(cpf_responsavel,11,0), data_criacao, DATE_FORMAT(convert(data_fim_contrato,DATE),"%d/%m/%Y"), chamado, status, id from cadastro order by nome'
SQL_BUSCA_CAD_SEARCH = 'SELECT  nome, LPAD(cpf,11,0), email, empresa, LPAD(cnpj,14,0), responsavel, LPAD(cpf_responsavel,11,0), data_criacao, DATE_FORMAT(convert(data_fim_contrato,DATE),"%d/%m/%Y"), chamado, status, id from cadastro where nome like %s order by nome'
SQL_BUSCA_CAD_SEARCH_RESP = 'SELECT  nome, LPAD(cpf,11,0), email, empresa, LPAD(cnpj,14,0), responsavel, LPAD(cpf_responsavel,11,0), data_criacao, DATE_FORMAT(convert(data_fim_contrato,DATE),"%d/%m/%Y"), chamado, status, id from cadastro where responsavel like %s order by nome'
SQL_CRIA_CADASTRO = 'INSERT into cadastro (nome,cpf,email,empresa,cnpj,responsavel,cpf_responsavel,data_criacao,data_fim_contrato, chamado, status) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
SQL_BUSCA_CAD_IMPORT = 'SELECT  nome, LPAD(cpf,11,0) cpf, email, empresa, LPAD(cnpj,14,0) cnpj, responsavel, LPAD(cpf_responsavel,11,0) cpf_responsavel, data_criacao from gesterdb.cadastro WHERE data_criacao >= DATE_FORMAT(convert(DATE_SUB(CURDATE(), INTERVAL 7 DAY),DATE),"%Y%m%d") order by nome'
SQL_BUSCA_CAD_IMPORT_REV = 'SELECT  nome, LPAD(cpf,11,0) cpf, email, empresa, LPAD(cnpj,14,0) cnpj, responsavel, LPAD(cpf_responsavel,11,0) cpf_responsavel, data_criacao from gesterdb.cadastro WHERE data_fim_contrato between DATE_FORMAT(convert(DATE_SUB(CURDATE(), INTERVAL 7 DAY),DATE),"%Y%m%d") and DATE_FORMAT(convert(CURDATE(),DATE),"%Y%m%d") order by nome'


SQL_USUARIO_POR_USUARIO = 'SELECT usuario, nome, email, LPAD(cpf,11,0), senha, data_criacao, data_revogacao, status, id from usuarios where usuario = %s'
SQL_USUARIO_POR_ID = 'SELECT usuario, nome, email, LPAD(cpf,11,0), senha, data_criacao, convert(data_revogacao, DATE), status, id from usuarios where id = %s'
SQL_BUSCA_USUARIOS = 'SELECT usuario, nome, email, LPAD(cpf,11,0), senha, data_criacao, data_revogacao, status, id from usuarios where usuario <> "admin"'
SQL_ATUALIZA_USUARIO = 'UPDATE usuarios SET usuario=%s, nome=%s, email=%s, cpf=%s, data_revogacao=%s, status=%s where id = %s'
SQL_CRIA_USUARIO = 'INSERT into usuarios (usuario, nome, email, cpf, senha, data_criacao, data_revogacao, status) values (%s, %s, %s, %s, %s, %s, %s, %s)'
SQL_DELETA_USUARIO = 'delete from usuarios where id = %s'
SQL_UPDATE_SENHA = 'UPDATE usuarios SET senha=%s where id = %s'

class GesterDao:
    def __init__(self, db):
        self.__db = db

    def salvar(self, gesterCadastro):
        cursor = self.__db.cursor()

        if (gesterCadastro.id):
            cursor.execute(SQL_ATUALIZA_CADASTRO, (gesterCadastro.nome,gesterCadastro.cpf,gesterCadastro.email,gesterCadastro.empresa,gesterCadastro.cnpj, gesterCadastro.responsavel,
                                                   gesterCadastro.cpf_responsavel,gesterCadastro.data_fim_contrato, gesterCadastro.chamado, gesterCadastro.status, gesterCadastro.id))
        else:
            cursor.execute(SQL_CRIA_CADASTRO, (gesterCadastro.nome,gesterCadastro.cpf,gesterCadastro.email,gesterCadastro.empresa,gesterCadastro.cnpj, gesterCadastro.responsavel,
                                               gesterCadastro.cpf_responsavel,gesterCadastro.data_criacao,gesterCadastro.data_fim_contrato, gesterCadastro.chamado, gesterCadastro.status))
            gesterCadastro.id = cursor.lastrowid
        self.__db.commit()
        return gesterCadastro

    def listar(self):
        cursor = self.__db.cursor()
        cursor.execute(SQL_BUSCA_CADASTROS)
        cadastros = traduz_cad(cursor.fetchall())
        self.__db.commit()
        return cadastros

    def listarSearch(self,search):
        cursor = self.__db.cursor()
        cursor.execute(SQL_BUSCA_CAD_SEARCH, ("%" + search + "%",))
        cadastros = traduz_cad(cursor.fetchall())
        self.__db.commit()
        return cadastros

    def listarSearchResp(self,search):
        cursor = self.__db.cursor()
        cursor.execute(SQL_BUSCA_CAD_SEARCH_RESP, ("%" + search + "%",))
        cadastros = traduz_cad(cursor.fetchall())
        self.__db.commit()
        return cadastros

    def busca_por_id(self, id):
        cursor = self.__db.cursor()
        cursor.execute(SQL_CAD_POR_ID, (id,))
        tupla = cursor.fetchone()
        self.__db.commit()
        return Cadastro(tupla[0], tupla[1], tupla[2], tupla[3], tupla[4], tupla[5], tupla[6], tupla[7], tupla[8], tupla[9], tupla[10])

    def deletar(self, id):
        self.__db.cursor().execute(SQL_DELETA_CAD, (id,))
        self.__db.commit()

class UsuarioDao:
    def __init__(self, db):
        self.__db = db

    def listarUsuarios(self):
        cursor = self.__db.cursor()
        cursor.execute(SQL_BUSCA_USUARIOS)
        usuariosList = traduz_usuario_cad(cursor.fetchall())
        self.__db.commit()
        return usuariosList

    def buscar_por_id(self, usuario):
        cursor = self.__db.cursor()
        cursor.execute(SQL_USUARIO_POR_USUARIO, (usuario,))
        dados = cursor.fetchone()
        usuario = traduz_usuario(dados) if dados else None
        self.__db.commit()
        return usuario

    def busca_por_id_usuario(self, id):
        cursor = self.__db.cursor()
        cursor.execute(SQL_USUARIO_POR_ID, (id,))
        tupla = cursor.fetchone()
        self.__db.commit()
        return Usuario(tupla[0], tupla[1], tupla[2], tupla[3], tupla[4], tupla[5], tupla[6], tupla[7], tupla[8])

    def salvarUsuario(self, gesterUsuario):
        cursor = self.__db.cursor()

        if (gesterUsuario.id):
            cursor.execute(SQL_ATUALIZA_USUARIO, (gesterUsuario.usuario, gesterUsuario.nome, gesterUsuario.email, gesterUsuario.cpf,
                                                  gesterUsuario.data_revogacao, gesterUsuario.status, gesterUsuario.id))
        else:
            cursor.execute(SQL_CRIA_USUARIO, (gesterUsuario.usuario, gesterUsuario.nome, gesterUsuario.email, gesterUsuario.cpf,
                                              bcrypt.hashpw(gesterUsuario.senha.encode('utf8'), bcrypt.gensalt()), gesterUsuario.data_criacao,
                                              gesterUsuario.data_revogacao, gesterUsuario.status))
            gesterUsuario.id = cursor.lastrowid
        self.__db.commit()
        return gesterUsuario

    def deletarUsuario(self, id):
        self.__db.cursor().execute(SQL_DELETA_USUARIO, (id,))
        self.__db.commit()

    def reset(self, id,senha):
        senha = senha
        senha = bcrypt.hashpw(senha.encode('utf8'), bcrypt.gensalt())
        self.__db.cursor().execute(SQL_UPDATE_SENHA, (senha, id))
        self.__db.commit()


def traduz_cad(cad):
    def cria_cad_com_tupla(tupla):
       return Cadastro(tupla[0], tupla[1], tupla[2], tupla[3], tupla[4], tupla[5], tupla[6], tupla[7], tupla[8], tupla[9], tupla[10], tupla[11])
    return list(map(cria_cad_com_tupla, cad))

def traduz_usuario(tupla):
    return Usuario(tupla[0], tupla[1], tupla[2], tupla[3], tupla[4], tupla[5], tupla[6], tupla[7], tupla[8])

def traduz_usuario_cad(usuarios):
    def cria_usuarios_com_tupla(tupla):
        return Usuario(tupla[0], tupla[1], tupla[2], tupla[3], tupla[4], tupla[5], tupla[6], tupla[7], tupla[8])
    return list(map(cria_usuarios_com_tupla,usuarios))


class RelatoriosDao:
    def __init__(self, db):
        self.__db = db

    def importCadBlazon(self):
        cursor = self.__db.cursor()
        cursor.execute(SQL_BUSCA_CAD_IMPORT)
        importBlazon = cursor.fetchall()

        list_import = []

        config = open('C:\Automations\generalSettings\credentials.txt', 'r').readlines()
        list_config = []

        for n in config:
            list_config.append(n.rstrip())

        dblazon = mysql.connector.connect(user='' + (list_config[2][list_config[2].find('=') + 1:]).strip() + '', passwd='' + (list_config[3][list_config[3].find('=') + 1:]).strip() + '', host="172.33.6.66", db="iamblazon")
        cursor_blazon = dblazon.cursor()

        for impBlazon in importBlazon:
            cursor_blazon.execute("select blazon.Nome, blazon.CPF, blazon.state from (select us.displayName AS Nome, (select TRIM(REPLACE(REPLACE(atr.value, '.', '' ), '-', '')) from EntryAttributeValue atr where atr.entry_id = us.id and atr.name = 'documentNumber') CPF, "
                                  "entry.state AS state from User us, Entry entry where entry.id = us.id) blazon where blazon.state = 'ACTIVE' and blazon.cpf = "+impBlazon[1])
            blazon = cursor_blazon.fetchall()

            if blazon is None or blazon == []:
                list_import.append((impBlazon[0], impBlazon[1], impBlazon[2], impBlazon[3], impBlazon[4], impBlazon[5], impBlazon[6], impBlazon[7]))

        return list_import


    def importCadBlazonRevoga(self):
        cursor = self.__db.cursor()
        cursor.execute(SQL_BUSCA_CAD_IMPORT_REV)
        importBlazon = cursor.fetchall()

        list_import = []

        config = open('C:\Automations\generalSettings\credentials.txt', 'r').readlines()
        list_config = []

        for n in config:
            list_config.append(n.rstrip())

        dblazon = mysql.connector.connect(user='' + (list_config[2][list_config[2].find('=') + 1:]).strip() + '', passwd='' + (list_config[3][list_config[3].find('=') + 1:]).strip() + '', host="172.33.6.66", db="iamblazon")
        cursor_blazon = dblazon.cursor()

        for impBlazon in importBlazon:
            cursor_blazon.execute("select blazon.CPF, blazon.id id, blazon.username username from (select us.id id, us.username username, (select TRIM(REPLACE(REPLACE(atr.value, '.', '' ), '-', '')) from EntryAttributeValue atr where atr.entry_id = us.id and atr.name = 'documentNumber') CPF, "
                                  "entry.state AS state from User us, Entry entry where entry.id = us.id) blazon where blazon.state = 'ACTIVE' and blazon.cpf = "+impBlazon[1])
            blazon = cursor_blazon.fetchall()

            if not blazon is None or blazon != []:
                list_import.append((blazon[0][1], blazon[0][2]))

        return list_import