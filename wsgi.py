#
# Conteudo do arquivo `wsgi.py`
#
import sys

#Caminho para requisições seguras
sys.path.insert(0, "/var/www/html/py-bemtevi")

from servidor import app as application