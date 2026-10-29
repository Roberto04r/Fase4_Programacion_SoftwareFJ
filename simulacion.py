"""Ejecuta mas de diez operaciones reales, exitosas y fallidas, sin detenerse."""

from software_fj import (
    Asesoria, Equipo, ErrorSoftwareFJ, Sala, SistemaSoftwareFJ
)


def ejecutar_simulacion() -> None:
    sistema = SistemaSoftwareFJ()
    exitos = 0
    errores = 0

    def operacion(descripcion, funcion) -> None:
        nonlocal exitos, errores
        try:
            resultado = funcion()
        except (ErrorSoftwareFJ, ValueError, TypeError) as error:
            errores += 1
            sistema.logger.error("ERROR CONTROLADO en %s: %s", descripcion, error, exc_info=True)
            print(f"[ERROR CONTROLADO] {descripcion}: {error}")
        else:
            exitos += 1
            print(f"[OK] {descripcion}" + (f" -> {resultado}" if resultado is not None else ""))
        finally:
            print("-" * 62)

    print("=" * 62)
    print(" SOFTWARE FJ - SIMULACION DE OPERACIONES")
    print("=" * 62)
    operacion("1. Registrar cliente valido", lambda: sistema.registrar_cliente(
        "C001", "Maria Garcia", "maria@ejemplo.com", "3001234567").describir())
    operacion("2. Rechazar correo invalido", lambda: sistema.registrar_cliente(
        "C099", "Pedro Perez", "correo_invalido", "3001234567"))
    operacion("3. Registrar otro cliente", lambda: sistema.registrar_cliente(
        "C002", "Luis Martinez", "luis@ejemplo.com", "3019876543").describir())
    operacion("4. Rechazar cliente duplicado", lambda: sistema.registrar_cliente(
        "C001", "Otro Nombre", "otro@ejemplo.com", "3001234568"))
    operacion("5. Registrar sala", lambda: sistema.registrar_servicio(
        Sala("S001", "Sala de reuniones", 80000, 8)).describir())
    operacion("6. Rechazar servicio con tarifa negativa", lambda: sistema.registrar_servicio(
        Equipo("E099", "Equipo defectuoso", -1000, 2)))
    operacion("7. Registrar equipos", lambda: sistema.registrar_servicio(
        Equipo("E001", "Portatil", 50000, 3)).describir())
    operacion("8. Registrar asesoria", lambda: sistema.registrar_servicio(
        Asesoria("A001", "Asesoria de software", 65000, "Ana Torres")).describir())
    operacion("9. Rechazar servicio duplicado", lambda: sistema.registrar_servicio(
        Sala("S001", "Sala repetida", 20000, 4)))
    operacion("10. Crear reserva de sala", lambda: sistema.crear_reserva(
        "R001", "C001", "S001", 2, {"personas": 4}).describir())
    operacion("11. Confirmar reserva de sala", lambda: sistema.confirmar_reserva("R001"))
    operacion("12. Crear segunda reserva de sala", lambda: sistema.crear_reserva(
        "R002", "C002", "S001", 3, {"personas": 3}).describir())
    operacion("13. Rechazar sala ocupada", lambda: sistema.confirmar_reserva("R002"))
    operacion("14. Crear reserva de 2 equipos", lambda: sistema.crear_reserva(
        "R003", "C002", "E001", 2, {"unidades": 2}, impuesto=19, descuento=10).describir())
    operacion("15. Confirmar equipos con impuesto y descuento", lambda: sistema.confirmar_reserva("R003"))
    operacion("16. Crear reserva sin existencias suficientes", lambda: sistema.crear_reserva(
        "R004", "C001", "E001", 1, {"unidades": 3}).describir())
    operacion("17. Rechazar equipos insuficientes", lambda: sistema.confirmar_reserva("R004"))
    operacion("18. Cancelar reserva de sala", lambda: sistema.cancelar_reserva("R001"))
    operacion("19. Confirmar reserva que estaba pendiente", lambda: sistema.confirmar_reserva("R002"))
    operacion("20. Rechazar reserva inexistente", lambda: sistema.cancelar_reserva("R999"))
    operacion("21. Crear asesoria virtual", lambda: sistema.crear_reserva(
        "R005", "C001", "A001", 2, {"modalidad": "virtual"}).describir())
    operacion("22. Confirmar asesoria", lambda: sistema.confirmar_reserva("R005"))
    operacion("23. Rechazar reserva duplicada", lambda: sistema.crear_reserva(
        "R005", "C001", "A001", 1, {"modalidad": "presencial"}))
    operacion("24. Cancelar equipos y devolver existencias", lambda: sistema.cancelar_reserva("R003"))
    operacion("25. Confirmar reserva tras liberar equipos", lambda: sistema.confirmar_reserva("R004"))

    print(f"RESUMEN: {exitos + errores} operaciones | {exitos} exitosas | {errores} errores controlados")
    print(f"Clientes: {len(sistema.clientes)} | Servicios: {len(sistema.servicios)} | Reservas: {len(sistema.reservas)}")
    for reserva in sistema.reservas:
        print(" -", reserva.describir())
    print("Eventos y errores registrados en logs/eventos.log")


if __name__ == "__main__":
    ejecutar_simulacion()
