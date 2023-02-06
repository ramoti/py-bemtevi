# coding:utf-8

#importando bibliotecas
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, jwt_required
import mysql.connector
import config

#Endpoint de login
class Login(Resource):

    #Funcao chamada que chama as demais funcoes
    def post(self):
        argumentos = reqparse.RequestParser()
        argumentos.add_argument("funcao", type=str, required=True, help="O campo 'funcao' deve ser informado!")
        argumentos.add_argument("login", type = dict, required = True, help= "O campo 'login' deve ser informado!")
        argumentos.add_argument("parametros", type = dict, required = True, help= "O campo 'parametros' deve ser informado!")
        args = argumentos.parse_args()
        chamar_funcao = "Login."+ "{}(self,{},{})".format(args['funcao'], args['login'], args['parametros'])
        resultado  = eval(chamar_funcao)
        return resultado


    #funcao para fazer login nas apis
    def logar(self,login,  parametros):
        

        #conexao com o banco de dados
        conexao = mysql.connector.connect(

                host = config.conexao["host"],
                user= config.conexao["user"],
                password= config.conexao["password"],
                database= config.conexao["db"]
        )


        #verifica se o usuario e senha informados estao certos com o id passado
        cursor = conexao.cursor(buffered=True)
        comando = "SELECT * FROM sis_conexoes_api WHERE user = '{}' and senha = '{}' and id = {}".format(login['user'],login['senha'],login['id'])
        cursor.execute(comando)
        r = cursor.fetchone()

        conexao.close()
        

        #caso nao encontre as credenciais
        if r is None:
            return {"message":'usuario, senha ou id incorretos'},401


        #retorna token de acesso
        else:
            token_acesso = create_access_token(identity = r)
            return {"access_token":token_acesso}, 200

    def get(self):
        return "nnn"