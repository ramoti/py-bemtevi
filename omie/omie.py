#importando bibliotecas
from logging import error
from flask_restful import Resource, reqparse
from flask import Flask
from flask_restful import Resource, Api
from flask_jwt_extended import create_access_token, jwt_required
import mysql.connector
import config
import requests
import json

#endpoin de endereco
class Omie (Resource):

    #requer estar logado, funcao que chama as demais funcoes
    @jwt_required()
    def post(self):
        argumentos = reqparse.RequestParser()
        argumentos.add_argument("funcao", type=str, required=True, help="O campo 'funcao' deve ser informado!")
        argumentos.add_argument("id", type = int, required = True, help= "O campo 'id' deve ser informado!")
        argumentos.add_argument("parametros", type = dict, required = True, help= "O campo 'parametros' deve ser informado!")
        args = argumentos.parse_args()
        chamar_funcao = "Omie.{}(self,{},{})".format(args["funcao"],args['id'], args['parametros'])
        resultado  = eval(chamar_funcao)
        return resultado

    
    def retornar_integracoes_omie(self, id, args):

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

        comando = "SELECT codIntegracaoOmie, descricao FROM cli_omie_integracoes"

        try :
            cursor.execute(comando)
            integracoes = cursor.fetchall()
            lista_integracoes = []
            for integracao in integracoes:
                lista_integracoes.append({
                    "codigo":integracao[0],
                    "descricao":integracao[1]
                })
            conexao.close()

            return{
                "status":"1",
                "msg":"Consulta feita com sucesso",
                "integracoes": lista_integracoes
            },200


        except mysql.connector.Error as error:
            conexao.close()

            return {
                "status":"2",
                "msg":"Problema ao retornar integracoes omie",
                "error":error
            },400

    def adicionar_cliente_omie(self, id, args):

        headers = {
            'Content-Type': 'application/json'
        }

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

        comando = "SELECT app_key, app_secret FROM cli_omie_integracoes WHERE codIntegracaoOmie = {}".format(args['cod_integracao_omie'])

        cursor.execute(comando)
        variaveis = cursor.fetchone()

        payload = json.dumps({
            "call":"IncluirCliente",
            "app_key":variaveis[0],
            "app_secret":variaveis[1],
            "param":[{
                "codigo_cliente_integracao": args['cod_cliente'],
                "email": args["email"],
                "razao_social": args["razao_social"],
                "nome_fantasia": args["nome_fantasia"],
                "cnpj_cpf":args["cnpj_cpf"],
                "contato":args["contato"],
                "bairro":args["bairro"],
                "cep":args["cep"],
                "complemento":args["complemento"],
                "observacao":args["observacao"]
                }]
        })
        response = requests.post(url = "https://app.omie.com.br/api/v1/geral/clientes/", data= payload, headers= headers)
        response_json = response.json()
        
        if response.status_code == 500 :

            return {
                "status":"2",
                "msg":"problema ao tentar incluir cliente no omie",
                "error": response_json["faultstring"]
            },400

        comando = "INSERT INTO cli_omie_clientes (\
                    codCliente,\
                    codIntegracaoOmie,\
                    omie_CodCliente\
                ) \
                VALUES\
                    ('{}', '{}', '{}')".format(args["cod_cliente"],args["cod_integracao_omie"], response_json["codigo_cliente_omie"])
        try :
            cursor.execute(comando)
            conexao.commit()
            conexao.close()

            if cursor.rowcount == 1:

                return{
                    "status":"1",
                    "msg":"cliente criado com sucesso",
                    "id":response_json["codigo_cliente_omie"]
                },201

        except mysql.connector.Error as error:
            conexao.close()

            return{
                "status":"2",
                "msg":"Problema ao tentar incluir cliente na base",
                "error":str(error)
            },400

    
            