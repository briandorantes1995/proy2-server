import os
import jwt
from flask import Flask, request, Response, make_response, jsonify
from flask_cors import CORS
from prisma import Prisma
from dotenv import load_dotenv
from waitress import serve
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta


load_dotenv()
app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    return 'Inicio Proy Int 2'


# Registro de Usuario
@app.route('/registro', methods=['POST'])
async def registro_usuario():
    db = Prisma()
    try:
        await db.connect()
        user = await db.usuario.create(
            data={
                'nombre': request.form['nombre'],
                'email': request.form['email'],
                'password': generate_password_hash(request.form['password']),
            },
        )
        if user:
            return Response("Usuario Creado Exitosamente", status=200)
        else:
            return Response("No se pudo crear el usuario", status=400)
    except Exception as e:
        return Response("Error en la creación de usuario" + str(e), status=500)
    finally:
        await db.disconnect()


# Login de Usuario
@app.route('/login', methods=['POST'])
async def login_usuario():
    auth = request.form

    if not auth or not auth.get('email') or not auth.get('password'):
        return make_response(
            'Could not verify', 401, {'WWW-Authenticate': 'Basic realm ="Login required !!"'})
    db = Prisma()
    try:
        await db.connect()
        user = await db.usuario.find_unique(
            where={
                'email': request.form['email'],
            }
        )

        if not user:
            return make_response(
                'Could not verify', 401, {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'})

        if check_password_hash(user.password, auth.get('password')):
            token = jwt.encode({
                'nombre': user.nombre,
                'email': user.email,
                'exp': datetime.utcnow() + timedelta(minutes=30)
            }, os.environ.get("SECRET_KEY"))
            return make_response(jsonify({'token': token}), 201)

        return make_response('Could not verify', 403, {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'})
    except Exception as e:
        return Response("Error al Logearse" + str(e), status=500)
    finally:
        await db.disconnect()


# Mostrar de Usuarios
@app.route('/mostrarUsuarios', methods=['GET'])
async def mostrar_usuarios():
    db = Prisma()
    try:
        await db.connect()
        usuarios = await db.usuario.find_many()
        if usuarios:
            usuarios_serializados = []
            for usuario in usuarios:
                usuario_serializado = {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'email': usuario.email,
                    'hospedado_actualmente': usuario.hospedado,
                    'cuarto': usuario.cuarto,
                }
                usuarios_serializados.append(usuario_serializado)
            return make_response(jsonify({'usuarios': usuarios_serializados}), 201)
        else:
            return Response("No se pueden mostrar los usuarios", status=400)
    except Exception as e:
        return Response("Erro al mostrar los usuarios" + str(e), status=500)
    finally:
        await db.disconnect()


# Habitaciones----------------------------------------------------------------------------------------------------------
# Creat Tipo(doble,sencilla...)
@app.route('/crearTipo', methods=['POST'])
async def crear_tipo():
    db = Prisma()
    try:
        await db.connect()
        tipo = await db.tipohabitacion.create(
            data={
                'tipo': request.form['nombre'],
                'descripcion': request.form['descripcion'],
            },
        )
        if tipo:
            return Response("Se ha registrado Tipo de habitacion", status=200)
        else:
            return Response("No se pudo crear el tipo de habitacion", status=400)
    except Exception as e:
        return Response("Error al crear el tipo" + str(e), status=500)
    finally:
        await db.disconnect()


# Mostrar Tipos
@app.route('/Tipos', methods=['GET'])
async def mostrar_tipos():
    db = Prisma()
    try:
        await db.connect()
        tipos = await db.tipohabitacion.find_many()

        if tipos:
            tipos_serializados = []
            for tipo in tipos:
                tipo_serializado = {
                    'id': tipo.id,
                    'tipo': tipo.tipo,
                    'descripcion': tipo.descripcion,
                }
                tipos_serializados.append(tipo_serializado)
            return make_response(jsonify({'tipos': tipos_serializados}), 201)
        else:
            return Response("No se pueden mostrar los tipos de habitacion", status=400)
    except Exception as e:
        return Response("Error al mostrar los tipos de habitaciones" + str(e), status=500)
    finally:
        await db.disconnect()


# Crear Habitacion
@app.route('/crearHabitacion', methods=['POST'])
async def crear_habitacion():
    db = Prisma()
    try:
        await db.connect()
        tipo_habitacion = await db.tipohabitacion.find_first(where={"tipo": request.form['tipo']})
        habitacion = await db.habitaciones.create(
            data={
                'numero': request.form['numero'],
                'costo': request.form['costo'],
                'tipo': {
                    'connect': {
                        'id': tipo_habitacion.id
                    }
                },
            },
        )
        if habitacion:
            return Response("Se ha registrado la habitacion", status=200)
        else:
            return Response("No se pudo registrar/crear la habitacion", status=400)
    except Exception as e:
        return Response("Error al crear habitacion" + str(e), status=500)
    finally:
        await db.disconnect()


# Mostrar Habitaciones
@app.route('/Habitaciones', methods=['GET'])
async def mostrar_habitaciones():
    db = Prisma()
    try:
        await db.connect()
        habitaciones = await db.habitaciones.find_many()
        if habitaciones:
            habitaciones_serializados = []
            for habitacion in habitaciones:
                tipo_habitacion = await db.tipohabitacion.find_first(
                    where={"id": habitacion.tipohabitacionId}
                )
                habitacion_serializado = {
                    'id': habitacion.id,
                    'numero': habitacion.numero,
                    'tipo': tipo_habitacion.tipo,
                    'descripcion': tipo_habitacion.descripcion,
                    'costo': habitacion.costo,
                }
                habitaciones_serializados.append(habitacion_serializado)
            return make_response(jsonify({'habitaciones': habitaciones_serializados}), 201)
        else:
            return Response("No se pueden mostrar los tipos de habitacion", status=400)
    except Exception as e:
        return Response("Error al mostrar las habitaciones disponibles" + str(e), status=500)
    finally:
        await db.disconnect()


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)




