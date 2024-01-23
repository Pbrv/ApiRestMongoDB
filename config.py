from flask import Flask
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
host = os.environ.get("MONGODB_HOST")
usuario = os.environ.get("MONGODB_USUARIO")
passwd = os.environ.get("MONGODB_PASSWORD")
bd = os.environ.get("MONGODB_BD")
        
app = Flask(__name__)

# Para conexiones en la nube se requiere tener instalado el paquete dnspython
# Se ejecuta el comando: py -m pip install pymongo[srv]
app.config["MONGO_URI"] = 'mongodb+srv://pilarbravo17:PilarBrDAW2@daw2.gqzn8s6.mongodb.net/imanol-pilar-daw2'