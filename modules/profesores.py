class Profesores:
    # n_materia se refiere al nombre de la materia
    # cursos se refiere a los paralelos A B C
    # Año se refiere al año lectivo que corresponde para el profesor
    def __init__(self,id_profe,nombre,n_materia,cursos,año,cedula,clave):
        
        self.id_profe=id_profe
        self.nombre=nombre
        self.n_materia=n_materia
        self.cursos=cursos
        self.año=año
        self.cedula=cedula
        self.clave=clave
        
        
    def ProfesorDBCollection(self):
        return{
            'id_profe':self.id_profe,
            "nombre":self.nombre,
            'n_materia':self.n_materia,
            'cursos':self.cursos,
            'año':self.año,
            'cedula':self.cedula,
            'clave':self.clave
        }