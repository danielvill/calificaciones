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
    # Obtener cédulas únicas
    cedulas_unicas = db['profesor'].distinct("cedula")
    # Modifica esta línea en tu ruta
  
    
    # Obtener el primer registro de cada profesor
    profesores_unicos = []
    for cedula in cedulas_unicas:
        prof = db['profesor'].find_one({"cedula": cedula})
        profesores_unicos.append(prof)
    
    if request.method == 'POST':
        id_resultado = str(get_next_sequence('resultadoId')).zfill(1)
        resultado = db['resultado']
        
        # Datos fijos (se repiten en todos los registros)
        cedula = request.form['cedula']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        paralelo = request.form['paralelo']
        n_año = request.form['n_año']
        profesor = request.form['profesor']  # Nombre del profesor (puede ser el mismo o diferente)
        fecha_creacion = request.form['fecha_creacion']
        
        # Datos variables (arrays)
        materias = request.form.getlist('materias[]')
        bimestres = request.form.getlist('bimestre[]')
        notas = request.form.getlist('nota[]')
        
        # Validar que los arrays tengan la misma longitud
        if not (len(materias) == len(bimestres) == len(notas)):
            flash("Error: Los datos enviados no son consistentes", "error")
            return redirect(url_for('tareas.adresultado'))
        
        # Preparar todos los documentos a insertar
        documentos_a_insertar = []
        for i in range(len(materias)):
            # Generar un ID único para cada registro (opcional)
            #id_resultado = str(get_next_sequence('resultadoId')).zfill(1)
            
            documento = {
                #"_id": id_resultado,  # O puedes omitirlo si MongoDB genera automáticamente el ID
                "cedula": cedula,
                "nombre": nombre,
                "apellido": apellido,
                "paralelo": paralelo,
                "n_año": n_año,
                "fecha_creacion": fecha_creacion,
                "materias": materias[i],
                "bimestre": bimestres[i],
                "profesor": profesor,  # Puede ser el mismo o diferente
                "nota": notas[i]
            }
            # Verificar si ya existe un registro con los mismos datos
            if resultado.find_one({
                "cedula": cedula,
                "materias": materias[i],
                "bimestre": bimestres[i],
                
            }):
                flash(f"Advertencia: Ya existe un examen para {nombre} en {materias[i]}, {bimestres[i]} . No se duplicará.", "warning")
                # No se agrega el documento a la lista para insertar
            else:
                documentos_a_insertar.append(documento)
        # Insertar todos los registros en una sola operación
        if documentos_a_insertar:
            resultado.insert_many(documentos_a_insertar)
            
            flash(f"✅ Se guardaron {len(documentos_a_insertar)} calificaciones correctamente", "success")
        else:
            flash("⚠️ No se recibieron datos para guardar", "warning")
        
        return redirect(url_for('tareas.transicion'))
    else:
        return render_template("admin/in_resultado.html",estudiante = estudiante ,materia = materia ,profesor_unicos=profesores_unicos)




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
        resultado.update_one ({"cedula":edire},{"$set":{"nombre":nombre ,"apellido":apellido , "paralelo":paralelo, "n_año":n_año,  "fecha_creacion":fecha_creacion, "materias":materias, "bimestre":bimestre,"nota":nota}})
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