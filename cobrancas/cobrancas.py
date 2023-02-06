#importando bibliotecas
from logging import error
from flask_restful import Resource, reqparse
from flask import Flask
from flask_restful import Resource, Api
from flask_jwt_extended import create_access_token, jwt_required
import mysql.connector
import config
import os
import requests
import json
from datetime import datetime, date

#endpoin de endereco
class Cobranca (Resource):

    #requer estar logado, funcao que chama as demais funcoes
    @jwt_required()
    def post(self):
        argumentos = reqparse.RequestParser()
        argumentos.add_argument("funcao", type=str, required=True, help="O campo 'funcao' deve ser informado!")
        argumentos.add_argument("id", type = int, required = True, help= "O campo 'id' deve ser informado!")
        argumentos.add_argument("parametros", type = dict, required = True, help= "O campo 'parametros' deve ser informado!")
        args = argumentos.parse_args()
        chamar_funcao = "Cobranca.{}(self,{},{})".format(args["funcao"],args['id'], args['parametros'])
        resultado  = eval(chamar_funcao)
        return resultado

    #funcao para retornar os tipos de cobrancas
    def retornar_tipos_de_cobranca(self, id, args):

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
                    codtiposcobranca,\
                    fin_contascorrentes_codcontacorrente,\
                    fin_gruposcobranca_codgrupocobranca,\
                    descricao,\
                    diacobranca,\
                    formapagamento,\
                    diabilhetageminicial,\
                    diabilhetagemfinal,\
                    gruponsa,\
                    tipopessoa,\
                    tipobilhetagem,\
                    numerocobrancaspagina,\
                    STATUS,\
                    VOIP_CDR_DiaBilhetagemInicial,\
                    VOIP_CDR_DiaBilhetagemFinal,\
                    VOIP_CDR_TipoBilhetagem,\
                    cobrancaRegistrada,\
                    diasCobranca,\
                (SELECT \
                    b.descricao \
                FROM\
                    fin_gruposcobranca b \
                WHERE b.codgrupocobranca = fin_gruposcobranca_codgrupocobranca) descricaoGrupo,\
                    permiteNovosCadastros \
                FROM\
                    fin_tiposcobranca "

        cursor.execute(comando)
        tipos_de_cobranca = cursor.fetchall()
        conexao.close()

        lista_tipos =[]
        for tipo in tipos_de_cobranca:
            
            lista_tipos.append({
                "cod_tipo_cobranca":tipo[0],
                "cod_conta_corrente":tipo[1],
                "cod_grupo_cobranca":tipo[2],
                "descricao":tipo[3],
                "dia_cobranca":tipo[4],
                "forma_pagamento":tipo[5],
                "dia_bilhetagem_inicial":tipo[6],
                "dia_bilhetagem_final":tipo[7],
                "gruposa":tipo[8],
                "tipo_pessoa":tipo[9],
                "tipo_bilhetagem":tipo[10],
                "numero_cobrancas_pagina":tipo[11],
                "status":tipo[12],
                "voip_cdr_dia_bilhetagem_inicial":tipo[13],
                "voip_cdr_dia_bilhetagem_final":tipo[14],
                "voip_cdr_tipo_bilhetagem":tipo[15],
                "cobranca_registrada":tipo[16],
                "dias_cobranca":tipo[17],
                "descricao_grupo_cobranca":tipo[18]

            })

        return {
            "status":"1",
            "msg":"consulta feita com sucesso",
            "lista_tipos_cobranca":lista_tipos
        },200

    def retornar_cobrancas_cliente(self, id, args):

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

        comando = "SELECT nome FROM cli_clientes WHERE codcliente = {} AND situacao != 1".format(args['cod_cliente'])
        cursor.execute(comando)
        nome = cursor.fetchone()

        if nome:
            nome = nome[0]
        else:
            return{
                "status":"2",
                "msg":"cod cliente nao encontrado",
                "error": "não foi possível encontrar o codigo do cliente {} ou o cliente está arquivado".format(args['cod_cliente'])
            },400

        lista_cobrancas = []

        comando = "SELECT \
                        a.codcobranca,\
                        a.valorcobranca,\
                        a.datavencimento,\
                        b.rua,\
                        b.bairro,\
                        b.complemento,\
                        c.nome AS Cidade,\
                        d.nome AS estado,\
                        f.descricao,\
                        f.formapagamento,\
                        b.cep,\
                        (SELECT f.email FROM cli_emails f WHERE f.cli_clientes_codcliente = a.codcliente LIMIT 1) AS EMAIL,\
                        (SELECT g.numero FROM cli_fones g WHERE g.cli_enderecos_cli_clientes_codcliente = b.cli_clientes_codcliente LIMIT 1) AS FONE\
                        FROM\
                        cob_cobrancas a,\
                        cli_enderecos b,\
                        sis_cidades c,\
                        sis_estados d,\
                        fin_cobrancascliente e,\
                        fin_tiposcobranca f,\
                        cob_cobrancasgeradas g\
                        WHERE a.codcobranca NOT IN \
                        (SELECT \
                            codcobranca \
                        FROM\
                            cob_pagamentos) \
                        AND a.codcliente = {} \
                        AND a.situacao = 0 \
                        AND a.codcliente = b.cli_clientes_codcliente \
                        AND c.codcidade = b.sis_cidades_codcidade \
                        AND d.codestado = b.sis_cidades_sis_estados_codestado \
                        AND a.codcobrancacliente = e.codcobrancascliente \
                        AND b.codendereco = e.cli_enderecos_codendereco \
                        AND e.fin_tiposcobranca_codtiposcobranca = f.codtiposcobranca\
                        AND a.cob_cobrancasgeradas_codcobrancagerada = g.codcobrancagerada\
                        AND a.codcobranca NOT IN (SELECT cob_cobrancas_codcobranca from cob_pagamentosparciais)".format(args['cod_cliente'])
        cursor.execute(comando)
        cobrancas = cursor.fetchall()
        conexao.close()

        for cobranca in cobrancas:
            caminho = "url nao encontrada"
            if cobranca[9] != 6:
                response = requests.get(banco[7] + "/bemtevi/admin/cobrancas/bolpdf/search.php?search={}".format(cobranca[0]))
                response_json = response.json()
                if len(response_json) <= 0 :
                    caminho = "nao encontrado"
                else:
                    caminho = banco[7] + "/bemtevi/admin/cobrancas/bolpdf/" + response_json[0]


                
            else :
                comando = "SELECT pagseguro_url from cob_cobrancas_informacoesadicionais where codcobranca = {}".format(cobranca[0])
                cursor.execute(comando)
                resultado = cursor.fetchone()
                if resultado is None:
                    caminho = 'url nao encontrada'
                else :
                    caminho = resultado[0]
                

            
            lista_cobrancas.append({
            'cod_cobranca':cobranca[0],
            'valor_cobranca':float('{0:.2f}'.format(cobranca[1])),
            'data_vencimento':str(cobranca[2]),
            'cedente': cobranca[8],
            "sacado" : nome,
            "cep": cobranca[10],
            "logradouro" :cobranca[3],
            "bairro" : cobranca[4],
            "cidade" : cobranca[6],
            "estado" : cobranca[7],
            "complemento": cobranca[5],
            "email":cobranca[11],
            "telefone":cobranca[12],
            "url": caminho
            })

        return {
            "status":"1",
            "msg":"consulta feita com sucesso",
            'boletos':lista_cobrancas
        } ,200



    def adicionar_cobranca(self, id, args):

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
        cursor = conexao.cursor(buffered = True)

        if args["dia_cobranca"] > 31:
            conexao.close()

            return{
                "status":"2",
                "msg":"Problema ao criar cobrança",
                "error":"a data da cobrança não pode ser mais que 31"
            },400

        comando = "SELECT \
                    * \
                FROM\
                  fin_cobrancascliente a \
                WHERE a.cli_clientes_codcliente = {} \
                    AND a.fin_tiposcobranca_codtiposcobranca = {} \
                    AND a.diacobranca = {} ;".format(args['cod_cliente'], args['cod_tipo_cobranca'], args["dia_cobranca"])

        cursor.execute(comando)
        cobranca_existe = cursor.fetchone()
        if cobranca_existe is not None:
            comando = "SELECT \
                        valor \
                    FROM\
                        sis_configuracoes a \
                    WHERE a.`chave` LIKE '%permitirCadastrarCobrancasNoMesmoDiaVencimento%'"
            cursor.execute(comando)
            configuracao = cursor.fetchone()
            if configuracao[0] == "0":
                conexao.close()
                
                return {
                    "status":"2",
                    "msg":"problema ao tentar inserir cobranca",
                    "error":"este cliente ja possui uma cobranca com este tipo nesta data"
                },400
            
        comando = "SELECT \
                    * \
                FROM\
                    cli_enderecos a \
                WHERE a.`codendereco` = {} ;".format(args['cod_endereco_cliente'])

        cursor.execute(comando)
        endereco = cursor.fetchone()

        if endereco is  None:
            conexao.close()

            return{
                "status":"2",
                "msg":"problema ao tentar inserir cobranca",
                "error":"o endereco nao existe/nao foi encontrado"
            },404

        comando = "SELECT \
                    * \
                FROM\
                    cli_enderecos a \
                WHERE a.`codendereco` = {} ;".format(args['cod_endereco_nf'])

        cursor.execute(comando)
        endereco_nf = cursor.fetchone()

        if endereco_nf is  None:
            conexao.close()

            return{
                "status":"2",
                "msg":"problema ao tentar inserir cobranca",
                "error":"o endereco da nota fiscal nao existe/nao foi encontrado"
            },404

        comando = "SELECT \
                    * \
                FROM\
                    fin_contascorrentes a \
                WHERE a.`codcontacorrente` = {} ;".format(args['cod_conta_corrente'])

        cursor.execute(comando)
        conta_corrente = cursor.fetchone()

        if conta_corrente is  None:
            conexao.close()

            return{
                "status":"2",
                "msg":"problema ao tentar inserir cobranca",
                "error":"A conta corrente nao existe/ foi encontrada"
            },404

        comando = "SELECT \
                    * \
                FROM\
                    fin_tiponotasfiscais a \
                WHERE a.codtiponotafiscal = {};".format(args['cod_tipo_nota_fiscal'])

        cursor.execute(comando)
        tipo_nota_fiscal = cursor.fetchone()

        if tipo_nota_fiscal is None:
            conexao.close()

            return {
                "status":"2",
                "msg":"tipo de nota fiscal nao encontrada",
                "error":"nota fiscal nao encontrada para o codigo passado"
            },404


        comando = "SELECT \
                    * \
                FROM\
                    fin_grupoimpostos a \
                WHERE a.codgrupoimposto = {} ;".format(args['cod_grupo_impostos'])

        cursor.execute(comando)
        grupo_impostos = cursor.fetchone()

        if grupo_impostos is None:
            conexao.close()

            return {
                "status":"2",
                "msg":"grupo de impostos nao encontrado",
                "error":"o codigo de imposto nao foi encontrado"
            },404

        

        comando = "INSERT INTO fin_cobrancascliente (\
                    cli_clientes_codcliente,\
                    fin_tiposcobranca_codtiposcobranca,\
                    cli_enderecos_cli_clientes_codcliente,\
                    cli_enderecos_codendereco,\
                    codendereco_nf,\
                    diacobranca,\
                    descricao,\
                    codcontacorrente,\
                    codcartaocredito,\
                    codtiponotafiscal,\
                    impostos,\
                    codgrupoimposto,\
                    nrdiastolerancia,\
                    cfop,\
                    nfobsimpressao,\
                    enviaravisogeracaocobranca,\
                    comportamentosespeciais,\
                    emailnfe,\
                    codenderecodestinatario_nf,\
                    tipoBilhetagem,\
                    diaBilhetagemInicial,\
                    diaBilhetagemFinal,\
                    codIntegracaoOmie\
                    ) \
                VALUES\
                    (\
                        {},\
                        {},\
                        {},\
                        {},\
                        {},\
                        '{}',\
                        '{}',\
                        {},\
                        {},\
                        {},\
                        {},\
                        {},\
                        '{}',\
                        '{}',\
                        '{}',\
                        {},\
                        '{}',\
                        '{}',\
                        {},\
                        {},\
                        {},\
                        {},\
                        {}\
                    )".format(
                        args["cod_cliente"],
                        args["cod_tipo_cobranca"],
                        args["cod_cliente"],
                        args["cod_endereco_cliente"],
                        args["cod_endereco_nf"],
                        args["dia_cobranca"],
                        args["descricao"],
                        args["cod_conta_corrente"],
                        '0',
                        args["cod_tipo_nota_fiscal"],
                        '0',
                        args["cod_grupo_impostos"],
                        args["nr_dias_tolerancia"],
                        args["cod_cfop"],
                        args["nf_obs_impressao"],
                        args["enviar_aviso_geracao"],
                        '0',
                        args["email_nfe"],
                        '0',
                        args["tipo_bilhetagem"],
                        args["dia_bilhetagem_inicial"],
                        args["dia_bilhetagem_final"],
                        args["cod_integracao_omie"]
                    )

        cursor.execute(comando)

        conexao.commit()
        if cursor.rowcount == 1:
            conexao.close()

            id = cursor.lastrowid

            return {
                "status":"1",
                "msg":"cobranca adicionada com sucesso",
                "id":id
            },201

    def inserir_cobranca_cliente_plano (self, id, args):

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
        periodocliente = args["periodo_cliente"]
        if args["periodo_cliente"] == "":

            periodocliente = 0

        comando = "INSERT INTO fin_cobrancasclienteplanos (\
                    plan_planos_codplano,\
                    fin_cobrancascliente_codcobrancascliente,\
                    codcobrancasclienteplanos,\
                    precocliente,\
                    cortesia,\
                    datacadastro,\
                    dataativacao,\
                    datadesativacao,\
                    codrevenda,\
                    diabilhetageminicial,\
                    diabilhetagemfinal,\
                    quantidade,\
                    obs,\
                    mescobranca,\
                    anocobranca,\
                    periodocliente,\
                    codigosagentesdominioemail,\
                    descricaoboleto,\
                    descricaonotafiscal,\
                    codplanoanterior,\
                    codendereco,\
                    complementoBoleto,\
                    complementoNotaFiscal,\
                    codVendedor,\
                    NumCircuito,\
                    Porta,\
                    NumCrossConnect,\
                    IP,\
                    Hostname,\
                    ssid,\
                    ssid5,\
                    senha,\
                    senha5\
                ) \
                VALUES\
                    (\
                    {}, \
                    {},\
                    {},\
                    '{}',\
                    {},\
                    '{}',\
                    '{}',\
                    '{}',\
                    {},\
                    {},\
                    {},\
                    '{}',\
                    '{}',\
                    {},\
                    '{}',\
                    '{}',\
                    '{}',\
                    '{}',\
                    '{}',\
                    {},\
                    '{}',\
                    '{}',\
                    '{}',\
                    '{}',\
                    '{}',\
                    '{}',\
                    '{}',\
                    '{}',\
                    '{}',\
                    '{}',\
                    '{}',\
                    '{}',\
                    '{}'\
                )".format(
                    args["cod_plano"],
                    args["cod_cobranca_cliente"],
                    args["cod_cobranca_cliente_plano"],
                    args["preco_cliente"],
                    args["cortesia"],
                    args["data_cadastro"],
                    args["data_ativacao"],
                    args["data_desativacao"],
                    args["cod_revenda"],
                    args["dia_bilhetagem_inicial"],
                    args["dia_bilhetagem_final"], 
                    args["quantidade"], 
                    args["obs"], 
                    args["mescobranca"], 
                    args["anocobranca"], 
                    periodocliente, 
                    args["codigos_agentes_dominio_email"], 
                    args["descricao_boleto"], 
                    args["descricao_nota_fiscal"], 
                    args["cod_plano_anterior"], 
                    args["cod_endereco"],
                    args["complemento_boleto"],
                    args["complemento_nota_fiscal"],
                    args["cod_vendedor"],
                    args["num_circuito"],
                    args["porta"],
                    args["num_cross_connect"],
                    args["IP"],
                    args["Hostname"],
                    args["ssid"],
                    args["ssid"],
                    args["senha"],
                    args["senha"]

                )
        try :

            cursor.execute(comando)

            conexao.commit()
            if cursor.rowcount == 1: 

                id = cursor.lastrowid


                conexao.close()
                return {
                    "status":"1",
                    "msg":"Criação feita com sucesso",
                    "id":id
                },201

        except mysql.connector.Error as error:
            conexao.close()

            return {
                "status":"2",
                "msg":"problema ao tentar incluir cliente no banco",
                "error": error
            },400


    def retornar_cliente_cobranca_planos(self, id, args):

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
                    codcobrancasclienteplanos,\
                    fin_cobrancascliente_codcobrancascliente,\
                    plan_planos_codplano,\
                    precocliente,\
                    cortesia,\
                    datacadastro,\
                    dataativacao,\
                    datadesativacao,\
                    codrevenda,\
                    diabilhetageminicial,\
                    diabilhetagemfinal,\
                    quantidade,\
                    obs,\
                    mescobranca,\
                    anocobranca,\
                    periodocliente,\
                    codigosagentesdominioemail,\
                    descricaoboleto,\
                    descricaonotafiscal,\
                    codendereco,\
                    codDesignador,\
                    PK_codCobrancaClientePlano,\
                    complementoBoleto,\
                    complementoNotaFiscal,\
                    codVendedor,\
                    codPrimeiraCobranca,\
                    bloqueioTemporarioDesdeDe,\
                    ultimoDesbloqueioTemporarioFoiEm,\
                    bloqueiosTemporarios_logs,\
                    NumCircuito,\
                    Porta,\
                    NumCrossConnect,\
                    IP,\
                    Hostname,\
                    ssid,\
                    ssid5,\
                    senha,\
                    senha5\
                FROM\
                    fin_cobrancasclienteplanos \
                WHERE fin_cobrancascliente_codcobrancascliente = {}\
                    AND plan_planos_codplano = {}\
                    AND codcobrancasclienteplanos = {}".format(args["cod_cobranca_cliente"],args["cod_plano"],args["cod_cliente_planos"])

        cursor.execute(comando)
        cliente_cobranca_plano = cursor.fetchone()

        if cliente_cobranca_plano is  None:

            return {
                "status":"2",
                "msg":"Não foi possivel encontrar resultados",
                "error":"Nao foi encontrado nenhum plano na cobranca do cliente com os dados informados"
            },404

        return {
            "status":"1",
            "msg":"consulta feita com sucesso",
            "cliente_cobranca_plano":{
                "codcobrancasclienteplanos":cliente_cobranca_plano[0],
                "fin_cobrancascliente_codcobrancascliente":cliente_cobranca_plano[1],
                "plan_planos_codplano":cliente_cobranca_plano[2],
                "precocliente":cliente_cobranca_plano[3],
                "cortesia":cliente_cobranca_plano[4],
                "datacadastro":str(cliente_cobranca_plano[5]),
                "dataativacao":str(cliente_cobranca_plano[6]),
                "datadesativacao":str(cliente_cobranca_plano[7]),
                "codrevenda":cliente_cobranca_plano[8],
                "diabilhetageminicial":cliente_cobranca_plano[9],
                "diabilhetagemfinal":cliente_cobranca_plano[10],
                "quantidade":cliente_cobranca_plano[11],
                "obs":cliente_cobranca_plano[12],
                "mescobranca":cliente_cobranca_plano[13],
                "anocobranca":cliente_cobranca_plano[14],
                "periodocliente":cliente_cobranca_plano[15],
                "codigosagentesdominioemail":cliente_cobranca_plano[16],
                "descricaoboleto":cliente_cobranca_plano[17],
                "descricaonotafiscal":cliente_cobranca_plano[18],
                "codendereco":cliente_cobranca_plano[19],
                "codDesignador":cliente_cobranca_plano[20],
                "PK_codCobrancaClientePlano":cliente_cobranca_plano[21],
                "complementoBoleto":cliente_cobranca_plano[22],
                "complementoNotaFiscal":cliente_cobranca_plano[23],
                "codVendedor":cliente_cobranca_plano[24],
                "codPrimeiraCobranca":cliente_cobranca_plano[25],
                "bloqueioTemporarioDesdeDe":str(cliente_cobranca_plano[26]),
                "ultimoDesbloqueioTemporarioFoiEm":cliente_cobranca_plano[27],
                "bloqueiosTemporarios_logs":cliente_cobranca_plano[28],
                "NumCircuito":cliente_cobranca_plano[29],
                "Porta":cliente_cobranca_plano[30],
                "NumCrossConnect":cliente_cobranca_plano[31],
                "IP":cliente_cobranca_plano[32],
                "Hostname":cliente_cobranca_plano[33],
                "ssid":cliente_cobranca_plano[34],
                "ssid5":cliente_cobranca_plano[35],
                "senha":cliente_cobranca_plano[36],
                "senha5":cliente_cobranca_plano[37]
            }
        },200

    def gerar_2_via(self, id, args):

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
        comando = "SELECT usuario, senha FROM sis_usuarios WHERE situacao = 0 LIMIT 1 ;"
        cursor.execute(comando)
        credencial = cursor.fetchone()
        cod_cobranca = args["cod_cobranca"]
        nova_data_vencimento = args["nova_data_vencimento"]
        comando = f"SELECT \
                    codcliente \
                FROM\
                    cob_cobrancas \
                WHERE codcobranca = {cod_cobranca};"
        cursor.execute(comando)
        cod_cliente = cursor.fetchone()

        if cod_cliente is None:
            return {
                "status":"2",
                "msg":"problema na busca",
                "error":"cobranca nao existe"
            },404

        payload = json.dumps({
            "codCobranca":cod_cobranca,
            "dataVencimento":nova_data_vencimento,
            "login":credencial[0],
            "senha":credencial[1],
            "codCliente":cod_cliente[0],
            "calcularJuros":"1"
        })
        response = requests.post(url = banco[7] + "/bemtevi/cadastros/gerar_2a_api.php", data= payload)
        response_json = response.json()

        link_boleto = response_json["link_boleto"]
        link_boleto = link_boleto.replace("..","")
        link_boleto = banco[7] + "/bemtevi" + link_boleto
        return{
            "status":"1",
            "msg":"geracao feita com sucesso",
            "caminho_pdf":link_boleto,
            "cobranca":response_json["dadosCobranca"]
        }
        

    def alterar_ssid_senha (self, id, args):

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

        comando = "UPDATE \
                    fin_cobrancasclienteplanos a \
                SET\
                    a.ssid5 = '{}',\
                    a.ssid = '{}',\
                    a.senha = '{}',\
                    a.senha5 = '{}' \
                WHERE a.PK_codCobrancaClientePlano = '{}';".format(args["ssid"],args["ssid"],args["senha"],args["senha5"], args["pk_cod_cobranca_cliente_plano"])
        try:
            cursor.execute(comando)
            conexao.commit()
            conexao.close()


            return{
                "status":"1",
                "msg":"alteracao feita com sucesso"
            }

        except mysql.connector.Error as error:
            conexao.close()
            return{
                "status":"2",
                "msg":"problema na alteracao",
                "error":error
            }

    def retornar_cobrancas_vencidas_nao_pagas_cliente(self, id, args):

        #Para essa funcao funcionar, precisa do php para procurar o arquivo (search.php)

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

        data_atual = date.today()
        data_string = datetime.strftime(data_atual , '%Y-%m-%d')
        cliente = args['cod_cliente']
        if cliente:
            comando = "SELECT \
                        a.codcobranca,\
                        a.valorcobranca,\
                        a.datavencimento,\
                        b.rua,\
                        b.bairro,\
                        b.complemento,\
                        c.nome AS Cidade,\
                        d.nome AS estado,\
                        f.descricao,\
                        f.formapagamento,\
                        b.cep,\
                        (SELECT f.email FROM cli_emails f WHERE f.cli_clientes_codcliente = a.codcliente LIMIT 1) AS EMAIL,\
                        (SELECT g.numero FROM cli_fones g WHERE g.cli_enderecos_cli_clientes_codcliente = b.cli_clientes_codcliente LIMIT 1) AS FONE\
                        FROM\
                        cob_cobrancas a,\
                        cli_enderecos b,\
                        sis_cidades c,\
                        sis_estados d,\
                        fin_cobrancascliente e,\
                        fin_tiposcobranca f,\
                        cob_cobrancasgeradas g\
                        WHERE a.codcobranca NOT IN \
                        (SELECT \
                            codcobranca \
                        FROM\
                            cob_pagamentos) \
                        AND a.codcliente = {} \
                        AND a.situacao = 0 \
                        AND a.codcliente = b.cli_clientes_codcliente \
                        AND a.datavencimento < '{}' \
                        AND c.codcidade = b.sis_cidades_codcidade \
                        AND d.codestado = b.sis_cidades_sis_estados_codestado \
                        AND a.codcobrancacliente = e.codcobrancascliente \
                        AND b.codendereco = e.cli_enderecos_codendereco \
                        AND e.fin_tiposcobranca_codtiposcobranca = f.codtiposcobranca\
                        AND a.cob_cobrancasgeradas_codcobrancagerada = g.codcobrancagerada\
                        AND a.codcobranca NOT IN (SELECT cob_cobrancas_codcobranca from cob_pagamentosparciais)".format(cliente,data_string)
            cursor.execute(comando)
            cobrancas = cursor.fetchall()
            boletos_vencidos = []
            count = 0
            for cobranca in cobrancas:

                adicionar_boletos = True
                data_vencimento = cobranca[2]
                data_vencimento_formatada = data_vencimento.strftime('%d/%m/%Y')
                indice_da_semana_vencimento = data_vencimento.weekday()
                diferenca_datas = data_atual - data_vencimento

                if indice_da_semana_vencimento == 5:
                    if diferenca_datas.days <= 2:
                        adicionar_boletos = False

                if indice_da_semana_vencimento == 6:
                    if diferenca_datas.days <= 1:
                        adicionar_boletos = False

                response_feriados = requests.get(url="https://api.calendario.com.br/?json=true&ano={}&token=Z2FicmllbC5rc3lzQGdtYWlsLmNvbSZoYXNoPTg1OTI5NzQ3".format(data_atual.year))
                for i in response_feriados.json():
                    if i['date'] == str(data_vencimento_formatada):
                        indice_feriado = datetime.strptime (i['date'], '%d/%m/%Y').date()
                        indice_feriado = indice_feriado.weekday()
                        if indice_feriado == 4:
                            if diferenca_datas.days <= 3:
                                adicionar_boletos = False
                                
                        if (indice_feriado != 4 and indice_feriado != 5 and indice_feriado != 6) :
                            if diferenca_datas.days == 1:
                                adicionar_boletos = False

                if adicionar_boletos == True:    
                    caminho = "url nao encontrada"
                    if cobranca[9] != 6:
                        response = requests.get(banco[7] + "/bemtevi/admin/cobrancas/bolpdf/search.php?search={}".format(cobranca[0]))
                        response_json = response.json()
                        if len(response_json) <= 0 :
                            caminho = "nao encontrado"
                        else:
                            caminho = banco[7] + "/bemtevi/admin/cobrancas/bolpdf/" + response_json[0]

                    else :
                        comando = "SELECT pagseguro_url from cob_cobrancas_informacoesadicionais where codcobranca = {}".format(cobranca[0])
                        cursor.execute(comando)
                        resultado = cursor.fetchone()
                        if resultado is None:
                            caminho = 'url nao encontrada'
                        else :
                            caminho = resultado[0]
                        
                    boletos_vencidos.append({
                    'cod_cobranca':cobranca[0],
                    'valor_cobranca':float('{0:.2f}'.format(cobranca[1])),
                    'data_vencimento':str(cobranca[2]),
                    'cedente': cobranca[8],
                    "cep": cobranca[10],
                    "logradouro" :cobranca[3],
                    "bairro" : cobranca[4],
                    "cidade" : cobranca[6],
                    "estado" : cobranca[7],
                    "complemento": cobranca[5],
                    "email":cobranca[11],
                    "telefone":cobranca[12],
                    "url": caminho
                    })
                    count +=1 
        
            return {'boletos_vencidos':boletos_vencidos,
                    'contador':count} ,200
 
        return {
            "status":"2",
            "msg":"nenhum cliente encontrado"
        }