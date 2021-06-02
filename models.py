class Cadastro:
    def __init__(self,  nome, cpf, email, empresa, cnpj, responsavel, cpf_responsavel, data_criacao, data_fim_contrato, chamado, status, id=None ):
        self.id = id
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.empresa = empresa
        self.cnpj = cnpj
        self.responsavel = responsavel
        self.cpf_responsavel = cpf_responsavel
        self.data_criacao = data_criacao
        self.data_fim_contrato = data_fim_contrato
        self.chamado = chamado
        self.status = status


class Usuario:
    def __init__(self, usuario, nome, email, cpf, senha, data_criacao, data_revogacao, status, id=None ):
        self.id = id
        self.usuario = usuario
        self.nome = nome
        self.email = email
        self.cpf = cpf
        self.senha = senha
        self.data_criacao = data_criacao
        self.data_revogacao = data_revogacao
        self.status = status

