from bson import ObjectId
from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.profesores import Profesores
from modules.resultado import Resultado
from modules.tareas import Tarea
from pymongo import MongoClient
db = dbase()

profesores = Blueprint('profesores', __name__)

# Este codigo es para lo que es el ID
# id_profe n_materia  cursos  año  fecha_creacion

def get_next_sequence(name): 
    seq = db.seqs.find_one({'_id': name})
    if seq is None:
        # Inicializa 'añoId' en 220 si no existe
        db.seqs.insert_one({'_id': 'profeId', 'seq': 0})
        seq = db.seqs.find_one({'_id': name})

    result = db.seqs.find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        return_document=True
    )
    return result.get('seq')

# Ingresar profesores
@profesores.route("/admin/in_profesor", methods=['GET', 'POST'])
def adpro():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('profesor.index')) 
    materia = db["materia"].find()
    if request.method == 'POST':
        id_profe = str(get_next_sequence('profeId')).zfill(1)
        profesor = db['profesor']
        nombre = request.form['nombre']
        materias_seleccionadas = request.form.getlist('n_materia[]')
        cursos = request.form['cursos']
        año = request.form['año']
        cedula = request.form['cedula']
        clave = request.form['clave']

        for n_materia in materias_seleccionadas:
            print (materias_seleccionadas)
            profi = Profesores(id_profe,nombre,n_materia,cursos,año,cedula,clave)
            profesor.insert_one(profi.ProfesorDBCollection())
        flash("Profesor Ingresado exitosamente" ,"success")
        return redirect(url_for('profesores.transicion'))
    else:
        return render_template("admin/in_profesor.html",materia=materia)


# Animacion para transicion
@profesores.route('/ad_profe')
def transicion():
    return render_template('transi/ad_profe.html')

@profesores.route('/profesores/adpro')
def adprofe():
    return redirect(url_for('profesores.adpro'))


# id_profe n_materia  cursos  año  fecha_creacion


# Editar profesores
@profesores.route('/edit_profesor/<string:edpro>', methods=['GET', 'POST'])#
def edit_profesor(edpro):
    profesor = db['profesor']
    nombre = request.form["nombre"]
    n_materia = request.form["n_materia"]
    cursos = request.form['cursos']
    año = request.form["año"]
    cedula = request.form["cedula"]
    
    if nombre and  n_materia and cursos and año and cedula :
        profesor.update_one({'id_profe' : edpro}, {'$set' : { "nombre":nombre  , "n_materia":n_materia ,"cursos": cursos ,"año": año ,  "cedula" :cedula }})
        flash("Profesor editado correctamente " ,"success")
        return redirect(url_for('profesores.v_profe'))
    else:
        return render_template('admin/profesor.html')


# * Eliminar año
@profesores.route('/delete_profe/<string:elipro>')
def delete_profe(elipro):
    profesor = db["profesor"]
    documento =  profesor.find_one({"id_profe":elipro})
    id_profe = documento["id_profe"]
    profesor.delete_one({"id_profe":elipro})
    flash(  "Codigo " +  id_profe +  " eliminado correctamente" ,"success") 
    return redirect(url_for('profesores.v_profe'))




# Visualizar año
@profesores.route("/admin/profesor")
def v_profe():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('profesores.index'))
    profesor = db['profesor'].find()
    materia = db["materia"].find()
    return render_template("admin/profesor.html", profesor=profesor,materia=materia)


# Este es apartado de los Profesores todo el codigo que pertenesca a ellos sera procesado aqui

@profesores.route("/profesor/estudiantes", methods=['GET', 'POST'])
def v_proestudi():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('profesores.index'))
    
    # Obtener la información del profesor que ha iniciado sesión
    cedula_profesor = session['username']
    profesor = db['profesor'].find_one({'cedula': cedula_profesor})
    
    if not profesor:
        flash("Profesor no encontrado")
        return redirect(url_for('profesores.index'))
    
    # Filtrar los estudiantes según el año y el paralelo asignados al profesor
    estudiantes = db['estudiante'].find({
        'n_año': profesor['cursos'], 
        'paralelo': profesor['año']
    })
    
    return render_template("profesor/estudiantes.html", estudiantes=estudiantes)


# Ingreso de tareas e ingreso de examenes 
# Este codigo es para lo que es el ID tareas
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

@profesores.route("/profesor/in_calificacion", methods=['GET', 'POST'])
def adprota():
    if 'username' not in session:
        flash("Inicia sesión con tu usuario y contraseña")
        return redirect(url_for('resultado.index')) 
    
    # Obtener la información del profesor que ha iniciado sesión
    cedula_profesor = session['username']
    profesor_actual = db['profesor'].find_one({'cedula': cedula_profesor})
    
    if not profesor_actual:
        flash("Profesor no encontrado")
        return redirect(url_for('profesores.index'))
    
    nombre_profesor = profesor_actual['nombre']
    nombre_materia = profesor_actual['n_materia']
    
    materias_profesor = list(db['profesor'].find({'cedula': cedula_profesor}))
    estudiantes = db['estudiante'].find({
        'n_año': profesor_actual['cursos'], 
        'paralelo': profesor_actual['año']
    })
    todas_materias = db['materia'].find()
    todos_profesores = db['profesor'].find()
    
    if request.method == 'POST':
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
            return redirect(url_for('profesores.adprota'))
        
        # Preparar todos los documentos a insertar
        documentos_a_insertar = []
        for i in range(len(deberes)):
            documento = {
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
        
        return redirect(url_for('profesores.transicion2'))
    
    else:
        return render_template("profesor/in_calificacion.html", 
                            materi=nombre_materia,
                            usuario=nombre_profesor,
                            estudiantes=estudiantes,
                            materia=todas_materias,
                            profesor=todos_profesores,
                            materias_profesor=materias_profesor)
# Animacion para transicion
@profesores.route('/profe')
def transicion2():
    return render_template('transi/profe.html')

@profesores.route('/profesores/adprota')
def prota():
    return redirect(url_for('profesores.adprota'))


# Visualizar los trabajos de los alumnos del profesor
@profesores.route("/profesor/calificacion")
def profetarea():
    if 'username' not in session:
        flash("Inicia sesión con tu usuario y contraseña")
        return redirect(url_for('profesores.index'))

    # Obtener la información del profesor que ha iniciado sesión
    cedula_profesor = session['username']
    profesor = db['profesor'].find_one({'cedula': cedula_profesor})
    
    if not profesor:
        flash("Profesor no encontrado")
        return redirect(url_for('profesores.profetarea'))
    
    # Obtener las tareas y eliminar duplicados por estudiante
    tareas_cursor = db['tareas'].find(
        {
            'n_año': profesor['cursos'], 
            'paralelo': profesor['año']
        }
    )

    # Usamos un diccionario para eliminar duplicados basados en la cédula del estudiante
    estudiantes_unicos = {}
    for tarea in tareas_cursor:
        estudiantes_unicos[tarea['cedula']] = tarea  # Reemplaza si ya existe

    # Convertimos el diccionario a una lista de tareas únicas
    tareas = list(estudiantes_unicos.values())

    materia = db['materia'].find(
        {
            'n_año': profesor['cursos'], 
            'paralelo': profesor['año']
        }
    )
    
    return render_template("profesor/calificacion.html", tareas=tareas, materia=materia)

# Visualizar detalles del cliente por ID y que se pueda revisar 
@profesores.route("/profesor/tareas/<id>")
def p_cali(id):
    if 'username' not in session:
        flash("Inicia sesión con tu usuario y contraseña")
        return redirect(url_for('profesores.index'))
    
    # Buscar todas las tareas del estudiante con la cédula proporcionada
    tareas = list(db['tareas'].find({"cedula": id}))
    
    if not tareas:
        flash("Estudiante no encontrado")
        return redirect(url_for('profesores.profetarea'))  # Cambia al endpoint deseado

    # Extraer datos únicos del estudiante (usamos el primer registro)
    estudiante_unico = {
        "cedula": tareas[0]["cedula"],
        "nombre": tareas[0]["nombre"],
        "apellido": tareas[0]["apellido"],
        "paralelo": tareas[0]["paralelo"],
        "n_año": tareas[0]["n_año"],
    }

    # Agrupar las tareas por "deber" y organizar notas por trimestre
    tareas_por_trimestre = {}
    for tarea in tareas:
        deber = tarea["deber"]
        if deber not in tareas_por_trimestre:
            tareas_por_trimestre[deber] = {"materias": tarea["materias"], "profesor": tarea["profesor"], "trimestres": {}}
        
        # Añadir nota según el trimestre
        tareas_por_trimestre[deber]["trimestres"][tarea["bimestre"]] = tarea["nota"]

    return render_template("profesor/v_califi.html", tareas=tareas_por_trimestre, estudiante=estudiante_unico)

# Parte para editar calificaciones 
# Editar Tareas 
@profesores.route('/edit_procali/', methods=['POST'])
def edit_procali():
    if 'username' not in session:
        flash("Inicia sesión con tu usuario y contraseña")
        return redirect(url_for('profesores.index'))
    
    cedula = request.form["cedula"]
    deber = request.form["deber"]
    bimestre = request.form["bimestre"]
    nueva_nota = request.form["nota"]
    
    if cedula and deber and bimestre and nueva_nota:
        db['tareas'].update_one(
            {"cedula": cedula, "deber": deber, "bimestre": bimestre},
            {'$set': {"nota": nueva_nota}}
        )
        flash("Calificación editada correctamente", "success")
        return redirect(url_for('profesores.p_cali', id=cedula))
    else:
        flash("Datos incompletos", "error")
        return redirect(url_for('profesores.p_cali', id=cedula))

# Parte del codigo que necesito para agregar examen

# Este codigo es para lo que es el ID para examen
def get_next_sequence(name): 
    seq = db.seqs.find_one({'_id': name})
    if seq is None:
        # Inicializa 'añoId' en 220 si no existe
        db.seqs.insert_one({'_id': 'examenId', 'seq': 0})
        seq = db.seqs.find_one({'_id': name})

    result = db.seqs.find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        return_document=True
    )
    return result.get('seq')

@profesores.route("/profesor/in_examen", methods=['GET', 'POST'])
def proexa():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('profesores.index')) 
    # Obtener la información del profesor que ha iniciado sesión
    
    # Obtener la información del profesor que ha iniciado sesión
    cedula_profesor = session['username']
    profesor_actual = db['profesor'].find_one({'cedula': cedula_profesor})
    
    if not profesor_actual:
        flash("Profesor no encontrado")
        return redirect(url_for('profesores.index'))
    
    nombre_profesor = profesor_actual['nombre']
    nombre_materia = profesor_actual['n_materia']
    
    materias_profesor = list(db['profesor'].find({'cedula': cedula_profesor}))
    estudiantes = db['estudiante'].find({
        'n_año': profesor_actual['cursos'], 
        'paralelo': profesor_actual['año']
    })
    todas_materias = db['materia'].find()
    todos_profesores = db['profesor'].find()
    
    if request.method == 'POST':
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
            return redirect(url_for('profesores.adprota'))
        
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
        
        return redirect(url_for('profesores.transicion3'))
    
    else:
        return render_template("profesor/in_examen.html", 
                            materi=nombre_materia,
                            usuario=nombre_profesor,
                            estudiantes=estudiantes,
                            materia=todas_materias,
                            profesor=todos_profesores,
                            materias_profesor=materias_profesor)

# Animacion para transicion de examenes
@profesores.route('/profetas')
def transicion3():
    return render_template('transi/profetas.html')

@profesores.route('/profesores/proexa')
def examen():
    return redirect(url_for('profesores.proexa'))




# Mostrar los estudiantes

@profesores.route("/profesor/examen")
def v_examen():
    if 'username' not in session:
        flash("Inicia sesion con tu usuario y contraseña")
        return redirect(url_for('profesores.index'))
    # Obtener la información del profesor que ha iniciado sesión
    cedula_profesor = session['username']
    profesor = db['profesor'].find_one({'cedula': cedula_profesor})
    
    if not profesor:
        flash("Profesor no encontrado")
        return redirect(url_for('profesores.index'))
    
    # Filtrar los estudiantes según el año y el paralelo asignados al profesor
    resultado_cursos = db['resultado'].find({
        'n_año': profesor['cursos'], 
        'paralelo': profesor['año']
    })
    
    # Usamos un diccionario para eliminar duplicados basados en la cédula del estudiante
    estudiantes_unicos = {}
    for resultado in resultado_cursos:
        estudiantes_unicos[resultado['cedula']] = resultado  # Reemplaza si ya existe

    # Convertimos el diccionario a una lista de tareas únicas
    resultado = list(estudiantes_unicos.values())

    
    
    
    materia = db['materia'].find(
        {
        'n_año': profesor['cursos'], 
        'paralelo': profesor['año']
    }
    )
    
    return render_template("profesor/examen.html", resultado=resultado,materia = materia)


# Visualizacion de estudiantes de los profesores de forma individual
# Visualizar detalles del cliente por ID y que se pueda revisar 
@profesores.route("/profesor/examen/<id>")
def p_exam(id):
    if 'username' not in session:
        flash("Inicia sesión con tu usuario y contraseña")
        return redirect(url_for('profesores.index'))
    
    # Buscar todas las tareas del estudiante con la cédula proporcionada
    tareas = list(db['resultado'].find({"cedula": id}))
    
    if not tareas:
        flash("Estudiante no encontrado")
        return redirect(url_for('profesores.profetarea'))  # Cambia al endpoint deseado

    # Extraer datos únicos del estudiante (usamos el primer registro)
    estudiante_unico = {
        "cedula": tareas[0]["cedula"],
        "nombre": tareas[0]["nombre"],
        "apellido": tareas[0]["apellido"],
        "paralelo": tareas[0]["paralelo"],
        "n_año": tareas[0]["n_año"],
    }

    # Agrupar las tareas por "deber" y organizar notas por trimestre
    tareas_por_trimestre = {}
    for tarea in tareas:
        deber = tarea["materias"]
        if deber not in tareas_por_trimestre:
            tareas_por_trimestre[deber] = {"materias": tarea["materias"], "profesor": tarea["profesor"], "trimestres": {}}
        
        # Añadir nota según el trimestre
        tareas_por_trimestre[deber]["trimestres"][tarea["bimestre"]] = tarea["nota"]

    return render_template("profesor/v_exam.html", tareas=tareas_por_trimestre, estudiante=estudiante_unico)



# Editar Examenes
@profesores.route('/edit_proexa/', methods=['GET', 'POST'])
def edit_proexa():
    cedula = request.form["cedula"]
    materias = request.form["materias"]  # Asegúrate que coincida con el name del input
    bimestre = request.form["bimestre"]  # "1 Trimestre", "2 Trimestre", etc.
    nueva_nota = request.form["nota"]
    
    if cedula and materias and bimestre and nueva_nota:
        # Actualiza la colección resultado en lugar de tareas
        db['resultado'].update_one(
            {
                "cedula": cedula, 
                "materias": materias, 
                "bimestre": bimestre
            },
            {'$set': {"nota": nueva_nota}}
        )
        flash("Calificación editada correctamente", "success")
        return redirect(url_for('profesores.p_exam', id=cedula))
    else:
        flash("Datos incompletos", "error")
        return redirect(url_for('profesores.p_exam', id=cedula))    