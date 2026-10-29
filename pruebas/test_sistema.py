"""Pruebas automaticas ejecutables con unittest de la biblioteca estandar."""

import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from software_fj import (
    Asesoria, DatosInvalidosError, Equipo, OperacionNoPermitidaError,
    RegistroDuplicadoError, RegistroNoEncontradoError, Sala,
    ServicioNoDisponibleError, SistemaSoftwareFJ
)


class PruebasSoftwareFJ(unittest.TestCase):
    def setUp(self) -> None:
        self.directorio = tempfile.TemporaryDirectory()
        self.addCleanup(self.directorio.cleanup)
        self.archivo_log = Path(self.directorio.name) / "eventos.log"
        self.sistema = SistemaSoftwareFJ(self.archivo_log)
        # unittest ejecuta los cleanups en orden inverso: primero cerrar
        # el FileHandler y despues eliminar la carpeta temporal.
        self.addCleanup(self.sistema.cerrar)
        self.sistema.registrar_cliente("C1", "Maria Lopez", "maria@test.com", "3001234567")
        self.sistema.registrar_servicio(Sala("S1", "Sala principal", 80000, 5))
        self.sistema.registrar_servicio(Equipo("E1", "Portatil", 50000, 3))
        self.sistema.registrar_servicio(Asesoria("A1", "Consultoria tecnica", 60000, "Ana Rios"))

    def test_registro_cliente_valido(self):
        self.assertEqual(len(self.sistema.clientes), 1)
        self.assertEqual(self.sistema.clientes[0].correo, "maria@test.com")

    def test_rechaza_correo_incorrecto(self):
        with self.assertRaises(DatosInvalidosError):
            self.sistema.registrar_cliente("C2", "Jose Perez", "incorrecto", "3001234567")

    def test_rechaza_cliente_duplicado(self):
        with self.assertRaises(RegistroDuplicadoError):
            self.sistema.registrar_cliente("C1", "Jose Perez", "jose@test.com", "3001234567")

    def test_rechaza_tarifa_negativa(self):
        with self.assertRaises(DatosInvalidosError):
            self.sistema.registrar_servicio(Equipo("E2", "Otro portatil", -100, 5))

    def test_calculo_sala(self):
        self.sistema.crear_reserva("R1", "C1", "S1", 2, {"personas": 2})
        self.assertEqual(self.sistema.confirmar_reserva("R1"), Decimal("160000.00"))

    def test_no_hace_doble_reserva_sala(self):
        self.sistema.crear_reserva("R1", "C1", "S1", 2, {"personas": 2})
        self.sistema.confirmar_reserva("R1")
        self.sistema.crear_reserva("R2", "C1", "S1", 1, {"personas": 2})
        with self.assertRaises(ServicioNoDisponibleError):
            self.sistema.confirmar_reserva("R2")
        self.assertEqual(self.sistema.reservas[1].estado, "PENDIENTE")
        self.assertEqual(self.sistema.reservas[1].intentos, 1)

    def test_cancelar_deja_disponible_sala(self):
        self.sistema.crear_reserva("R1", "C1", "S1", 1, {"personas": 2})
        self.sistema.confirmar_reserva("R1")
        self.sistema.cancelar_reserva("R1")
        self.sistema.crear_reserva("R2", "C1", "S1", 1, {"personas": 3})
        self.assertEqual(self.sistema.confirmar_reserva("R2"), Decimal("80000.00"))

    def test_alquiler_calculo_con_descuento_e_impuesto(self):
        self.sistema.crear_reserva("R1", "C1", "E1", 2, {"unidades": 2}, impuesto=19, descuento=10)
        self.assertEqual(self.sistema.confirmar_reserva("R1"), Decimal("214200.00"))
        equipo = next(s for s in self.sistema.servicios if s.identificador == "E1")
        self.assertEqual(equipo.disponibles, 1)

    def test_alquiler_sin_existencias_suficientes(self):
        self.sistema.crear_reserva("R1", "C1", "E1", 1, {"unidades": 4})
        with self.assertRaises(ServicioNoDisponibleError):
            self.sistema.confirmar_reserva("R1")

    def test_cancelar_devuelve_equipo(self):
        self.sistema.crear_reserva("R1", "C1", "E1", 1, {"unidades": 2})
        self.sistema.confirmar_reserva("R1")
        self.sistema.cancelar_reserva("R1")
        equipo = next(s for s in self.sistema.servicios if s.identificador == "E1")
        self.assertEqual(equipo.disponibles, 3)

    def test_asesoria_modalidad_incorrecta(self):
        self.sistema.crear_reserva("R1", "C1", "A1", 1, {"modalidad": "telefonica"})
        with self.assertRaises(DatosInvalidosError):
            self.sistema.confirmar_reserva("R1")

    def test_descuento_fuera_de_rango(self):
        self.sistema.crear_reserva("R1", "C1", "S1", 2, {"personas": 2}, descuento=101)
        with self.assertRaises(DatosInvalidosError):
            self.sistema.confirmar_reserva("R1")

    def test_rechaza_duracion_cero(self):
        with self.assertRaises(DatosInvalidosError):
            self.sistema.crear_reserva("R1", "C1", "S1", 0, {"personas": 2})

    def test_encadenamiento_de_excepciones(self):
        try:
            self.sistema.crear_reserva("R1", "NO_EXISTE", "S1", 1, {"personas": 2})
        except RegistroNoEncontradoError as error:
            self.assertIsInstance(error.__cause__, KeyError)
        else:
            self.fail("Se esperaba una excepcion encadenada")

    def test_no_confirma_dos_veces(self):
        self.sistema.crear_reserva("R1", "C1", "S1", 1, {"personas": 2})
        self.sistema.confirmar_reserva("R1")
        with self.assertRaises(OperacionNoPermitidaError):
            self.sistema.confirmar_reserva("R1")

    def test_log_registra_eventos_y_errores(self):
        with self.assertRaises(RegistroNoEncontradoError):
            self.sistema.cancelar_reserva("R_MISSING")
        contenido = self.archivo_log.read_text(encoding="utf-8")
        self.assertIn("Operacion realizada", contenido)
        self.assertIn("ERROR", contenido)
        self.assertIn("RegistroNoEncontradoError", contenido)

    def test_servicio_sin_parametros(self):
        self.sistema.crear_reserva("R1", "C1", "S1", 1, {})
        with self.assertRaises(DatosInvalidosError):
            self.sistema.confirmar_reserva("R1")


if __name__ == "__main__":
    unittest.main()
