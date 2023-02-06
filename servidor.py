#importando bibliotecas
from omie.omie import Omie
from cliente.cliente import Cliente
from login.logar import Login
from endereco.endereco import Endereco
from contato.contato import Contato
from cobrancas.cobrancas import Cobranca
from nota_fiscal.nota_fiscal import Nota_fiscal
from plano.planos import Planos
from radius.free_radius import FreeRadius
from configuracao.configuracao import Configuracao
from logins.logins import Logins
from flask import Flask
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager


app = Flask(__name__)
api = Api(app)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = '15asd3as5d1awe8f1as5'

#Endpoint
api.add_resource(Cliente, '/cliente')
api.add_resource(Login, '/login')
api.add_resource(Endereco, "/endereco")
api.add_resource(Contato, "/contato")
api.add_resource(Omie, "/omie")
api.add_resource(Cobranca, "/cobrancas")
api.add_resource(Nota_fiscal, "/notas_fiscais")
api.add_resource(Planos, "/planos")
api.add_resource(Configuracao, "/configuracao")
api.add_resource(FreeRadius, "/freeRadius")
api.add_resource(Logins, "/logins")



#Configurações de inicialização, EM PRODUÇÃO O DEBUG DEVE SER IGUAL A FALSE
if __name__ == "__main__":
    app.run(host = '0.0.0.0', port=9092, debug=True)