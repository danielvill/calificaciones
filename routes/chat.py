from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.profesores import Profesores
from modules.año import Año
from modules.estudiante import Estudiante
from modules.materia import Materia
from modules.resultado import Resultado
from pymongo import MongoClient
db = dbase()

# Crear un Blueprint para las rutas de chat
chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/admin/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_input = request.form.get('user_input').lower()
        db = dbase()

        # Mapeo de preguntas a colecciones
        preguntas = {
            "muestra que hay en la tabla estudiantes": "estudiante",
            "muestra que hay en la tabla materias": "materia",
        }
        
        if user_input in preguntas:
            coleccion = preguntas[user_input]
            
            datos = list(db[coleccion].find())
            
            return render_template('admin/chat.html', **{coleccion + "s": datos})
        
        
        elif user_input == "muestra que hay en la tabla profesores":
            # Consulta para obtener todos los profesores
            profesores = db['profesor'].find()
            
            # Convertir los resultados a una lista para pasarlos a la plantilla
            profesores_list = list(profesores)
            # Renderizar la plantilla con los datos de los profesores
            return render_template('admin/chat.html', profesores=profesores_list)
        

        elif  user_input == "muestra que hay en la tabla calificaciones":
            # Consulta para obtener todas las calificaciones
            calificaciones = db['resultado'].find()
            
            # Convertir los resultados a una lista para pasarlos a la plantilla
            calificaciones_list = list(calificaciones)
            # Renderizar la plantilla con los datos de las calificaciones
            return render_template('admin/chat.html', calificaciones=calificaciones_list)
        
        # Procesar la pregunta del usuario
        # Procesar la pregunta del usuario
        elif user_input == "muestra a los estudiantes con calificaciones mayores":
            # Consulta para obtener los estudiantes con calificaciones mayores o iguales a "A"
            mayores = db['resultado'].find({"nota": {"$in": ["10", "9.50", "9.60","9","8","8.50","8.60","8.70"]}})
            
            # Convertir los resultados a una lista para pasarlos a la plantilla
            mayores_list = list(mayores)
            # Renderizar la plantilla con los datos de los mayores
            return render_template('admin/chat.html', mayores=mayores_list)
        
        elif user_input == "muestra a los estudiantes con calificaciones menores":
            # Consulta para obtener los estudiantes con calificaciones menores a "C"
            menores = db['resultado'].find({"nota": {"$in": ["7.50", "7.60","7","6","6.50","6.60","6.70","5","5.50","5.60","5.70"]}})
            # Convertir los resultados a una lista para pasarlos a la plantilla
            menores_list = list(menores)
            print(menores_list)
            # Renderizar la plantilla con los datos de los menores
            return render_template('admin/chat.html', menores=menores_list)

        else:
            flash("Pregunta no reconocida", "error")
            return redirect(url_for('chat.chat'))

    return render_template('admin/chat.html')