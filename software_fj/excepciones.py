"""Excepciones de negocio del sistema Software FJ."""


class ErrorSoftwareFJ(Exception):
    """Error controlado de la aplicacion."""


class DatosInvalidosError(ErrorSoftwareFJ):
    """Datos incorrectos, incompletos o fuera de rango."""


class RegistroDuplicadoError(ErrorSoftwareFJ):
    """El identificador ya esta registrado."""


class RegistroNoEncontradoError(ErrorSoftwareFJ):
    """No existe un cliente, servicio o reserva solicitado."""


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """El servicio no puede aceptar la reserva solicitada."""


class OperacionNoPermitidaError(ErrorSoftwareFJ):
    """La operacion no es compatible con el estado actual."""
