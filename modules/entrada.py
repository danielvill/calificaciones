class Entrada:
    def __init__(self,id_entrada,nombre,cedula,fecha,hora):
        
        self.id_entrada=id_entrada
        self.nombre=nombre
        self.cedula=cedula
        self.fecha=fecha
        self.hora=hora
        
        
    def EntradaDBCollection(self):
        return{
            'id_entrada':self.id_entrada,
            'nombre':self.nombre,
            'cedula':self.cedula,
            'fecha':self.fecha,
            'hora':self.hora
            
        }