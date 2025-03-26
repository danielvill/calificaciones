from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.resultado import Resultado
from pymongo import MongoClient
db = dbase()
from collections import defaultdict
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
    profesor = db['profesor'].find()
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
        bimestre = request.form ["bimestre"]
        profesor = request.form["profesor"]
        nota = request.form['nota']

        exist_materias = resultado.find_one ({"materias":materias,"nombre":nombre,"apellido":apellido,"bimestre":bimestre })
        if exist_materias:
            flash("Esa materia o ese bimestre con ese nombre y apellido ya ha sido registrada" ,"danger") 
            return redirect(url_for('resultado.adresultado'))
        else:
            resultado.insert_one(Resultado(id_resultado, cedula, nombre, apellido,paralelo,n_año,fecha_creacion, materias, bimestre,profesor,nota).ResultadoDBCollection())
            flash("Calificacion ingresada exitosamente","success")
            return redirect(url_for('resultado.transicion'))
    else:
        return render_template("admin/in_resultado.html",estudiante = estudiante ,materia = materia , profesor = profesor)




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
    bimestre = request.form ["bimestre"]
    nota = request.form["nota"]

    if cedula  and nombre and apellido and paralelo  and n_año  and fecha_creacion and materias and bimestre  and nota:
        resultado.update_one ({"id_resultado":edire},{"$set":{"cedula":cedula,"nombre":nombre ,"apellido":apellido , "paralelo":paralelo, "n_año":n_año,  "fecha_creacion":fecha_creacion, "materias":materias, "bimestre":bimestre,"nota":nota}})
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



@resultado.route("/admin/individual", methods=['GET', 'POST'])
def individual():
    
    if 'username' not in session:
        flash("Inicia sesión con tu usuario y contraseña")
        return redirect(url_for('resultado.index'))
        
    estudiante = db["estudiante"].find()

    if request.method == 'POST':
        cedula = request.form.get('cedula')
        resultado = db['resultado'].find({"cedula": cedula})
        tareas = db['tareas'].find({"cedula": cedula})
        
        # Agrupar notas por materia (como ya lo tienes)
        materias = defaultdict(lambda: {
            "profesor": "",
            "notas": {
                "1 Trimestre": "",
                "2 Trimestre": "",
                "3 Trimestre": "",
                "4 Trimestre": ""
            }
        })
        
        for doc in resultado:
            materia_nombre = doc["materias"]
            materias[materia_nombre]["profesor"] = doc["profesor"]
            materias[materia_nombre]["notas"][doc["bimestre"]] = doc["nota"]
        
        # Agrupar tareas por materia y tipo de deber
        tareas_agrupadas = defaultdict(lambda: {
            "profesor": "",
            "notas": {
                "1 Trimestre": "",
                "2 Trimestre": "",
                "3 Trimestre": "",
                "4 Trimestre": ""
            }
        })
        
        for doc in tareas:
            clave = f"{doc['materias']} - {doc['deber']}"  # Agrupa por materia y tipo de deber
            tareas_agrupadas[clave]["profesor"] = doc["profesor"]
            tareas_agrupadas[clave]["notas"][doc["bimestre"]] = doc["nota"]
        
        # Convertir el defaultdict a un diccionario normal para pasarlo a la plantilla
        datos = {
            "cedula": cedula,
            "nombre": doc["nombre"],
            "apellido": doc["apellido"],
            "paralelo": doc["paralelo"],
            "n_año": doc["n_año"],
            "materias": materias
        }
        
        # Procesar tareas agrupadas
        datos2 = {
            "cedula": cedula,
            "nombre": doc["nombre"],
            "apellido": doc["apellido"],
            "paralelo": doc["paralelo"],
            "n_año": doc["n_año"],
            "materias2": tareas_agrupadas
        }
        
        
        return render_template("admin/individual.html", datos=datos, estudiante=estudiante, datos2=datos2)
    
    return render_template("admin/individual.html", estudiante=estudiante)
