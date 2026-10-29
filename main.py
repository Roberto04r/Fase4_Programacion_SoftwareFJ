"""Menu de consola para ejecutar Software FJ de manera interactiva."""

from software_fj import (
    Asesoria, Equipo, ErrorSoftwareFJ, Sala, SistemaSoftwareFJ
)


def mostrar_menu() -> None:
    print("\n=== SOFTWARE FJ | GESTION DE RESERVAS ===")
    print("1. Registrar cliente")
    print("2. Registrar sala")
    print("3. Registrar equipo")
    print("4. Registrar asesoria")
    print("5. Crear reserva")
    print("6. Confirmar reserva")
    print("7. Cancelar reserva")
    print("8. Mostrar registros")
    print("0. Salir")


def crear_parametros(servicio) -> dict[str, object]:
    if isinstance(servicio, Sala):
        return {"personas": int(input("Numero de asistentes: "))}
    if isinstance(servicio, Equipo):
        return {"unidades": int(input("Unidades a alquilar: "))}
    if isinstance(servicio, Asesoria):
        return {"modalidad": input("Modalidad (virtual/presencial): ").strip().lower()}
    raise ValueError("Tipo de servicio desconocido.")


def main() -> None:
    sistema = SistemaSoftwareFJ()
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opcion: ").strip()
        if opcion == "0":
            print("Programa finalizado correctamente.")
            break
        try:
            if opcion == "1":
                cliente = sistema.registrar_cliente(
                    input("Codigo de cliente: "), input("Nombre y apellido: "),
                    input("Correo: "), input("Telefono: "))
                print("Registrado:", cliente.describir())
            elif opcion in {"2", "3", "4"}:
                codigo = input("Codigo del servicio: ")
                nombre = input("Nombre del servicio: ")
                tarifa = input("Tarifa por hora (COP): ")
                if opcion == "2":
                    servicio = Sala(codigo, nombre, tarifa, int(input("Capacidad: ")))
                elif opcion == "3":
                    servicio = Equipo(codigo, nombre, tarifa, int(input("Existencias: ")))
                else:
                    servicio = Asesoria(codigo, nombre, tarifa, input("Especialista: "))
                sistema.registrar_servicio(servicio)
                print("Registrado:", servicio.describir())
            elif opcion == "5":
                codigo = input("Codigo de reserva: ")
                id_cliente = input("Codigo de cliente: ")
                id_servicio = input("Codigo del servicio: ").strip().upper()
                servicio = next((s for s in sistema.servicios if s.identificador == id_servicio), None)
                if servicio is None:
                    raise ValueError("Registre primero el servicio solicitado.")
                parametros = crear_parametros(servicio)
                duracion = int(input("Duracion en horas: "))
                impuesto = input("Impuesto porcentual (ej. 19): ") or "0"
                descuento = input("Descuento porcentual (ej. 10): ") or "0"
                reserva = sistema.crear_reserva(
                    codigo, id_cliente, id_servicio, duracion, parametros,
                    impuesto=impuesto, descuento=descuento)
                print("Creada:", reserva.describir())
            elif opcion == "6":
                codigo = input("Codigo de la reserva por confirmar: ")
                print("Costo confirmado (COP):", sistema.confirmar_reserva(codigo))
            elif opcion == "7":
                sistema.cancelar_reserva(input("Codigo de la reserva por cancelar: "))
                print("Reserva cancelada.")
            elif opcion == "8":
                print("\nCLIENTES")
                for c in sistema.clientes:
                    print("-", c.describir())
                print("\nSERVICIOS")
                for s in sistema.servicios:
                    print("-", s.describir())
                print("\nRESERVAS")
                for r in sistema.reservas:
                    print("-", r.describir())
            else:
                print("Opcion no valida. Intente nuevamente.")
        except (ErrorSoftwareFJ, ValueError, TypeError) as error:
            # El decorador auditar registra los errores de las operaciones del gestor.
            # Aqui se captura el error para conservar activo el menu.
            sistema.logger.error("Entrada incorrecta u operacion fallida: %s", error)
            print("Error controlado:", error)
        except (KeyboardInterrupt, EOFError):
            print("\nEntrada interrumpida; regresando al menu.")


if __name__ == "__main__":
    main()
