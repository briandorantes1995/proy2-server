import os
from flask import Flask, request, Response
from flask_cors import CORS
from prisma import Prisma
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
CORS(app)


@app.route('/')
def hello_world():
    return 'Inicio Proy Int 2'


@app.route('/registro', methods=['POST'])
async def registro_usuario():
    db = Prisma()
    await db.connect()
    user = await db.usuario.create(
        data={
            'nombre': request.form['nombre'],
            'email': request.form['email'],
            'password': generate_password_hash(request.form['password']),
        },
    )
    if user:
        return Response("Usario Creado Exitosamente", status=200)
    else:
        return Response("No se pudo crear el usuario", status=400)


@app.route('/login', methods=['POST'])
def login_usuario():
    db.connect()
    db.usuario.find_unique(
        where={
            'email': request.form['email'],
        }
    )
    return Response("Usario Creado Exitosamente", status=200)


if __name__ == '__main__':
    app.run()
