class Materia:
    def __init__(self,id_materia,n_materia,fecha_creacion):
        
        self.id_materia=id_materia
        self.n_materia=n_materia
        self.fecha_creacion=fecha_creacion
        
        
    def MateriaDBCollection(self):
        return{
            'id_materia':self.id_materia,
            'n_materia':self.n_materia,
            'fecha_creacion':self.fecha_creacion
        }