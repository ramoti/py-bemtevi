#importando bibliotecas
from logging import error
from flask_restful import Resource, reqparse
from flask import Flask
from flask_restful import Resource, Api
from flask_jwt_extended import create_access_token, jwt_required
import mysql.connector
import config


#endpoin de endereco
class Configuracao (Resource):

    #requer estar logado, funcao que chama as demais funcoes
    @jwt_required()
    def post(self):
        argumentos = reqparse.RequestParser()
        argumentos.add_argument("funcao", type=str, required=True, help="O campo 'funcao' deve ser informado!")
        argumentos.add_argument("id", type = int, required = True, help= "O campo 'id' deve ser informado!")
        argumentos.add_argument("parametros", type = dict, required = True, help= "O campo 'parametros' deve ser informado!")
        args = argumentos.parse_args()
        chamar_funcao = "Configuracao.{}(self,{},{})".format(args["funcao"],args['id'], args['parametros'])
        resultado  = eval(chamar_funcao)
        return resultado


    #funcao para adicionar celular de um cliente
    def retornar_configuracoes_onu(self, id, args):

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
        comando = comando = "SELECT \
                    * \
                FROM\
                    sis_configuracoes \
                WHERE secao = 'integracao.onu'"
        cursor.execute(comando)
        configuracoes = cursor.fetchall()
        lista_config = []
        for configuracao in configuracoes:

            lista_config.append({
                "chave":configuracao[1],
                "valor":configuracao[3]
            })

        return {
            "status":"1",
            "msg":"consulta feita com sucesso",
            "lista_config": lista_config
        }