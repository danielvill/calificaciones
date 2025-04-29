from datetime import datetime
from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from controllers.database import Conexion as dbase
from modules.profesores import Profesores
from modules.año import Año
from modules.estudiante import Estudiante
from modules.materia import Materia
from modules.resultado import Resultado
from pymongo import MongoClient
from reportlab.pdfgen import canvas # *pip install reportlab este es para imprimir reportes
from reportlab.lib.pagesizes import letter #* pip install reportlab 
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle, Spacer ,Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet ,ParagraphStyle
from flask import make_response
from io import BytesIO

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


# Generar PDF de calificaciones mayores @chat_bp.route('/generar_pdf_mayores')
@chat_bp.route('/generar_pdf_mayores')
def generar_pdf_mayores():
    # Crear un buffer para el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Obtener los datos de la base de datos
    db = dbase()
    mayores = list(db['resultado'].find({"nota": {"$in": ["10", "9.50", "9.60", "9", "8", "8.50", "8.60", "8.70"]}}))
    
    # Preparar los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Fecha actual
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Reporte de Calificaciones Mayores - Generado el: {fecha}", styles['Title']))
    elements.append(Paragraph(" ", styles['Normal']))  # Espacio
    
    # Encabezados de la tabla
    data = [['Nombre', 'Apellido', 'Cédula', 'Paralelo', 'Año', 'Materia', 'Trimestre', 'Nota']]
    
    # Agregar datos a la tabla
    for mayo in mayores:
        data.append([
            mayo.get('nombre', ''),
            mayo.get('apellido', ''),
            mayo.get('cedula', ''),
            mayo.get('paralelo', ''),
            mayo.get('n_año', ''),
            mayo.get('materias', ''),
            mayo.get('bimestre', ''),
            mayo.get('nota', '')
        ])
    
    # Crear la tabla
    table = Table(data)
    
    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    
    table.setStyle(style)
    elements.append(table)
    
    # Construir el PDF
    doc.build(elements)
    
    # Preparar la respuesta
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=calificaciones_mayores.pdf'
    
    return response

# Generar PDF de calificaciones menores

@chat_bp.route('/generar_pdf_menores')
def generar_pdf_menores():
    # Crear un buffer para el PDF
    buffer = BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Obtener los datos de la base de datos
    db = dbase()
    menores = list(db['resultado'].find({"nota": {"$in": ["7.50", "7.60", "7", "6", "6.50", "6.60", "6.70", "5", "5.50", "5.60", "5.70"]}}))
    
    # Preparar los elementos del PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    
    # Fecha actual
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Reporte de Calificaciones Menores - Generado el: {fecha}", styles['Title']))
    elements.append(Paragraph(" ", styles['Normal']))  # Espacio
    
    # Encabezados de la tabla
    data = [['Nombre', 'Apellido', 'Cédula', 'Paralelo', 'Año', 'Materia', 'Trimestre', 'Nota']]
    
    # Agregar datos a la tabla
    for meno in menores:
        data.append([
            meno.get('nombre', ''),
            meno.get('apellido', ''),
            meno.get('cedula', ''),
            meno.get('paralelo', ''),
            meno.get('n_año', ''),
            meno.get('materias', ''),
            meno.get('bimestre', ''),
            meno.get('nota', '')
        ])
    
    # Crear la tabla
    table = Table(data)
    
    # Estilo de la tabla
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.black),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    
    table.setStyle(style)
    elements.append(table)
    
    # Construir el PDF
    doc.build(elements)
    
    # Preparar la respuesta
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=calificaciones_menores.pdf'
    
    return response

