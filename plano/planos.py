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
class Planos (Resource):

    #requer estar logado, funcao que chama as demais funcoes
    @jwt_required()
    def post(self):
        argumentos = reqparse.RequestParser()
        argumentos.add_argument("funcao", type=str, required=True, help="O campo 'funcao' deve ser informado!")
        argumentos.add_argument("id", type = int, required = True, help= "O campo 'id' deve ser informado!")
        argumentos.add_argument("parametros", type = dict, required = True, help= "O campo 'parametros' deve ser informado!")
        args = argumentos.parse_args()
        chamar_funcao = "Planos.{}(self,{},{})".format(args["funcao"],args['id'], args['parametros'])
        resultado  = eval(chamar_funcao)
        return resultado

    def retornar_plano(self, id, args):

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
                    nome,\
                    periodo,\
                    descricao,\
                    datacriacao,\
                    periodoexpiracao,\
                    planoposexpiracao,\
                    precoforcado,\
                    codgrupoplano,\
                    diabilhetageminicial,\
                    diabilhetagemfinal,\
                    cobrarprorataadicionaldiaativacaomaiorigualque,\
                    cobrarprorataadicionaldiaativacaomenorigualque,\
                    nrdiasadicionarcalculobilhetagem,\
                    nrdiasgratis,\
                    aparecernf,\
                    adicional,\
                    STATUS,\
                    prepago,\
                    emailespacodiscototal,\
                    obs,\
                    parametrosadicionaisprovedor,\
                    VOIP,\
                    codServicoPrefeitura,\
                    codAtividade,\
                    VOIP_quandoCobrarCDR,\
                    disponivelParaTipoPessoa,\
                    necessitaAprovacao,\
                    podeAlterarValorPlano,\
                    percentualAproximadoTributos,\
                    anatel_descricaoSEAC,\
                    anatel_valorSEAC,\
                    anatel_codPlanoPaiSEAC,\
                    anatel_descricaoSTFC,\
                    anatel_valorSTFC,\
                    anatel_codPlanoPaiSTFC,\
                    anatel_desccricaoSCM,\
                    anatel_valorSCM,\
                    anatel_codPlanoPaiSCM,\
                    anatel_descricaoSVA,\
                    anatel_valorSVA,\
                    anatel_codPlanoPaiSVA,\
                    codTipoTecnologia,\
                    codPlanoClassificacaoItemFiscal,\
                    SEFAZ_codigoTipoUtilizacao,\
                    SEFAZ_codigoClassificacaoItemDocumentoFiscal,\
                    HDK_CodServicoEntregavel,\
                    formaPagamento,\
                    sippulse_profiles,\
                    sippulse_planostarifa,\
                    DFE_tributacaoMunicipio,\
                    anatel_descricaoOTT,\
                    anatel_valorOTT,\
                    anatel_codPlanoPaiOTT,\
                    CodigoPlanoConta,\
                    pon,\
                    slot,\
                    SERIAL,\
                    oNum \
                FROM\
                    plan_planos \
                WHERE codplano = {};".format(args["cod_plano"])
        cursor.execute(comando)
        plano = cursor.fetchone()

        if plano is None :
            conexao.close()
            return {
                "status":"2",
                "msg":"cod_plano nao encontrado",
                "error":"por favor informe um codigo de plano existente"
            },404

        conexao.close()
        return {
            "status":"1",
            "msg":"Consulta feita com sucesso",
            "plano": {
                "nome": plano[0],
                "periodo": plano[1],
                "descricao": plano[2],
                "data_criacao": str(plano[3]),
                "periodo_expiracao": plano[4],
                "plano_pos_expiracao": plano[5],
                "preco_forcado": plano[6],
                "cod_grupo_plano": plano[7],
                "dia_bilhetagem_inicial": plano[8],
                "dia_bilhetagem_final": plano[9],
                "cobrar_prorata_adicional_dia_ativacao_maior_igual_que": plano[10],
                "cobrar_prorata_adicionaldia_ativacao_menor_igual_que": plano[11],
                "nr_dias_adicionar_calculo_bilhetagem": plano[12],
                "nr_dias_gratis": plano[13],
                "aparecer_nf": plano[14],
                "adicional": plano[15],
                "STATUS": plano[16],
                "prepago": plano[17],
                "email_espacodis_cototal": plano[18],
                "obs": plano[19],
                "parametros_adicionais_provedor": plano[20],
                "VOIP": plano[21],
                "cod_servico_Prefeitura": plano[22],
                "cod_atividade": plano[23],
                "VOIP_quando_cobrar_CDR": plano[24],
                "disponivel_para_tipo_pessoa": plano[25],
                "necessita_aprovacao": plano[26],
                "pode_alterar_valor_plano": plano[27],
                "percentual_aproximado_tributos": plano[28],
                "anatel_descricao_SEAC": plano[29],
                "anatel_valor_SEAC": plano[30],
                "anatel_cod_plano_pai_SEAC": plano[31],
                "anatel_descricao_STFC": plano[32],
                "anatel_valor_STFC": plano[33],
                "anatel_cod_plano_pai_STFC": plano[34],
                "anatel_desccricao_SCM": plano[35],
                "anatel_valor_SCM": plano[36],
                "anatel_cod_plano_pai_SCM": plano[37],
                "anatel_descricao_SVA": plano[38],
                "anatel_valor_SVA": plano[39],
                "anatel_cod_plano_pai_SVA": plano[40],
                "cod_tipo_tecnologia": plano[41],
                "cod_plano_classificacao_item_fiscal": plano[42],
                "SEFAZ_codigo_tipo_utilizacao": plano[43],
                "SEFAZ_codigo_classificacao_item_documento_fiscal": plano[44],
                "HDK_Cod_servico_entregavel": plano[45],
                "forma_pagamento": plano[46],
                "sippulse_profiles": plano[47],
                "sippulse_planos_tarifa": plano[48],
                "DFE_tributacao_municipio": plano[49],
                "anatel_descricao_OTT": plano[50],
                "anatel_valor_OTT": plano[51],
                "anatel_cod_plano_pai_OTT": plano[52],
                "Codigo_plano_conta": plano[53],
                "pon": plano[54],
                "slot": plano[55],
                "SERIAL": plano[56],
                "oNum": plano[57] 
            }
        },200


    def retornar_plano_completo (self, id, args):

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

        comando = ""

        cursor.execute(comando)
        plano = cursor.fetchone()

        return{
            "status":"1",
            "msg":"consulta feita com sucesso",
            "plano":{
                
            }
        }