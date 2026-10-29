"""Gestor central; colecciones en memoria y logging de eventos/errores."""

from functools import wraps
import logging
from pathlib import Path
from typing import Callable, TypeVar, Any

from .entidades import Cliente
from .excepciones import RegistroDuplicadoError, RegistroNoEncontradoError
from .reservas import Reserva
from .servicios import Servicio

T = TypeVar("T")


def auditar(funcion: Callable[..., T]) -> Callable[..., T]:
    """Registra los exitos y cada excepcion, sin ocultar los errores."""
    @wraps(funcion)
    def envoltura(self: "SistemaSoftwareFJ", *args: Any, **kwargs: Any) -> T:
        try:
            resultado = funcion(self, *args, **kwargs)
        except Exception:
            self.logger.exception("ERROR en %s", funcion.__name__)
            raise
        else:
            self.logger.info("Operacion realizada: %s", funcion.__name__)
            return resultado
    return envoltura


class SistemaSoftwareFJ:
    """Administra objetos en diccionarios (sin ninguna base de datos)."""

    def __init__(self, archivo_log: str | Path = "logs/eventos.log") -> None:
        ruta = Path(archivo_log).resolve()
        ruta.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(f"SoftwareFJ::{ruta}")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        if not self.logger.handlers:
            manejador = logging.FileHandler(ruta, encoding="utf-8")
            manejador.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
            self.logger.addHandler(manejador)
        self._clientes: dict[str, Cliente] = {}
        self._servicios: dict[str, Servicio] = {}
        self._reservas: dict[str, Reserva] = {}

    def cerrar(self) -> None:
        """Libera el archivo de auditoria, incluso en Windows.

        Se debe llamar al finalizar las pruebas que utilizan logs temporales,
        para evitar el bloqueo de archivos durante su eliminacion.
        """
        for manejador in list(self.logger.handlers):
            self.logger.removeHandler(manejador)
            try:
                manejador.flush()
            finally:
                manejador.close()

    @auditar
    def registrar_cliente(self, identificador: str, nombre: str, correo: str, telefono: str) -> Cliente:
        cliente = Cliente(identificador, nombre, correo, telefono)
        if cliente.identificador in self._clientes:
            raise RegistroDuplicadoError(f"El cliente {cliente.identificador} ya existe.")
        self._clientes[cliente.identificador] = cliente
        return cliente

    @auditar
    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        if not isinstance(servicio, Servicio):
            from .excepciones import DatosInvalidosError
            raise DatosInvalidosError("Debe proporcionar un servicio valido.")
        if servicio.identificador in self._servicios:
            raise RegistroDuplicadoError(f"El servicio {servicio.identificador} ya existe.")
        self._servicios[servicio.identificador] = servicio
        return servicio

    def _obtener(self, coleccion: dict[str, T], identificador: str, tipo: str) -> T:
        """Convierte KeyError en excepcion de dominio y preserva su causa."""
        try:
            return coleccion[identificador.strip().upper()]
        except (KeyError, AttributeError) as error:
            raise RegistroNoEncontradoError(f"No se encontro {tipo} '{identificador}'.") from error

    @auditar
    def crear_reserva(self, identificador: str, id_cliente: str, id_servicio: str,
                      duracion_horas: int, parametros: dict[str, object],
                      impuesto: object = 0, descuento: object = 0) -> Reserva:
        cliente = self._obtener(self._clientes, id_cliente, "el cliente")
        servicio = self._obtener(self._servicios, id_servicio, "el servicio")
        reserva = Reserva(identificador, cliente, servicio, duracion_horas,
                          parametros, impuesto, descuento)
        if reserva.identificador in self._reservas:
            raise RegistroDuplicadoError(f"La reserva {reserva.identificador} ya existe.")
        self._reservas[reserva.identificador] = reserva
        return reserva

    @auditar
    def confirmar_reserva(self, identificador: str):
        return self._obtener(self._reservas, identificador, "la reserva").confirmar()

    @auditar
    def cancelar_reserva(self, identificador: str) -> None:
        self._obtener(self._reservas, identificador, "la reserva").cancelar()

    @property
    def clientes(self) -> tuple[Cliente, ...]:
        return tuple(self._clientes.values())

    @property
    def servicios(self) -> tuple[Servicio, ...]:
        return tuple(self._servicios.values())

    @property
    def reservas(self) -> tuple[Reserva, ...]:
        return tuple(self._reservas.values())
