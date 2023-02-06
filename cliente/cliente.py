#importando modulos necessarios 
from logging import error
from flask_restful import Resource, reqparse
from flask import Flask
from flask_restful import Resource, Api
from flask_jwt_extended import create_access_token, jwt_required
import mysql.connector
import config


#endpoint de criar cliente
class Cliente(Resource):


    #requer estar logado, funcao que chama as demais funcoes
    @jwt_required()
    def post(self):
        argumentos = reqparse.RequestParser()
        argumentos.add_argument("funcao", type=str, required=True, help="O campo 'funcao' deve ser informado!")
        argumentos.add_argument("id", type = int, required = True, help= "O campo 'id' deve ser informado!")
        argumentos.add_argument("parametros", type = dict, required = True, help= "O campo 'parametros' deve ser informado!")
        args = argumentos.parse_args()
        chamar_funcao = "Cliente.{}(self,{},{})".format(args["funcao"],args['id'], args['parametros'])
        resultado  = eval(chamar_funcao)
        return resultado


    #funcao para adicionar cliente no sistema
    def adicionar_cliente(self,id,args):

        #conexao com banco de dados e acordo com o cliente
        conexao = mysql.connector.connect(
                host = config.conexao["host"],
                user= config.conexao["user"],
                password= config.conexao["password"],
                database= config.conexao["db"]
        )
        cursor = conexao.cursor()
        comando = "SELECT * from sis_conexoes_api WHERE ID = {}".format(id)
        cursor.execute(comando)
        banco = cursor.fetchone()
        conexao.close()


        #conexao no banco de dados do cliente
        conexao = mysql.connector.connect(
            host = banco[3],
            user= banco[4],
            password= banco[5],
            database= banco[6]
        )
        cursor = conexao.cursor()

        comando = "SELECT cpfcnpj, nome FROM cli_clientes WHERE cpfcnpj = '{}' AND situacao != 1".format(args['cpfcnpj'])
        cursor.execute(comando)
        cliente = cursor.fetchone()


        #se o cliente ja existe e NAO esta arquivado
        if cliente is not None:
            return {
                "status":"2",
                "msg":"O cpf/cnpj ja existe e o cliente nao esta arquivado",
                "erro":{
                    "nome":cliente[1],
                    "cpfcnpj":cliente[0]
                }
            },400


        #inserir o cliente na tabela
        comando = "INSERT INTO cli_clientes (nome, cpfcnpj, pessoafisica, inscricaoestadual, razaosocial, rg) VALUES (%s,%s,%s,%s,%s,%s)"
        val = (args["nome"],args["cpfcnpj"],args["pessoafisica"], args["inscricaoestadual"], args["razaosocial"], args['rg'])

        try:
            cursor.execute(comando,val)
            conexao.commit()

            id = cursor.lastrowid

            #caso de tudo certo
            if cursor.rowcount == 1:
                conexao.close()
                return {
                    "status":"1", 
                    "msg":"Cliente adicionado com sucesso!",
                    "cliente" : id
                },201

        #caso de algum erro
        except mysql.connector.Error as error:
            conexao.close()
            return{
                "status":"2",
                "msg":"Probema ao adicionar cliente",
                "erro":error
            },400

    
    #funcao para consultar se cpf ou cnpj ja existe
    def consultar_cliente_cpfcnpj(self,id,args):


        #conexao com banco de dados
        conexao = mysql.connector.connect(
                host = config.conexao["host"],
                user= config.conexao["user"],
                password= config.conexao["password"],
                database= config.conexao["db"]
        )
        cursor = conexao.cursor()
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
        comando = "SELECT * from cli_clientes WHERE cpfcnpj = '{}'".format(args['cpfcnpj'])

        cursor.execute(comando)

        cliente = cursor.fetchone()
        conexao.close()


        #Caso encontre um cliente com tal cpf ou cnpj
        if cliente is not None:

            return{
                "status":"1",
                "msg":"Consulta feita com sucesso!",
                "cliente": {
                    "codcliente":cliente[0],
                    "nome":cliente[1],
                    "cpfcnpj":cliente[2],
                    "razaosocial":cliente[5],
                    "rg":cliente[7]
                }
            },200
        

        #caso nao encontre nenhum cliente
        else :

            return {
                "status":"1",
                "msg":"Nenhum cliente encontrado"
            },200



    def retornar_cliente (self,id,args):

        #conexao com banco de dados
        conexao = mysql.connector.connect(
                host = config.conexao["host"],
                user= config.conexao["user"],
                password= config.conexao["password"],
                database= config.conexao["db"]
        )
        cursor = conexao.cursor()
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
                    codcliente,\
                    nome,\
                    cpfcnpj,\
                    inscricaoestadual,\
                    pessoafisica,\
                    razaoSocial,\
                    datahoracadastro,\
                    rg,\
                    datanascimento,\
                    nomemae,\
                    nomepai,\
                    codusuarioresponsavel,\
                    obs,\
                    datacontrato,\
                    dataativacao,\
                    datacabeamento,\
                    situacao,\
                    contato,\
                    inscricaoestadual_uf,\
                    reterISS,\
                    contribuinteParaOperacoesInterEstaduais \
                FROM\
                    cli_clientes \
                WHERE codcliente = {}".format(args['cod_cliente'])
        cursor.execute(comando)
        cliente = cursor.fetchone()
        if cliente is not None:

            return{
                "status":"1",
                "msg":"consulta feita com sucesso",
                "cliente":{
                    "cod_cliente": cliente[0],
                    "nome":cliente[1],
                    "cpfcnpj":cliente[2],
                    "inscricao_estadual":cliente[3],
                    "pessoa_fisica": cliente[4],
                    "razaoSocial":cliente[5],
                    "datahoracadastro":str(cliente[6]),
                    "rg":cliente[7],
                    "datanascimento":str(cliente[8]),
                    "nomemae":cliente[9],
                    "nomepai":cliente[10],
                    "codusuarioresponsavel":cliente[11],
                    "obs":cliente[12],
                    "datacontrato":str(cliente[13]),
                    "dataativacao":str(cliente[14]),
                    "datacabeamento":str(cliente[15]),
                    "situacao":cliente[16],
                    "contato":cliente[17],
                    "inscricaoestadual_uf":cliente[18],
                    "reterISS":cliente[19],
                    "contribuinteParaOperacoesInterEstaduais": cliente[20]
                }
            },200

        return {
            "status":"2",
            "msg":"cliente não encontrado",
            "error": "informe um cod_cliente que exista no sistema"
        },400
        conexao.close()
    def retornar_planos_cliente(self,id,args):

        lista_planos = []
        #conexao com banco de dados
        conexao = mysql.connector.connect(
                host = config.conexao["host"],
                user= config.conexao["user"],
                password= config.conexao["password"],
                database= config.conexao["db"]
        )
        cursor = conexao.cursor()
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
                    * \
                FROM\
                    fin_cobrancascliente a \
                WHERE a.cli_clientes_codcliente = {} \
                    AND a.modo = 0 \
                    AND a.removida = 0 ;".format(args['cod_cliente'])
        cursor.execute(comando)
        cobrancas_cliente = cursor.fetchall()

        for cobranca in cobrancas_cliente:

            comando = "SELECT \
                        a.plan_planos_codplano,\
                        a.precocliente,\
                        a.cortesia,\
                        a.datacadastro,\
                        a.dataativacao,\
                        a.datadesativacao,\
                        a.PK_codCobrancaClientePlano\
                    FROM\
                        fin_cobrancasclienteplanos a \
                        WHERE a.fin_cobrancascliente_codcobrancascliente = {} ;".format(cobranca[0])
            cursor.execute(comando)
            planos = cursor.fetchall()

            for plano in planos :

                if plano is None:
                    pass
                else:
                    lista_planos.append({
                        "cod_plano":plano[0],
                        "preco_cliente":plano[1],
                        "cortesia":plano[2],
                        "data_cadastro":str(plano[3]),
                        "data_ativacao":str(plano[4]),
                        "data_desativacao":str(plano[5]),
                        "cod_cobranca_cliente_plano":plano[6]
                    })
        return {
            "status":"1",
            "msg":"consulta feita com sucesso",
            "planos":lista_planos
        },200

    def retornar_cliente_pela_central(self,id,args):

        #conexao com banco de dados
        conexao = mysql.connector.connect(
                host = config.conexao["host"],
                user= config.conexao["user"],
                password= config.conexao["password"],
                database= config.conexao["db"]
        )
        cursor = conexao.cursor()
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
                    a.codcliente,\
                    a.nome,\
                    a.cpfcnpj,\
                    a.pessoafisica,\
                    a.razaosocial,\
                    a.situacao \
                FROM\
                    cli_clientes a \
                WHERE a.centralassinantelogin = '{}' \
                    AND a.centralassinantesenha = '{}' ;".format(args['central_login'], args['central_senha'])
        cursor.execute(comando)
        cliente = cursor.fetchone()
        if cliente is not None:
            return {
                "status":"1",
                "msg":"cliente encontrado",
                "cliente":{
                    "codcliente":cliente[0],
                    "nome":cliente[1],
                    "cpfcnpj":cliente[2],
                    "pessoafisica":cliente[3],
                    "razaosocial":cliente[4],
                    "situacao":cliente[5],
                    "login":args['central_login'],
                    "senha":args['central_senha']
                }
            },200

        return{
            "status":"1",
            "msg":"cliente não encontrado"
        },404

    def retornar_email_cliente_atualizado(self,id,args):
        
        #conexao com banco de dados
        conexao = mysql.connector.connect(
                host = config.conexao["host"],
                user= config.conexao["user"],
                password= config.conexao["password"],
                database= config.conexao["db"]
        )
        cursor = conexao.cursor()
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
                    MAX(a.codemail),\
                    a.email \
                FROM\
                    cli_emails a \
                WHERE a.cli_clientes_codcliente = {};".format(args['cod_cliente'])
        cursor.execute(comando)
        email = cursor.fetchone()
        
        if email is None:
            return {
                "status":"1",
                "msg":"Não foi encontrado email para esse código de cliente",
            },400
        return {
            "status":"1",
            "msg":"Consulta feita com sucesso",
            "dados_email": {
                "cod_email":email[0],
                "email":email[1]
            }
        },200

    def retornar_celulares_cliente_atualizado(self,id,args):
        
        #conexao com banco de dados
        conexao = mysql.connector.connect(
                host = config.conexao["host"],
                user= config.conexao["user"],
                password= config.conexao["password"],
                database= config.conexao["db"]
        )
        cursor = conexao.cursor()
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
                    MAX(a.codcelular),\
                    a.numero \
                FROM\
                    cli_celulares a \
                WHERE a.cli_clientes_codcliente = {} ;".format(args['cod_cliente'])
        cursor.execute(comando)
        celular = cursor.fetchone()
        
        if celular is None:
            return {
                "status":"1",
                "msg":"Não foi encontrado celulares para esse código de cliente",
            }

        return {
            "status":"1",
            "msg":"Consulta feita com sucesso",
            "dados_celular": {
                "cod_celular":celular[0],
                "celular":celular[1]
            }
        },200