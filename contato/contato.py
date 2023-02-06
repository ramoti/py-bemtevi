#importando bibliotecas
from logging import error
from flask_restful import Resource, reqparse
from flask import Flask
from flask_restful import Resource, Api
from flask_jwt_extended import create_access_token, jwt_required
import mysql.connector
import config


#endpoin de endereco
class Contato (Resource):

    #requer estar logado, funcao que chama as demais funcoes
    @jwt_required()
    def post(self):
        argumentos = reqparse.RequestParser()
        argumentos.add_argument("funcao", type=str, required=True, help="O campo 'funcao' deve ser informado!")
        argumentos.add_argument("id", type = int, required = True, help= "O campo 'id' deve ser informado!")
        argumentos.add_argument("parametros", type = dict, required = True, help= "O campo 'parametros' deve ser informado!")
        args = argumentos.parse_args()
        chamar_funcao = "Contato.{}(self,{},{})".format(args["funcao"],args['id'], args['parametros'])
        resultado  = eval(chamar_funcao)
        return resultado


    #funcao para adicionar celular de um cliente
    def adicionar_celular(self, id, args):

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

        #comando para inserir celular
        comando = "INSERT INTO cli_celulares (\
                    cli_clientes_codcliente,\
                    numero\
                    ) \
                VALUES\
                    ('{}','{}')".format(
                        args["cod_cliente"],
                        args["numero"]
                    )
        try:
            cursor.execute(comando)
            conexao.commit()


            # se tudo deu certo
            if cursor.rowcount == 1:
                id = cursor.lastrowid

                conexao.close()

                return{
                    "status":"1",
                    "msg":"celular adicionado com sucesso",
                    "id":id
                },201

        # caso de algum erro
        except mysql.connector.Error as error:
            conexao.close()
            
            return{
                "status":"2",
                "msg":"Problema ao tentar incluir celular",
                "error": error
            },400

    #funcao para adicionar celular de um cliente
    def adicionar_email(self, id, args):

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

        comando = "INSERT INTO cli_emails (\
                    cli_clientes_codcliente,\
                    email)\
                VALUES ('{}','{}')".format(
                    args['cod_cliente'],
                    args['email']
                )

        try:
            cursor.execute(comando)
            conexao.commit()
            
            if cursor.rowcount == 1:

                id = cursor.lastrowid

                conexao.close()

                return{
                    "status":"1",
                    "msg":"email adicionado com sucesso",
                    "id":id
                },201


        except mysql.connector.Error as error:

            conexao.close()
            
            return {
                "status":"2",
                "msg":"Problema ao tentar incluir email",
                "error":error
            },400

    def adicionar_rede_social(self, id, args):

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


        comando = "INSERT INTO cli_redessociais (codCliente, tipoRedeSocial, Link) \
                    VALUES\
                ('{}','{}','{}')".format(args['cod_cliente'],args['tipo_rede_social'],args['link'])
        
        try:

            cursor.execute(comando)
            conexao.commit()

            if cursor.rowcount == 1:
                id = cursor.lastrowid

                conexao.close()

                return{
                    "status":"1",
                    "msg":"rede social adicionada com sucesso",
                    "id":id
                },201

        except mysql.connector.Error as error:

            conexao.close()

            return{
                "status":"2",
                "msg":"Problema ao tentar inserir rede social",
                "erro": error
            },400