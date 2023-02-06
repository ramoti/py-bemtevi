#importando bibliotecas
from logging import error
from flask_restful import Resource, reqparse
from flask import Flask
from flask_restful import Resource, Api
from flask_jwt_extended import create_access_token, jwt_required
import mysql.connector
import config
from datetime import date, datetime



#endpoin de endereco
class Logins (Resource):

    #requer estar logado, funcao que chama as demais funcoes
    @jwt_required()
    def post(self):
        argumentos = reqparse.RequestParser()
        argumentos.add_argument("funcao", type=str, required=True, help="O campo 'funcao' deve ser informado!")
        argumentos.add_argument("id", type = int, required = True, help= "O campo 'id' deve ser informado!")
        argumentos.add_argument("parametros", type = dict, required = True, help= "O campo 'parametros' deve ser informado!")
        args = argumentos.parse_args()
        chamar_funcao = "Logins.{}(self,{},{})".format(args["funcao"],args['id'], args['parametros'])
        resultado  = eval(chamar_funcao)
        return resultado

    

    def adicionar_login_plano(self, id, args):

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
                    * \
                FROM\
                    fin_cobrancasclienteplanos a \
                WHERE a.plan_planos_codplano = {}\
                    AND a.codcobrancasclienteplanos = {} \
                    AND a.fin_cobrancascliente_codcobrancascliente = {} ;".format(
                        args["cod_plano"],
                        args["cod_cobranca_cliente_planos"],
                        args["cod_cobranca_cliente"],
                    )
        cursor.execute(comando)
        fin_cobranca = cursor.fetchone()
        
        if fin_cobranca is None:

            return{
                "status":"2",
                "msg":"problema na inclusao",
                "error":"os dados de plano, cod_cobranca_cliente e cod_cobranca_cliente_planos nao foram encontrados"
            }

        comando = "SELECT \
                    * \
                FROM\
                    plan_planoitemacesso a \
                WHERE a.codplanoitem = {} \
                    AND a.plan_planos_codplano = {} ;".format(
                        args["cod_item"],
                        args["cod_plano"]
                    )

        cursor.execute(comando)
        item = cursor.fetchone()

        if item is None:

            return {
                "status":"2",
                "msg":"problema ao tentar incluir",
                "error":"os dados de item nao foram encontrados"
            }

        comando = "SELECT \
                    * \
                FROM\
                    plan_logins a \
                WHERE a.login = '{}' ;".format(args["login"])

        cursor.execute(comando)
        login = cursor.fetchone()

        datahora = datetime.now()
        datahora = datahora.strftime('%Y-%m-%d %H:%M:%S')
        comando = "SELECT \
                    descricao \
                FROM\
                    plan_planos \
                WHERE codplano = {}".format(
                    args["cod_plano"]
                )
        

        
        cursor.execute(comando)
        plano = cursor.fetchone()

        if plano is None:

            return{
                "status":"2",
                "msg":"problema ao tentar incluir",
                "error":"nao foi possivel encontrar a descricao do plano baseado no codplano {}".format(args["cod_plano"])
            }

        comando = "SELECT \
                    a.fin_tiposcobranca_codtiposcobranca \
                FROM\
                    fin_cobrancascliente a \
                WHERE a.codcobrancascliente = {} ;".format(
                    args["cod_cobranca_cliente"]
                )

        cursor.execute(comando)
        tipo_cobranca = cursor.fetchone()

        if tipo_cobranca is None:
            return{
                "status":"2",
                "msg":"problema ao tentar incluir",
                "error":"nao foi possivel encontrar o tipo de cobranca baseado no cocobrancacliente {}".format(args["cod_cobranca_cliente"])
            }

        comando = "SELECT \
                    descricao \
                FROM\
                    fin_tiposcobranca a\
                WHERE a.codtiposcobranca = {};".format(
                    tipo_cobranca[0]
                )

        cursor.execute(comando)
        tipo_cobranca = cursor.fetchone()
        if tipo_cobranca is None:
            return{
                "status":"2",
                "msg":"problema ao tentar incluir",
                "error":"nao foi possivel encontrar a descricao de cobranca baseado no tipo de cobranca {}".format(tipo_cobranca[0])
            }

        if login is not None:

            return{
                "status":"2",
                "msg":"problema ao tentar incluir",
                "error":"o login ja existe"
            }

        comando = "INSERT INTO plan_logins (\
                    fin_cobrancasclienteplanos_codplano,\
                    fin_cobrancasclienteplanos_codcobrancascliente,\
                    fin_cobrancasclienteplanos_codcobrancasclienteplanos,\
                    plan_planoitemacesso_codplano,\
                    plan_planoitemacesso_codplanoitem,\
                    login,\
                    loginpai\
                ) \
                VALUES\
                    ({}, {}, {}, {}, {},'{}','{}');".format(
                        args["cod_plano"],
                        args["cod_cobranca_cliente"],
                        args["cod_cobranca_cliente_planos"],
                        args["cod_plano"],
                        args["cod_item"],
                        args["login"],
                        args["login_pai"]
                    )        
        try:

            cursor.execute(comando)

            if cursor.rowcount == 1:
                
                #conexao.commit()
                comando = "INSERT INTO fin_muralalteracoes (\
                            codcliente,\
                            codusuario,\
                            tipooperacao,\
                            datahora,\
                            descricao\
                        ) \
                        VALUES\
                            (\
                                {},\
                                1,\
                                9,\
                                '{}',\
                                'Cobrança do Cliente: {}\
                            Plano: {}\
                            Plano Item: {}\
                            Login: {}\
                            Senha: {}'\
                        )".format(
                            args["cod_cliente"],
                            datahora,
                            tipo_cobranca[0],
                            plano[0],
                            plano[0],
                            args["login"],
                            args["senha"]

                        )

            try:
                cursor.execute(comando)
                conexao.commit()
                conexao.close()

                return {
                    "status":"1",
                    "msg":"inclusao feita com sucesso"
                    }

            except mysql.connector.Error as error:

                return{
                    "status":"2",
                    "msg":"problema ao tentar incluir no banco",
                    "error":error
                }

        except mysql.connector.Error as error:

            return{
                "status":"2",
                "msg":"problema ao tentar incluir no banco",
                "error":error
            }

    def retonar_logins_cpf(self, id, args):

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
                    codcliente \
                FROM\
                    cli_clientes a \
                WHERE cpfcnpj = {} ;".format(args["cpfcnpj"])

        cursor.execute(comando)
        codcliente = cursor.fetchone()
        codcliente = codcliente[0]

        comando = f"SELECT \
                    a.codcobrancascliente \
                FROM\
                    fin_cobrancascliente a \
                WHERE cli_clientes_codcliente = {codcliente} ;"
        cursor.execute(comando)
        cobrancas_cliente = cursor.fetchall()
        cobrancas_cliente
        lista_logins = []
        for cobranca in cobrancas_cliente:

            comando = f"SELECT \
                            a.codcobrancasclienteplanos,\
                            a.plan_planos_codplano \
                        FROM\
                            fin_cobrancasclienteplanos a \
                        WHERE a.fin_cobrancascliente_codcobrancascliente = {cobranca[0]} ;"

            cursor.execute(comando)
            planos_cliente = cursor.fetchall()

            for plano in planos_cliente:

                comando ="SELECT \
                            login \
                        FROM\
                            plan_logins a \
                        WHERE a.fin_cobrancasclienteplanos_codcobrancascliente = {} \
                        AND a.fin_cobrancasclienteplanos_codcobrancasclienteplanos = {}\
                        AND a.fin_cobrancasclienteplanos_codplano = {} ;".format(
                            cobranca[0],
                            plano[0],
                            plano[1]
                        )
                cursor.execute(comando)
                logins = cursor.fetchall()
                for login in logins:
                    lista_logins.append(login[0])

        return {
            "status":"1",
            "msg":"consulta feita com sucesso",
            "lista_logins":lista_logins
        }