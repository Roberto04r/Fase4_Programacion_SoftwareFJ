"""Servicio abstracto y tres especializaciones con polimorfismo."""

from abc import abstractmethod
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import overload

from .entidades import Entidad
from .excepciones import DatosInvalidosError, ServicioNoDisponibleError


def numero_decimal(valor: object, campo: str, *, permitir_cero: bool = False) -> Decimal:
    """Convierte a Decimal y rechaza NaN, infinitos, booleanos y negativos."""
    if isinstance(valor, bool):
        raise DatosInvalidosError(f"{campo} debe ser numerico.")
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, ValueError, TypeError) as error:
        raise DatosInvalidosError(f"{campo} debe ser numerico.") from error
    if not numero.is_finite() or numero < 0 or (numero == 0 and not permitir_cero):
        raise DatosInvalidosError(f"{campo} debe ser un numero valido y positivo.")
    return numero


def entero_positivo(valor: object, campo: str, limite: int = 1000) -> int:
    """Comprueba numeros enteros positivos sin aceptar True/False."""
    if isinstance(valor, bool) or not isinstance(valor, int) or not 1 <= valor <= limite:
        raise DatosInvalidosError(f"{campo} debe ser entero entre 1 y {limite}.")
    return valor


class Servicio(Entidad):
    """Modelo abstracto de un servicio reservable."""

    def __init__(self, identificador: str, nombre: str, tarifa: object) -> None:
        super().__init__(identificador)
        if not isinstance(nombre, str) or len(nombre.strip()) < 3:
            raise DatosInvalidosError("El servicio requiere un nombre de al menos 3 caracteres.")
        self._nombre = nombre.strip()
        self._tarifa = numero_decimal(tarifa, "La tarifa")

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa(self) -> Decimal:
        return self._tarifa

    @staticmethod
    def validar_duracion(duracion_horas: int) -> int:
        return entero_positivo(duracion_horas, "La duracion en horas", 168)

    @staticmethod
    def _calcular_total(subtotal: Decimal, impuesto: object, descuento: object) -> Decimal:
        porcentaje_impuesto = numero_decimal(impuesto, "El impuesto", permitir_cero=True)
        porcentaje_descuento = numero_decimal(descuento, "El descuento", permitir_cero=True)
        if porcentaje_impuesto > 100 or porcentaje_descuento > 100:
            raise DatosInvalidosError("Impuesto y descuento deben estar entre 0 y 100 por ciento.")
        total = subtotal * (Decimal("1") - porcentaje_descuento / 100)
        total = total * (Decimal("1") + porcentaje_impuesto / 100)
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @overload
    def calcular_costo(self, duracion_horas: int, *, impuesto: object = 0,
                      descuento: object = 0, **parametros: object) -> Decimal: ...

    @overload
    def calcular_costo(self, duracion_horas: int, impuesto: object,
                      descuento: object = 0, **parametros: object) -> Decimal: ...

    @abstractmethod
    def calcular_costo(self, duracion_horas: int, impuesto: object = 0,
                      descuento: object = 0, **parametros: object) -> Decimal:
        """Implementaciones concretas permiten variantes de impuesto/descuento."""

    @abstractmethod
    def validar_parametros(self, **parametros: object) -> None:
        """Valida la solicitud y disponibilidad del servicio."""

    @abstractmethod
    def reservar(self, **parametros: object) -> None:
        """Ocupa recursos de forma controlada."""

    @abstractmethod
    def liberar(self, **parametros: object) -> None:
        """Libera recursos al cancelar una reserva confirmada."""


class Sala(Servicio):
    """La sala solo admite una reserva simultanea y limita asistentes."""

    def __init__(self, identificador: str, nombre: str, tarifa: object, capacidad: int) -> None:
        super().__init__(identificador, nombre, tarifa)
        self._capacidad = entero_positivo(capacidad, "La capacidad", 500)
        self._ocupada = False

    def validar_parametros(self, **parametros: object) -> None:
        if set(parametros) != {"personas"}:
            raise DatosInvalidosError("La sala exige exclusivamente el parametro 'personas'.")
        personas = entero_positivo(parametros["personas"], "Las personas", 500)
        if personas > self._capacidad:
            raise ServicioNoDisponibleError("La cantidad de personas excede la capacidad de la sala.")
        if self._ocupada:
            raise ServicioNoDisponibleError("La sala esta ocupada.")

    def calcular_costo(self, duracion_horas: int, impuesto: object = 0,
                      descuento: object = 0, **parametros: object) -> Decimal:
        duracion = self.validar_duracion(duracion_horas)
        self.validar_parametros(**parametros)
        return self._calcular_total(self.tarifa * duracion, impuesto, descuento)

    def reservar(self, **parametros: object) -> None:
        self.validar_parametros(**parametros)
        self._ocupada = True

    def liberar(self, **parametros: object) -> None:
        self._ocupada = False

    def describir(self) -> str:
        return f"Sala {self.identificador} ({self.nombre}); capacidad {self._capacidad}"


class Equipo(Servicio):
    """Permite alquilar varias unidades, controlando existencias."""

    def __init__(self, identificador: str, nombre: str, tarifa: object, existencias: int) -> None:
        super().__init__(identificador, nombre, tarifa)
        self._existencias = entero_positivo(existencias, "Las existencias")
        self._disponibles = self._existencias

    @property
    def disponibles(self) -> int:
        return self._disponibles

    def validar_parametros(self, **parametros: object) -> None:
        if set(parametros) != {"unidades"}:
            raise DatosInvalidosError("El alquiler exige exclusivamente 'unidades'.")
        unidades = entero_positivo(parametros["unidades"], "Las unidades")
        if unidades > self._disponibles:
            raise ServicioNoDisponibleError("No hay suficientes equipos disponibles.")

    def calcular_costo(self, duracion_horas: int, impuesto: object = 0,
                      descuento: object = 0, **parametros: object) -> Decimal:
        duracion = self.validar_duracion(duracion_horas)
        self.validar_parametros(**parametros)
        return self._calcular_total(self.tarifa * duracion * int(parametros["unidades"]), impuesto, descuento)

    def reservar(self, **parametros: object) -> None:
        self.validar_parametros(**parametros)
        self._disponibles -= int(parametros["unidades"])

    def liberar(self, **parametros: object) -> None:
        unidades = entero_positivo(parametros.get("unidades"), "Las unidades")
        if self._disponibles + unidades > self._existencias:
            raise DatosInvalidosError("La devolucion excederia las existencias registradas.")
        self._disponibles += unidades

    def describir(self) -> str:
        return f"Equipo {self.identificador} ({self.nombre}); disponibles {self._disponibles}"


class Asesoria(Servicio):
    """Asesoria con modalidad validada y un turno a la vez."""

    def __init__(self, identificador: str, nombre: str, tarifa: object, especialista: str) -> None:
        super().__init__(identificador, nombre, tarifa)
        if not isinstance(especialista, str) or len(especialista.strip()) < 3:
            raise DatosInvalidosError("Debe indicar el nombre del especialista.")
        self._especialista = especialista.strip()
        self._ocupada = False

    def validar_parametros(self, **parametros: object) -> None:
        if set(parametros) != {"modalidad"}:
            raise DatosInvalidosError("La asesoria exige exclusivamente 'modalidad'.")
        if parametros["modalidad"] not in ("virtual", "presencial"):
            raise DatosInvalidosError("La modalidad debe ser 'virtual' o 'presencial'.")
        if self._ocupada:
            raise ServicioNoDisponibleError("El especialista ya tiene un turno reservado.")

    def calcular_costo(self, duracion_horas: int, impuesto: object = 0,
                      descuento: object = 0, **parametros: object) -> Decimal:
        duracion = self.validar_duracion(duracion_horas)
        self.validar_parametros(**parametros)
        return self._calcular_total(self.tarifa * duracion, impuesto, descuento)

    def reservar(self, **parametros: object) -> None:
        self.validar_parametros(**parametros)
        self._ocupada = True

    def liberar(self, **parametros: object) -> None:
        self._ocupada = False

    def describir(self) -> str:
        return f"Asesoria {self.identificador} ({self.nombre}); {self._especialista}"
