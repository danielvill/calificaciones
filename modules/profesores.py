class Profesores:
    # n_materia se refiere al nombre de la materia
    # cursos se refiere a los paralelos A B C
    # Año se refiere al año lectivo que corresponde para el profesor
    def __init__(self,id_profe,nombre,n_materia,cursos,año,fecha_creacion):
        
        self.id_profe=id_profe
        self.nombre=nombre
        self.n_materia=n_materia
        self.cursos=cursos
        self.año=año
        self.fecha_creacion=fecha_creacion
        
        
    def ProfesorDBCollection(self):
        return{
            'id_profe':self.id_profe,
            "nombre":self.nombre,
            'n_materia':self.n_materia,
            'cursos':self.cursos,
            'año':self.año,
            'fecha_creacion':self.fecha_creacion
        }