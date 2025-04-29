from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.tareas import Tarea
from pymongo import MongoClient
db = dbase()

tareas = Blueprint('tareas', __name__)

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

@tareas.route("/admin/in_tarea", methods=['GET', 'POST'])
def adtarea():
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
        resultado = db['tareas']
        
        # Datos fijos (se repiten en todos los registros)
        cedula = request.form['cedula']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        paralelo = request.form['paralelo']
        n_año = request.form['n_año']
        profesor = request.form['profesor']  # Nombre del profesor (puede ser el mismo o diferente)
        
        # Datos variables (arrays)
        deberes = request.form.getlist('deber[]')
        materias = request.form.getlist('materias[]')
        bimestres = request.form.getlist('bimestre[]')
        notas = request.form.getlist('nota[]')
        
        # Validar que los arrays tengan la misma longitud
        if not (len(deberes) == len(materias) == len(bimestres) == len(notas)):
            flash("Error: Los datos enviados no son consistentes", "error")
            return redirect(url_for('tareas.adtarea'))
        
        # Preparar todos los documentos a insertar
        documentos_a_insertar = []
        for i in range(len(deberes)):
            documento = {
                #"_id": id_resultado,  # O puedes omitirlo si MongoDB genera automáticamente el ID
                "cedula": cedula,
                "nombre": nombre,
                "apellido": apellido,
                "paralelo": paralelo,
                "n_año": n_año,
                "deber": deberes[i],
                "materias": materias[i],
                "bimestre": bimestres[i],
                "profesor": profesor,
                "nota": notas[i]
            }

            # Verificar si ya existe un registro con los mismos datos
            if resultado.find_one({
                "cedula": cedula,
                "materias": materias[i],
                "bimestre": bimestres[i],
                "deber": deberes[i]  # Incluimos el tipo de deber en la verificación
            }):
                flash(f"Advertencia: Ya existe una calificación para {nombre} en {materias[i]}, {bimestres[i]}, {deberes[i]}. No se duplicará.", "warning")
                # No se agrega el documento a la lista para insertar
            else:
                documentos_a_insertar.append(documento) # Solo agrega si no existe duplicado

        # Insertar los documentos
        if documentos_a_insertar:
            resultado.insert_many(documentos_a_insertar)
            flash(f"✅ Se guardaron {len(documentos_a_insertar)} calificaciones correctamente", "success")
        else:
            flash("⚠️ No se recibieron datos para guardar", "warning")
        return redirect(url_for('tareas.transicion'))
    else:
        return render_template("admin/in_tarea.html",estudiante = estudiante ,materia = materia , profesor_unicos=profesores_unicos)
    
# Animacion para transicion
@tareas.route('/ad_tarea')
def transicion():
    return render_template('transi/ad_tarea.html')

@tareas.route('/tareas/adtarea')
def adtar():
    return redirect(url_for('tareas.adtarea'))

# * Editar Resultado
@tareas.route('/edit_ta/<string:edire>', methods=['GET', 'POST'])
def edit_ta(edire):
    tarea = db["tareas"]
    cedula = request.form["cedula"]
    nombre = request.form["nombre"]
    apellido = request.form["apellido"]
    paralelo = request.form["paralelo"]
    n_año = request.form["n_año"]
    deber = request.form["deber"]
    materias = request.form["materias"]
    bimestre = request.form ["bimestre"]
    nota = request.form["nota"]

    if cedula  and nombre and apellido and paralelo  and n_año  and deber and materias and bimestre  and nota:
        tarea.update_one ({"id_resultado":edire},{"$set":{"cedula":cedula,"nombre":nombre ,"apellido":apellido , "paralelo":paralelo, "n_año":n_año,  "deber":deber, "materias":materias, "bimestre":bimestre,"nota":nota}})
        flash("Editado correctamente " ,"success")
        return redirect(url_for('tareas.v_tarea'))
    else:
        return render_template('admin/tarea.html')

# * Eliminar Tareas
@tareas.route('/delete_ta/<string:elita>')
def delete_ta(elita):
    tarea = db["tareas"]
    documento =  tarea.find_one({"id_resultado":elita})
    nombre = documento["nombre"]
    apellido = documento["apellido"]
    tarea.delete_one({"id_resultado":elita})
    flash("Estudiante " + nombre + " "+ apellido  +  " eliminado correctamente" ,"success") 
    return redirect(url_for('tareas.v_tarea'))


# Visualizar tareas
@tareas.route("/admin/tarea")
def v_tarea():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('tareas.index'))
    tareas = db['tareas'].find()
    materia = db['materia'].find()
    return render_template("admin/tarea.html", tareas=tareas,materia = materia)