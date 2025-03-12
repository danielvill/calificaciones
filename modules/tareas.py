class Tarea:
    def __init__(self,id_resultado,cedula,nombre,apellido,paralelo,n_año,deber,materias,bimestre,profesor,nota):
        
        self.id_resultado=id_resultado
        self.cedula=cedula
        self.nombre=nombre
        self.apellido=apellido
        self.paralelo=paralelo
        self.n_año=n_año
        self.deber=deber
        self.materias=materias
        self.bimestre=bimestre
        self.profesor = profesor
        self.nota=nota

    def TareadoDBCollection(self):
        return{
            'id_resultado':self.id_resultado,
            "cedula":self.cedula,
            'nombre':self.nombre,
            'apellido':self.apellido,
            "paralelo":self.paralelo,
            'n_año':self.n_año,
            'deber':self.deber,
            'materias':self.materias,
            'bimestre':self.bimestre,
            'profesor':self.profesor,
            'nota':self.nota
        }