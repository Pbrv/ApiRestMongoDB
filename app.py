from flask import Flask, request, jsonify, Response, send_file, send_from_directory
from flask_pymongo import PyMongo
from bson import json_util, Binary
from bson.objectid import ObjectId
from config import app
import io

mongo = PyMongo(app)

@app.route('/registro', methods=['POST'])
def crear_producto():
    nombreProducto = request.form.get('nombreProducto')
    stock = request.form.get('stock')
    fecha = request.form.get('fecha')
    categoria = request.form.get('categoria')
    imagen = request.files.get('imagen')
    
    if not nombreProducto or not stock or not fecha or not categoria or not imagen:
        return datos_incompletos()
    if not categoria_valida(categoria):
        return categoria_invalida()
    
    # Leer la imagen como en binario
    with imagen.stream as image_stream:
        binary_data = image_stream.read()
        
    id = mongo.db.products.insert_one({
        'nombreProducto': nombreProducto, 
        'stock': stock, 
        'fecha': fecha,
        'categoria': categoria, #########
        'imagen': imagen.filename,
        'imagen_binario': Binary(binary_data)})

    response = {
            'nombreProducto': nombreProducto,
            'stock': stock,
            'fecha': fecha,
            'categoria': categoria,
            'imagen_nombre': imagen.filename
    }
    return response

def categoria_valida(categoria):
    return categoria in ['funko', 'pelicula', 'comic']

@app.route('/productos', methods=['GET'])
def consultar_productos():
    productos = mongo.db.products.find()
    productos_converted = []

    for producto in productos:
        producto['_id'] = str(producto['_id'])

        # Filtrar los campos para excluir el binario
        producto_filtered = {key: value for key, value in producto.items() if not isinstance(value, bytes)}
        
        productos_converted.append(producto_filtered)

    response = json_util.dumps(productos_converted)

    return Response(response, mimetype='application/json')

@app.route('/producto/<id>', methods=['GET'])
def consultar_producto(id):
    producto = mongo.db.products.find_one({'_id': ObjectId(id)})
    
    if producto:  # Encontrado
        response = json_util.dumps(producto)
        return Response(response, mimetype='application/json') # Formato JSON
    else:
        return not_found()

@app.route('/producto/<id>', methods=['DELETE'])
def borrar_producto(id):
    producto = mongo.db.products.find_one({'_id': ObjectId(id)})
    
    if producto:
        borrarProducto = mongo.db.products.delete_one({'_id': ObjectId(id)})
        response = jsonify({'mensaje': 'El producto con ' + id + ' se ha eliminado satisfactoriamente'})
        return response
    else:
        return not_found()

@app.route('/producto/<id>', methods=['PUT'])
def actualizar_registro(id):
    request_data = request.get_json()
    
    if request_data is None:
        return datos_incompletos()
    producto = mongo.db.products.find_one({'_id': ObjectId(id)})
    
    if producto:  # Si se encuentra el producto rear un diccionario de campos
        campos_actualizables = {}
    
    # Verificar si cada campo está presente en la solicitud y agregarlo al diccionario
    if 'nombreProducto' in request_data:
        campos_actualizables['nombreProducto'] = request_data['nombreProducto']
    if 'stock' in request_data:
        campos_actualizables['stock'] = request_data['stock']
    if 'fecha' in request_data:
        campos_actualizables['fecha'] = request_data['fecha']
    
    # Actualizar solo los campos proporcionados
        mongo.db.products.update_one({'_id': ObjectId(id)}, {'$set': campos_actualizables})
        
        response = jsonify({'mensaje': 'El producto con ' + id + ' se ha actualizado correctamente'})
    else:
        response = not_found()

    return response

@app.route('/producto/<id>/imagen', methods=['GET']) #Ver imagen del producto
def obtener_imagen(id):
    producto = mongo.db.products.find_one({'_id': ObjectId(id)})

    if producto and 'imagen' in producto:
        # Obtener los datos binarios de la imagen y devolverla como respuesta
        return send_file(io.BytesIO(producto['imagen']), mimetype='image/jpeg')
    else:
        return not_found()

@app.errorhandler(404)
def not_found(error=None):
    response = jsonify({
        'mensaje': 'Recurso no encontrado: ' + request.url, 
        'status': 404
    })
    response.status_code = 404

    return response

@app.errorhandler(400)
def datos_incompletos(error=None):
    response = jsonify({
        'mensaje': 'Datos incompletos', 
        'status': 400
    })
    response.status_code = 400

    return response
def categoria_invalida(error=None):
    response = jsonify({
        'mensaje': 'La categoría del producto no es válida. Solo puede ser Funko, Película o Comic', 
        'status': 400
    })
    response.status_code = 400

    return response

if __name__ == "__main__":
    app.run(debug=True)