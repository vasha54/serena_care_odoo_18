
class MissingParameterError(Exception):
    """Custom exception to indicate that a required parameter is missing."""

    def __init__(self, parameter):
        text = f"El parámetro '{parameter}' es obligatorio."
        super().__init__(text)


class MissingMultipleParameterError(Exception):
    """Custom exception to indicate that a required parameter is missing."""

    def __init__(self, list_parameters):
        parameter = ", ".join([f"{x}" for x in list_parameters])
        text = (
            f"Se requiere al menos uno de los siguientes parámetros: {parameter}. "
            "Ninguno fue proporcionado."
        )
        super().__init__(text)


class  NotAccessResidence(Exception):
    
    def __init__(self):
        text ="No se tiene acceso a la residencia"
        super().__init__(text)


class  AutheticateFailed(Exception):
    
    def __init__(self):
        text ="Autenticación fallida"
        super().__init__(text)


class DatabaseNotAviable(Exception):

    def __init__(self):
        text = "Base de datos no disponible"
        super().__init__(text)


class EmptyBodyInRequest(Exception):

    def __init__(self):
        text = "Cuerpo vacío en la solicitud"
        super().__init__(text)   

class UserNotFound(Exception):

    def __init__(self):
        text = "No se encontró el usuario"
        super().__init__(text)     