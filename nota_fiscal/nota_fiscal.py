#importando bibliotecas
from logging import error
from flask_restful import Resource, reqparse
from flask import Flask
from flask_restful import Resource, Api
from flask_jwt_extended import create_access_token, jwt_required
import mysql.connector
import config


#endpoin de endereco
class Nota_fiscal (Resource):

    #requer estar logado, funcao que chama as demais funcoes
    @jwt_required()
    def post(self):
        argumentos = reqparse.RequestParser()
        argumentos.add_argument("funcao", type=str, required=True, help="O campo 'funcao' deve ser informado!")
        argumentos.add_argument("id", type = int, required = True, help= "O campo 'id' deve ser informado!")
        argumentos.add_argument("parametros", type = dict, required = True, help= "O campo 'parametros' deve ser informado!")
        args = argumentos.parse_args()
        chamar_funcao = "Nota_fiscal.{}(self,{},{})".format(args["funcao"],args['id'], args['parametros'])
        resultado  = eval(chamar_funcao)
        return resultado

    
    def retornar_tipos_notas_fiscais(self,id,args):

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
                    codtiponotafiscal,\
                    descricao \
                FROM\
                    fin_tiponotasfiscais "

        cursor.execute(comando)
        tipo_notas = cursor.fetchall()
        conexao.close()

        lista_tipo_notas = []

        for tipo_nota in tipo_notas:

            lista_tipo_notas.append({
                "cod_tipo_nota_fiscal":tipo_nota[0],
                "descricao":tipo_nota[1]
            })

        return {
            "status":"1",
            "msg":"consulta feita com sucesso",
            "lista_tipo_notas": lista_tipo_notas
        },200

    def retornar_grupo_de_impostos(self, id, args):

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

        comando = "SELECT * FROM fin_grupoimpostos"

        cursor.execute(comando)
        grupo_impostos = cursor.fetchall()

        lista_grupo_de_impostos = []
        for grupo_imposto in grupo_impostos:

            lista_grupo_de_impostos.append({
                "cod_grupo_impostos": grupo_imposto[0],
                "descricao":grupo_imposto[1]
            })

        return{
            "status":"1",
            "msg":"consulta feita com sucesso",
            "lista_grupos_de_impostos": lista_grupo_de_impostos
        },200

    def retornar_cfops(self, id, args):

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

        comando = "SELECT * FROM fin_cfops"

        cursor.execute(comando)
        cfops = cursor.fetchall()

        lista_cfops = []
        for cfop in cfops:

            lista_cfops.append({
                "cod_cfop": cfop[0],
                "numero": cfop[1],
                "descricao":cfop[2]
            })

        return{
            "status":"1",
            "msg":"consulta feita com sucesso",
            "lista_cfops": lista_cfops
        },200