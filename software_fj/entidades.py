"""Entidad abstracta y clase Cliente con encapsulacion de datos."""

from abc import ABC, abstractmethod
import re

from .excepciones import DatosInvalidosError


class Entidad(ABC):
    """Base abstracta que exige identificacion y una descripcion."""

    def __init__(self, identificador: str) -> None:
        if not isinstance(identificador, str) or not identificador.strip():
            raise DatosInvalidosError("El identificador es obligatorio.")
        self._identificador = identificador.strip().upper()

    @property
    def identificador(self) -> str:
        return self._identificador

    @abstractmethod
    def describir(self) -> str:
        """Representacion legible de la entidad."""


class Cliente(Entidad):
    """Cliente con datos privados, validados al momento del registro."""

    def __init__(self, identificador: str, nombre: str, correo: str, telefono: str) -> None:
        super().__init__(identificador)
        if not isinstance(nombre, str) or not re.fullmatch(
            r"[^\W\d_]+(?:[ '-][^\W\d_]+)*", nombre.strip(), flags=re.UNICODE
        ) or not 3 <= len(nombre.strip()) <= 80:
            raise DatosInvalidosError("El nombre debe contener de 3 a 80 caracteres alfabeticos.")
        if not isinstance(correo, str) or not re.fullmatch(
            r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", correo.strip()
        ):
            raise DatosInvalidosError("El correo electronico no es valido.")
        if not isinstance(telefono, str) or not re.fullmatch(r"\+?\d{7,15}", telefono.strip()):
            raise DatosInvalidosError("El telefono debe tener entre 7 y 15 digitos.")
        self.__nombre = nombre.strip()
        self.__correo = correo.strip().lower()
        self.__telefono = telefono.strip()

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def correo(self) -> str:
        return self.__correo

    @property
    def telefono(self) -> str:
        return self.__telefono

    def describir(self) -> str:
        return f"Cliente {self.identificador}: {self.__nombre}"
