"""Proceso de reserva, confirmacion, cancelacion y control de estados."""

from decimal import Decimal

from .entidades import Cliente, Entidad
from .excepciones import DatosInvalidosError, OperacionNoPermitidaError
from .servicios import Servicio


class Reserva(Entidad):
    """Integra cliente, servicio, duracion, parametros y estado."""

    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"

    def __init__(self, identificador: str, cliente: Cliente, servicio: Servicio,
                 duracion_horas: int, parametros: dict[str, object],
                 impuesto: object = 0, descuento: object = 0) -> None:
        super().__init__(identificador)
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise DatosInvalidosError("La reserva requiere un cliente y un servicio validos.")
        self._cliente = cliente
        self._servicio = servicio
        self._duracion_horas = Servicio.validar_duracion(duracion_horas)
        if not isinstance(parametros, dict):
            raise DatosInvalidosError("Los parametros de la reserva deben ser un diccionario.")
        self._parametros = parametros.copy()  # evita modificaciones externas accidentales
        self._impuesto = impuesto
        self._descuento = descuento
        self._estado = self.PENDIENTE
        self._costo: Decimal | None = None
        self._intentos = 0

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def costo(self) -> Decimal | None:
        return self._costo

    @property
    def intentos(self) -> int:
        return self._intentos

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    def procesar(self) -> Decimal:
        """Valida, calcula y ocupa recursos; mantiene el estado si falla."""
        try:
            if self._estado != self.PENDIENTE:
                raise OperacionNoPermitidaError("Solo se pueden confirmar reservas pendientes.")
            # Primero se calcula: si falla, no se ocupa ningun recurso.
            total = self._servicio.calcular_costo(
                self._duracion_horas, impuesto=self._impuesto,
                descuento=self._descuento, **self._parametros
            )
            self._servicio.reservar(**self._parametros)
        except Exception:
            # El gestor registra la excepcion y la simulacion puede continuar.
            raise
        else:
            self._costo = total
            self._estado = self.CONFIRMADA
            return total
        finally:
            # Se ejecuta tanto en exito como en error.
            self._intentos += 1

    def confirmar(self) -> Decimal:
        """Nombre alternativo para el proceso de confirmacion."""
        return self.procesar()

    def cancelar(self) -> None:
        """Libera los recursos si la reserva estaba confirmada."""
        if self._estado == self.CANCELADA:
            raise OperacionNoPermitidaError("La reserva ya esta cancelada.")
        if self._estado == self.CONFIRMADA:
            self._servicio.liberar(**self._parametros)
        self._estado = self.CANCELADA

    def describir(self) -> str:
        costo = f"${self._costo:,.2f}" if self._costo is not None else "pendiente"
        return (f"Reserva {self.identificador}: cliente {self._cliente.identificador}, "
                f"servicio {self._servicio.identificador}, {self._duracion_horas}h, "
                f"estado {self._estado}, costo {costo}")
