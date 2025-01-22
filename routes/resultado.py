from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.resultado import Resultado
from pymongo import MongoClient
db = dbase()

resultado = Blueprint('resultado', __name__)


# Este codigo es para lo que es el ID
def get_next_sequence(name): 
    seq = db.seqs.find_one({'_id': name})
    if seq is None:
        # Inicializa 'añoId' en 220 si no existe
        db.seqs.insert_one({'_id': 'resultadoId', 'seq': 0})
        seq = db.seqs.find_one({'_id': name})

    result = db.seqs.find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        return_document=True
    )
    return result.get('seq')

@resultado.route("/admin/in_resultado", methods=['GET', 'POST'])
def adresultado():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('resultado.index')) 
    estudiante = db['estudiante'].find()
    materia = db['materia'].find()
    if request.method == 'POST':
        id_resultado = str(get_next_sequence('resultadoId')).zfill(1)
        resultado = db['resultado']
        
        cedula = request.form['cedula']# Este tiene que ser la cedula del estudiante
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        paralelo = request.form['paralelo']
        n_año = request.form['n_año']
        fecha_creacion = request.form['fecha_creacion']
        materias = request.form['materias']
        nota = request.form['nota']

        exist_materias = resultado.find_one ({"materias":materias,"nombre":nombre,"apellido":apellido})

        if exist_materias:
            flash("Ese materia con ese nombre y apellido ya ha sido registrada" ,"danger") 
            return redirect(url_for('resultado.adresultado'))
        else:
            resultado.insert_one(Resultado(id_resultado, cedula, nombre, apellido,paralelo,n_año,fecha_creacion, materias, nota).ResultadoDBCollection())
            flash("Calificacion ingresada exitosamente","success")
            return redirect(url_for('resultado.transicion'))
    else:
        return render_template("admin/in_resultado.html",estudiante = estudiante ,materia = materia)




# Animacion para transicion
@resultado.route('/ad_resultado')
def transicion():
    return render_template('transi/ad_resultado.html')

@resultado.route('/resultado/adresultado')
def adre():
    return redirect(url_for('resultado.adresultado'))

# * Editar Resultado
@resultado.route('/edit_re/<string:edire>', methods=['GET', 'POST'])
def edit_re(edire):
    resultado = db["resultado"]
    cedula = request.form["cedula"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    paralelo = request.form["paralelo"]
    n_año = request.form["n_año"]
    fecha_creacion = request.form["fecha_creacion"]
    materias = request.form["materias"]
    nota = request.form["nota"]

    if cedula  and nombre and apellido and paralelo  and n_año  and fecha_creacion and materias and nota:
        resultado.update_one ({"id_resultado":edire},{"$set":{"cedula":cedula,"nombre":nombre ,"apellido":apellido , "paralelo":paralelo, "n_año":n_año,  "fecha_creacion":fecha_creacion, "materias":materias, "nota":nota}})
        flash("Editado correctamente " ,"success")
        return redirect(url_for('resultado.v_resultado'))
    else:
        return render_template('admin/resultado.html')



# * Eliminar Resultado
@resultado.route('/delete_re/<string:elire>')
def delete_re(elire):
    resultado = db["resultado"]
    documento =  resultado.find_one({"id_resultado":elire})
    nombre = documento["nombre"]
    apellido = documento["apellido"]
    resultado.delete_one({"id_resultado":elire})
    flash("Estudiante " + nombre + " "+ apellido  +  " eliminado correctamente" ,"success") 
    return redirect(url_for('resultado.v_resultado'))






# Visualizar resultado
@resultado.route("/admin/resultado")
def v_resultado():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('resultado.index'))
    resultado = db['resultado'].find()
    materia = db['materia'].find()
    return render_template("admin/resultado.html", resultado=resultado,materia = materia)

# Visualizar individual

@resultado.route("/admin/individual", methods=['GET', 'POST'])
def individual():
    if 'username' not in session:
        flash("Inicia sesión con tu usuario y contraseña")
        return redirect(url_for('resultado.index'))
    
    estudiante = db["estudiante"].find()
    if request.method == 'POST':
        cedula = request.form.get('cedula')
        resultado = db['resultado'].find({"cedula": cedula})
        
        datos = {}
        for doc in resultado:
            datos["cedula"] = doc["cedula"]
            datos["nombre"] = doc["nombre"]
            datos["apellido"] = doc["apellido"]
            datos["paralelo"] = doc["paralelo"]
            datos["n_año"] = doc["n_año"]
            if "materias" not in datos:
                datos["materias"] = []
            datos["materias"].append({"materia": doc["materias"], "nota": doc["nota"]})

        return render_template("admin/individual.html", datos=datos,estudiante = estudiante)
    
    return render_template("admin/individual.html",estudiante = estudiante)
