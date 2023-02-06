#importando bibliotecas
from logging import error
from flask_restful import Resource, reqparse
from flask import Flask
from flask_restful import Resource, Api
from flask_jwt_extended import create_access_token, jwt_required
import mysql.connector
import config


#endpoin de endereco
class FreeRadius (Resource):

    #requer estar logado, funcao que chama as demais funcoes
    @jwt_required()
    def post(self):
        argumentos = reqparse.RequestParser()
        argumentos.add_argument("funcao", type=str, required=True, help="O campo 'funcao' deve ser informado!")
        argumentos.add_argument("id", type = int, required = True, help= "O campo 'id' deve ser informado!")
        argumentos.add_argument("parametros", type = dict, required = True, help= "O campo 'parametros' deve ser informado!")
        args = argumentos.parse_args()
        chamar_funcao = "FreeRadius.{}(self,{},{})".format(args["funcao"],args['id'], args['parametros'])
        resultado  = eval(chamar_funcao)
        return resultado


    def retornar_informacoes_pelo_serial(self, id, args):

        #conexao com banco de dados
        conexao = mysql.connector.connect(
                host = config.conexao["host"],
                user= config.conexao["user"],
                password= config.conexao["password"],
                database= config.conexao["db"]
        )

        cursor = conexao.cursor()

        #comando para pegar a conexao do banco
        comando = "SELECT * from sis_conexoes_api WHERE ID = {}".format(id)

        cursor.execute(comando)
        banco = cursor.fetchone()
        conexao.close()


        #conexao com banco de dados do cliente
        conexao = mysql.connector.connect(
            host = banco[3],
            user= banco[4],
            password= banco[5],
            database= banco[6]
        )
        cursor = conexao.cursor()

        #comando para pegar as informacoes baseada no numero de serial
        comando = "SELECT \
                    fin_cobrancaclienteplanos_codplano,\
                    fin_cobrancaclienteplanos_codcobrancacliente,\
                    fin_cobrancaclienteplanos_codcobrancaclienteplanos\
                FROM\
                    pat_equipamentos \
                WHERE numeroserial = '{}';".format(args["numeroserial"])

        cursor.execute(comando)

        #deve ser fetchall para verificar se contem mais de 1 cadastrado
        dados = cursor.fetchall()

        #caso não encontre o serial number
        if dados == []:

            return {
                "status":"2",
                "msg":"nao encontrado",
                "error":"nao foi encontrado nenhum serial number"
            },404

        #caso tenha mais de um serial number
        if len(dados) > 1 :

            conexao.close()

            return {
                "status":"2",
                "msg":"Mais de um serial encontrado",
                "error":"foi encontrado mais de um serialnumber, sendo assim a api nao sabe qual retornar"
            }, 400

        #comando para pegar ssid e senhas baseada nas informacoes buscadas acima
        comando = "SELECT \
                    ssid,\
                    ssid5,\
                    senha,\
                    senha5,\
                    PK_codCobrancaClientePlano\
                FROM\
                    fin_cobrancasclienteplanos a \
                WHERE a.plan_planos_codplano = {}\
                    AND a.codcobrancasclienteplanos = {}\
                    AND a.fin_cobrancascliente_codcobrancascliente = {};".format(dados[0][0],dados[0][2],dados[0][1])

        cursor.execute(comando)

        #deve ser fetchall para verificar se contem mais de 1 cadastrado
        dados_plano = cursor.fetchall()

        #caso não encontre um plano linckado
        if dados_plano == []:

            return {
                "status":"2",
                "msg":"nao encontrado",
                "error":"nao foi encontrado nenhum plano atrelado"
            },404

        #caso tenha mais de um plano linkado
        if len(dados_plano) > 1 :

            return {
                "status":"2",
                "msg":"Mais de um plano com dados encontrado",
                "error":"foi encontrado mais de um plano com dados, sendo assim a api nao sabe qual retornar"
            },400


        #comando para pegar o login(username) baseada nas 3 primeiras informacoes coletadas
        comando = "SELECT \
                    login \
                FROM\
                    plan_logins a \
                WHERE a.`fin_cobrancasclienteplanos_codcobrancascliente` =  {}\
                    AND a.`fin_cobrancasclienteplanos_codcobrancasclienteplanos` = {}\
                    AND a.`fin_cobrancasclienteplanos_codplano` = {} ;".format(dados[0][1],dados[0][2],dados[0][0])

        cursor.execute(comando)

        #deve ser fetchall para verificar se contem mais de 1 cadastrado
        login = cursor.fetchall()

        #caso não encontre um login
        if login == []:

            return {
                "status":"2",
                "msg":"nao encontrado",
                "error":"nao foi encontrado nenhum login"
            },404

        #caso encontre mais de um login
        if len(login) > 1 :

            return {
                "status":"2",
                "msg":"Mais de um login encontrado",
                "error":"foi encontrado mais de um login, sendo assim a api nao sabe qual retornar"
            },400

        comando = "SELECT \
                    a.sis_conf_integracao_cod_conf \
                FROM\
                    sis_agentesexternos a \
                WHERE a.codagenteexterno = {}".format(args["cod_agente_externo"])

        cursor.execute(comando)
        agente = cursor.fetchone()

        if agente is None:

            return{
                "status":"2",
                "msg":"problema ao inserir",
                "error":"agente ou configuracao nao existentes"
            }

        #comando para pegar as informacoes do banco do radius
        comando = "SELECT \
                    * \
                FROM\
                    sis_conf_integracao \
                WHERE cod_conf_integracao = {}".format(agente[0])

        cursor.execute(comando)
        dados_conexao = cursor.fetchone()

        comando = "SELECT valor FROM sis_configuracoes WHERE chave = 'wan_dns1_ipv4';"
        cursor.execute(comando)
        wan_dns1_ipv4 = cursor.fetchone()
        
        comando = "SELECT valor FROM sis_configuracoes WHERE chave = 'wan_dns2_ipv4';"
        cursor.execute(comando)
        wan_dns2_ipv4 = cursor.fetchone()

        comando = "SELECT valor FROM sis_configuracoes WHERE chave = 'wan_dns1_ipv6';"
        cursor.execute(comando)
        wan_dns1_ipv6 = cursor.fetchone()

        comando = "SELECT valor FROM sis_configuracoes WHERE chave = 'wan_dns2_ipv6';"
        cursor.execute(comando)
        wan_dns2_ipv6 = cursor.fetchone()

        comando = "SELECT valor FROM sis_configuracoes WHERE chave = 'wan_type';"
        cursor.execute(comando)
        wan_type = cursor.fetchone()

        conexao.close()

        #conexao com o banco freeRadius
        conexao = mysql.connector.connect(
            host = dados_conexao[2],
            user= dados_conexao[3],
            password= dados_conexao[4],
            database= dados_conexao[5]
        )

        cursor = conexao.cursor()

        #comando para pegar a senha pppoe
        comando = "SELECT \
                    VALUE \
                FROM\
                    radcheck a \
                WHERE a.username = '{}'\
                    AND attribute = 'Cleartext-Password'".format(login[0][0])

        cursor.execute(comando)

        #deve ser fetchall para verificar se contem mais de 1 cadastrado
        senha_pppoe  = cursor.fetchall()

        #caso não encontre o login no freeRadius
        if senha_pppoe == []:

            return {
                "status":"2",
                "msg":"nao encontrado",
                "error":"o username cadastrado no bemtevi nao foi encontrado na base de dados do freeradius"
            },404

        #caso tenha mais de um login no freeradius
        if len(senha_pppoe) > 1 :

            {
                "status":"2",
                "msg":"Mais de um login encontrado",
                "error":"foi encontrado mais de um login na base do freeradius, sendo assim a api nao sabe qual retornar"
            },400

        #caso nao tenha ssid cadastrado deve retornar tudo que vem antes do @ do username
        if dados_plano[0][0] is None:
            login_quebrado = login[0][0].split("@")

            ssid = login_quebrado[0]
            ssid = ssid.upper()

        else :
            ssid = dados_plano[0][0]

        #caso nao tenha senha deve se retornar os 8 primeiro digitos do numero de serial
        if dados_plano[0][2] is None:

            senha = args["numeroserial"][:8]
            
        else:
            senha = dados_plano[0][2]

        return {
            "status":"1",
            "msg":"consulta feita com sucesso",
            "dados": {
                "ssid":ssid,
                "ssid5":ssid,
                "senha":senha,
                "senha5":senha,
                "pk_cod_cobranca_cliente_plano":dados_plano[0][4],
                "username":login[0][0],
                "senha_pppoe":senha_pppoe[0][0],
                "wan_dns1_ipv4":wan_dns1_ipv4[0],
                "wan_dns2_ipv4":wan_dns2_ipv4[0],
                "wan_dns1_ipv6":wan_dns1_ipv6[0],
                "wan_dns2_ipv6":wan_dns2_ipv6[0],
                "wan_type":wan_type[0]
            }
        }

    
    def retornar_grupo_regras_username(self, id, args):

        #conexao com banco de dados
        conexao = mysql.connector.connect(
                host = config.conexao["host"],
                user= config.conexao["user"],
                password= config.conexao["password"],
                database= config.conexao["db"]
        )

        cursor = conexao.cursor()

        #comando para pegar a conexao do banco
        comando = "SELECT * from sis_conexoes_api WHERE ID = {}".format(id)

        cursor.execute(comando)
        banco = cursor.fetchone()
        conexao.close()


        #conexao com banco de dados do cliente
        conexao = mysql.connector.connect(
            host = banco[3],
            user= banco[4],
            password= banco[5],
            database= banco[6]
        )
        cursor = conexao.cursor()

        
        comando = "SELECT \
                    a.sis_conf_integracao_cod_conf \
                FROM\
                    sis_agentesexternos a \
                WHERE a.codagenteexterno = {}".format(args["cod_agente_externo"])

        cursor.execute(comando)
        agente = cursor.fetchone()

        if agente is None:

            return{
                "status":"2",
                "msg":"problema ao inserir",
                "error":"agente ou configuracao nao existentes"
            }

        #comando para pegar as informacoes do banco do radius
        comando = "SELECT \
                    * \
                FROM\
                    sis_conf_integracao \
                WHERE cod_conf_integracao = {}".format(agente[0])

        cursor.execute(comando)
        dados_conexao = cursor.fetchone()
        conexao.close()

        #conexao com o banco freeRadius
        conexao = mysql.connector.connect(
            host = dados_conexao[2],
            user= dados_conexao[3],
            password= dados_conexao[4],
            database= dados_conexao[5]
        )

        cursor = conexao.cursor()

        
        comando = "SELECT \
                    groupname \
                FROM\
                    radusergroup \
                WHERE username = '{}' ".format(args["login"])

        cursor.execute(comando)

        groupname = cursor.fetchone()

        if groupname is None:

            return{
                "status":"2",
                "msg":"nao encontrado",
                "error":"nao foi encontrado o username ou nao esta em uma regra"
            }

        return {
            "status":"1",
            "msg":"consulta feita com sucesso",
            "data":{
                "username":args["login"],
                "groupname":groupname[0]
            }
        }



    def adicionar_login(self, id, args):

        #conexao com banco de dados
        conexao = mysql.connector.connect(
                host = config.conexao["host"],
                user= config.conexao["user"],
                password= config.conexao["password"],
                database= config.conexao["db"]
        )

        cursor = conexao.cursor()

        #comando para pegar a conexao do banco
        comando = "SELECT * from sis_conexoes_api WHERE ID = {}".format(id)

        cursor.execute(comando)
        banco = cursor.fetchone()
        conexao.close()


        #conexao com banco de dados do cliente
        conexao = mysql.connector.connect(
            host = banco[3],
            user= banco[4],
            password= banco[5],
            database= banco[6]
        )
        cursor = conexao.cursor()

        
        comando = "SELECT \
                    a.sis_conf_integracao_cod_conf \
                FROM\
                    sis_agentesexternos a \
                WHERE a.codagenteexterno = {}".format(args["cod_agente_externo"])

        cursor.execute(comando)
        agente = cursor.fetchone()

        if agente is None:

            return{
                "status":"2",
                "msg":"problema ao inserir",
                "error":"agente ou configuracao nao existentes"
            }

        #comando para pegar as informacoes do banco do radius
        comando = "SELECT \
                    * \
                FROM\
                    sis_conf_integracao \
                WHERE cod_conf_integracao = {}".format(agente[0])

        cursor.execute(comando)
        dados_conexao = cursor.fetchone()
        conexao.close()

        #conexao com o banco freeRadius
        conexao = mysql.connector.connect(
            host = dados_conexao[2],
            user= dados_conexao[3],
            password= dados_conexao[4],
            database= dados_conexao[5]
        )

        cursor = conexao.cursor()

        comando = "INSERT INTO radcheck (username, attribute, op, VALUE) \
                    VALUES\
                    (\
                        '{}',\
                        'Cleartext-Password',\
                        ':=',\
                        '{}'\
                    )".format(args["login"], args["senha"])

        try :
            cursor.execute(comando)
            conexao.commit()

            if cursor.rowcount == 1:

                comando = "SELECT \
                            MAX(id) \
                        FROM\
                            radcheck;"

                cursor.execute(comando)
                id = cursor.fetchone()

                return{
                    "status":"1",
                    "msg":"insercao feita com sucesso",
                    "id":id[0]
                }

            return {
                "status":"2",
                "msg":"problema ao inserir login",
                "error":"nao foi possivel incluir na tabela do freeRadius"
            }

        except mysql.connector.Error as error:

            return {
                "status":"2",
                "msg":"nao foi possivel incluir",
                "error":error
            }