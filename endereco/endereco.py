#importando bibliotecas
from logging import error
from flask_restful import Resource, reqparse
from flask import Flask
from flask_restful import Resource, Api
from flask_jwt_extended import create_access_token, jwt_required
import mysql.connector
import config


#endpoin de endereco
class Endereco (Resource):

    #requer estar logado, funcao que chama as demais funcoes
    @jwt_required()
    def post(self):
        argumentos = reqparse.RequestParser()
        argumentos.add_argument("funcao", type=str, required=True, help="O campo 'funcao' deve ser informado!")
        argumentos.add_argument("id", type = int, required = True, help= "O campo 'id' deve ser informado!")
        argumentos.add_argument("parametros", type = dict, required = True, help= "O campo 'parametros' deve ser informado!")
        args = argumentos.parse_args()
        chamar_funcao = "Endereco.{}(self,{},{})".format(args["funcao"],args['id'], args['parametros'])
        resultado  = eval(chamar_funcao)
        return resultado


    #funcao para retornar os predios cadastrados no sistema
    def retornar_predios(self, id, args):

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

        #comando para pegar os predios
        comando = "SELECT \
                    codpredio,\
                    sis_cidades_sis_estados_codestado,\
                    sis_cidades_codcidade,\
                    nome,\
                    bairro,\
                    rua,\
                    cep,\
                    complemento,\
                    caixapostal,\
                    obs,\
                    codresponsavel,\
                    localizacaoEnderecoAreaCobertura,\
                    tipoLogradouro,\
                    numeroEndereco \
                FROM\
                    cli_predios"

        try :
            cursor.execute(comando)
            predios = cursor.fetchall()
            conexao.close()
            #adicionando os predios em uma lista de predios como json
            lista_predios = []
            for predio in predios:
                lista_predios.append({
                    "cod_predio":predio[0],
                    "cod_estado":predio[1],
                    "cod_cidade":predio[2],
                    "nome":predio[3],
                    "bairro":predio[4],
                    "rua":predio[5],
                    "cep":predio[6],
                    "complemento":predio[7],
                    "caixa_postal":predio[8],
                    "obs":predio[9],
                    "cod_responsavel":predio[10],
                    "localizacaoEnderecoAreaCobertura":predio[11],
                    "tipoLogradouro":predio[12],
                    "numeroEndereco":predio[13],

                })
        
            return {
                "status":"1",
                "msg":"Consulta feita com sucesso",
                "lista_predios":lista_predios
            },200

        except mysql.connector.Error as error:

            conexao.close()


            return {
                "status":"2",
                "msg":"Problema ao pesquisar predio",
                "error": error
            },400


    #funcao para retornar as cidades cadastradas no sistema
    def retornar_cidades(self, id, args):

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


        #comando para pegas as cidades
        comando = "SELECT * FROM sis_cidades"
        cursor.execute(comando)
        cidades = cursor.fetchall()
        lista_cidades = []
        for cidade in cidades:

            lista_cidades.append({
                "cod_cidade":cidade[0],
                "cod_estado":cidade[1],
                "nome":cidade[2],
                "codigo_ibge":cidade[3],
                "abreviatua":cidade[4]
            })

        conexao.close()

        return {
            "status":1,
            "msg":"Consulta feita com sucesso",
            "lista_cidades": lista_cidades
        },200


    #funcao para retornar os estados cadastrados no sistema
    def retornar_estados(self, id, args):

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
        

        #comando para pegar os estados
        comando = "SELECT * FROM sis_estados"
        cursor.execute(comando)
        estados = cursor.fetchall()
        lista_estados = []
        for estado in estados:

            lista_estados.append({
                "cod_estado":estado[0],
                "nome":estado[1],
                "sigla":estado[2],
                "cod_pais":estado[3]
            })

        conexao.close()


        return {
            "status":1,
            "msg":"Consulta feita com sucesso",
            "lista_estados": lista_estados
        },200


    #funcao para retornar os paises cadastrados no sistema
    def retornar_paises(self, id, args):

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
        
        #comando para pegar os paises
        comando = "SELECT * FROM sis_paises"
        cursor.execute(comando)
        estados = cursor.fetchall()
        lista_estados = []
        for estado in estados:

            lista_estados.append({
                "cod_pais":estado[0],
                "nome":estado[1]
            })

        conexao.close()


        return {
            "status":1,
            "msg":"Consulta feita com sucesso",
            "lista_paises": lista_estados
        },200


    #funcao para adicionar endereco a um cliente
    def adicionar_endereco(self, id, args):

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
        

        #comando para inserir o endereco
        comando = "INSERT INTO cli_enderecos (\
                    cli_clientes_codcliente,\
                    sis_cidades_sis_estados_codestado,\
                    sis_cidades_codcidade,\
                    bairro,\
                    rua,\
                    cep,\
                    complemento,\
                    caixapostal,\
                    codpredio,\
                    codcep,\
                    obs,\
                    latitude,\
                    longitude,\
                    tipoendereco,\
                    numeroEndereco,\
                    numeroApto)\
                    VALUES('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(
                        args["cod_cliente"],
                        args["cod_estado"],
                        args["cod_cidade"],
                        args["bairro"],
                        args["rua"],
                        args["cep"],
                        args["complemento"],
                        args["caixa_postal"],
                        args["cod_predio"],
                        args["codcep"],
                        args["obs"],
                        args["latitude"],
                        args["longitude"],
                        args["tipoendereco"],
                        args["numeroEndereco"],
                        args["numeroApto"]
                    )

        try:
            
            cursor.execute(comando)
            conexao.commit()

            if cursor.rowcount == 1:
            
                id = cursor.lastrowid
                
                conexao.close()

                return{
                    "status":"1",
                    "msg":"endereco adicionado com sucesso",
                    "endereco":id
                },201

        except mysql.connector.Error as error:

            conexao.close()

            return{
                "status":"2",
                "msg":"Problema ao tentar inserir endereco",
                "erro": error
            },400

    def retornar_endereco_cliente (self, id, args):

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
                    codendereco,\
                    sis_cidades_codcidade,\
                    bairro,\
                    rua,\
                    cep,\
                    complemento,\
                    caixapostal,\
                    codpredio,\
                    ssid,\
                    codcep,\
                    obs,\
                    removido,\
                    tipoendereco,\
                    latitude,\
                    longitude,\
                    localizacaoEnderecoAreaCobertura,\
                    tipoLogradouro,\
                    numeroEndereco,\
                    tipoImovel,\
                    numeroApto\
                FROM\
                    cli_enderecos \
                WHERE cli_clientes_codcliente = {}".format(args['cod_cliente'])

        cursor.execute(comando)
        enderecos = cursor.fetchall()
        conexao.close()
        lista_enderecos = []
        for endereco in enderecos:

            lista_enderecos.append({
                "cod_endereco" : endereco[0],
                "sis_cidades_codcidade": endereco[1],
                "bairro": endereco[2],
                "rua": endereco[3],
                "cep": endereco[4],
                "complemento": endereco[5],
                "caixa_postal":endereco[6],
                "obs": endereco[7],
                "removido": endereco[8],
                "tipo_endereo": endereco[9],
                "latitude":endereco[10],
                "longitude" : endereco[11],
                "localizacaoEnderecoAreaCobertura" : endereco[12],
                "tipoLogradouro" : endereco[13],
                "numeroEndereco" : endereco[14],
                "tipoImovel" : endereco[15],
                "numeroApto" : endereco[16]
            })
        
        return {
            "status":"1",
            "msg":"consulta feita com sucesso",
            "lista_enderecos": lista_enderecos
        },200
