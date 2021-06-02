import cx_Oracle
import urllib3
from config import db
urllib3.disable_warnings()
from datetime import datetime
import time

sysdate = datetime.now().strftime('%d/%m/%Y')
sysdateCad = datetime.now().strftime('%Y%m%d')

print(str(datetime.now().strftime('%d/%m/%Y-%H:%M:%S')+': Inicio da atividade'))

#--------------------------- Lê arquivo de password ---------------------------
config = open('C:/Automations/generalSettings/credentials.txt', 'r').readlines()
list_config = []

for n in config:
     list_config.append(n.rstrip())

# --------------------------- Abrindo conexão com Qualitor ---------------------------
#PRD
dsn_tns = "(DESCRIPTION=(CONNECT_TIMEOUT=5)(TRANSPORT_CONNECT_TIMEOUT=3)(RETRY_COUNT=3)(ADDRESS_LIST=(LOAD_BALANCE=on)(ADDRESS=(PROTOCOL=TCP)(HOST=172.33.5.49)(PORT=1521))(ADDRESS=(PROTOCOL=TCP)(HOST=172.33.5.50)(PORT=1521))(ADDRESS=(PROTOCOL=TCP)(HOST=172.33.5.51)(PORT=1521)))(CONNECT_DATA=(SERVICE_NAME=QUALITP_gru1mw)))"
conn = cx_Oracle.connect(user=''+(list_config[8][list_config[8].find('=')+1:]).strip()+'', password=''+(list_config[9][list_config[9].find('=')+1:]).strip()+'', dsn=dsn_tns)
c = conn.cursor()
c.execute("select hd_chamado.cdchamado as chamado,data_fim.dtinformacao as DATA_FIM_CONTRATO,upper(nome_ter.nminformacao) as NOME_TERCEIRO,to_char(regexp_replace(cpf_ter.vlinformacao,'[^[:digit:]]'),'00000000000') as CPF_TERCEIRO, "
"upper(email_ter.nminformacao) as EMAIL_TERCEIRO,upper(nome_emp_ter.nminformacao) as NOME_EMPRESA_TERCEIRO,regexp_replace(cnpj_ter.nminformacao,'[^[:digit:]]') as CNPJ_EMPRESA_TERCEIRO, "
"upper(resp_sol.nminformacao) as RESPONSAVEL_SOLICITANTE,to_char(regexp_replace(cpf_resp.vlinformacao,'[^[:digit:]]'),'00000000000') as CPF_RESPONSAVEL,regexp_replace(tel_ter.vlinformacao,'[^[:digit:]]') as TELEFONE_TERCEIRO,hd_chamado.dtchamado as abertura, "
"hd_chamado.dttermino termino_chamado,hd_estruturasubsituacaoitem.nmsubsituacao as etapa "
"from hd_chamado left outer join hd_chamadoinformacaoadicional cpf_resp on cpf_resp.cdchamado = hd_chamado.cdchamado and cpf_resp.cdtipoinformacaoadicional = 3829 "
"left outer join hd_chamadoinformacaoadicional cpf_ter on cpf_ter.cdchamado = hd_chamado.cdchamado and cpf_ter.cdtipoinformacaoadicional = 3824 "
"left outer join hd_chamadoinformacaoadicional resp_sol on resp_sol.cdchamado = hd_chamado.cdchamado and resp_sol.cdtipoinformacaoadicional = 3828 "
"left outer join hd_chamadoinformacaoadicional cnpj_ter on cnpj_ter.cdchamado = hd_chamado.cdchamado and cnpj_ter.cdtipoinformacaoadicional = 3827 "
"left outer join hd_chamadoinformacaoadicional nome_ter on nome_ter.cdchamado = hd_chamado.cdchamado and nome_ter.cdtipoinformacaoadicional = 3823 "
"left outer join hd_chamadoinformacaoadicional nome_emp_ter on nome_emp_ter.cdchamado = hd_chamado.cdchamado and nome_emp_ter.cdtipoinformacaoadicional = 3826 "
"left outer join hd_chamadoinformacaoadicional data_fim on data_fim.cdchamado = hd_chamado.cdchamado and data_fim.cdtipoinformacaoadicional = 3831 "
"left outer join hd_chamadoinformacaoadicional email_ter on email_ter.cdchamado = hd_chamado.cdchamado and email_ter.cdtipoinformacaoadicional = 3825 "
"left outer join hd_chamadoinformacaoadicional tel_ter on tel_ter.cdchamado = hd_chamado.cdchamado and tel_ter.cdtipoinformacaoadicional = 3830 "
"left outer join hd_estruturasubsituacaoitem on hd_estruturasubsituacaoitem.cdestrutura = hd_chamado.cdestrutura and hd_estruturasubsituacaoitem.nrsequencia = hd_chamado.cdsubsituacao "
"where cdequipe = 761 and hd_estruturasubsituacaoitem.nmsubsituacao = 'CSC - REALIZAR  PROCESSAMENTO' and hd_chamado.dtchamado >= sysdate-3")
dados_chamados = c.fetchall()
c.close()

SQL_CRIA_CADASTRO = 'INSERT into cadastro (categoria, nome,cpf,email,empresa,cnpj,responsavel,cpf_responsavel,data_criacao,data_fim_contrato, chamado, status) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

class Jobs:
    def __init__(self, db):
        self.__db = db

    #Verifica novos chamados que não foram processados e insere no Sistema
    def cad_via_chamados(self):
        for chamados in dados_chamados:
            #data_fim_contrato = datetime.strptime(chamados[1], '%d/%m/%Y').date().strftime('%Y%m%d')
            data_fim_contrato = chamados[1].strftime('%Y%m%d')
            cursor = self.__db.cursor()
            cursor.execute('SELECT 1 from cadastro where chamado=%s or (cpf=%s and status = "ATIVO")',(chamados[0],chamados[3],))
            chamado_gester = cursor.fetchall()
            if chamado_gester == []:
                try:
                    cursor.execute(SQL_CRIA_CADASTRO, (1,chamados[2].upper(), chamados[3],chamados[4].upper(), chamados[5].upper(),chamados[6],chamados[7].upper(),chamados[8],sysdateCad,data_fim_contrato,chamados[0],'ATIVO'))
                    self.__db.commit()
                    cursor.close()
                except:
                    pass
            self.__db.commit()

#Execução das atividades
while 1:
    Jobs(db).cad_via_chamados()
    time.sleep(600)
