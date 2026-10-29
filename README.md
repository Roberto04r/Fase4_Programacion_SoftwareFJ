# Fase 4 - Programacion (213023) - Software FJ

**UNAD / ECBTI / Ingenieria de Sistemas**  
**Actividad:** Fase 4 - Practicas simuladas  
**Caso:** Sistema Integral de Gestion de Clientes, Servicios y Reservas.

## Objetivo

Construir y probar un sistema de gestion de clientes y reservas con programacion orientada a objetos y excepciones, **sin base de datos**. Los datos estan en memoria y se pierden cuando termina el programa. Solo los eventos y errores se registran en `logs/eventos.log`.

## Requisitos para ejecutar

- Python 3.10 o superior (recomendado Python 3.12).
- No se necesitan bibliotecas externas; se usa exclusivamente la biblioteca estandar.

## Como ejecutar

Desde la carpeta que contiene `main.py`:

```bash
python main.py
```

Para ejecutar **25 operaciones automaticas**, incluyendo registros correctos e incorrectos, reservas exitosas, reservas rechazadas y cancelaciones:

```bash
python simulacion.py
```

Para verificar las pruebas automaticas:

```bash
python -m unittest discover -s pruebas -v
```

En algunos equipos Windows es necesario usar `py` en lugar de `python`.

**Correccion para Windows:** `pruebas/test_sistema.py` ahora cierra los
manejadores de registro mediante `self.addCleanup(self.sistema.cerrar)` antes
de borrar las carpetas temporales. Esto evita `PermissionError: [WinError 32]`
cuando `unittest` limpia el archivo temporal `eventos.log`.

## Estructura

```text
Fase4_Programacion_SoftwareFJ/
|-- software_fj/
|   |-- __init__.py        # Interfaz publica del paquete
|   |-- entidades.py       # Entidad abstracta y Cliente encapsulado
|   |-- servicios.py       # Servicio abstracto, Sala, Equipo, Asesoria
|   |-- reservas.py        # Reserva, confirmacion, cancelacion y estados
|   |-- excepciones.py     # Excepciones personalizadas
|   `-- sistema.py         # Registro de objetos, logging y validaciones
|-- pruebas/
|   `-- test_sistema.py    # Pruebas automatizadas
|-- main.py                # Menu interactivo
|-- simulacion.py          # 25 casos de demostracion
|-- .gitignore
`-- README.md
```

## Arquitectura y criterios del anexo

| Criterio | Evidencia en el proyecto |
| --- | --- |
| Clase abstracta general | `Entidad(ABC)` en `entidades.py` |
| Encapsulacion y validacion | `Cliente`, propiedades de solo lectura y atributos privados |
| Clase Servicio abstracta | `Servicio(Entidad)` con metodos abstractos |
| Herencia y polimorfismo | `Sala`, `Equipo`, `Asesoria` sobrescriben metodos |
| Sobrecarga/variantes del calculo | `calcular_costo(duracion_horas, impuesto=0, descuento=0, ...)`, anotaciones `@overload` |
| Control de reservas | Clase `Reserva` con estados PENDIENTE, CONFIRMADA, CANCELADA |
| Manejo de excepciones | Excepciones propias; `try/except`, `else`, `finally` |
| Encadenamiento | `raise RegistroNoEncontradoError(...) from error` y conversion Decimal |
| Registro de eventos y errores | Modulo `logging`, archivo `logs/eventos.log` |
| Sin base de datos | Diccionarios de objetos en memoria; ninguna persistencia de datos |
| Al menos 10 operaciones | `simulacion.py` contiene 25 operaciones |
| Validacion con pruebas | `pruebas/test_sistema.py` |

**Nota sobre calculo de costos:** `impuesto` y `descuento` se expresan como porcentajes (por ejemplo, 19 y 10). Se aplica primero el descuento y luego el impuesto. Los costos se redondean a dos decimales utilizando `Decimal`.

**Nota sobre disponibilidad:** como el enunciado no pide fechas ni intervalos de calendario, las salas y asesorias admiten una reserva confirmada a la vez; los equipos descontaran sus unidades hasta su cancelacion. El programa modela la disponibilidad por recursos reservados, no por horas de agenda.

## Guia de GitHub para el grupo

1. Un integrante crea un repositorio GitHub, preferentemente `fase4-software-fj`.
2. Invita a los demas integrantes como colaboradores.
3. Suban la carpeta del proyecto manteniendo la estructura (omitan `__pycache__` y `logs/`).
4. Cada integrante debe realizar cambios identificables y documentar el trabajo realizado mediante commits.
5. Desde el repositorio, verifiquen que `main.py`, `simulacion.py` y las pruebas funcionen.
6. Compartan el **enlace real** del repositorio en el foro de desarrollo de la actividad.
7. En el PDF grupal agreguen portada, introduccion, enlace GitHub, conclusiones y referencias en normas APA.

> El proyecto se entrega como **base tecnica para integrar y revisar en equipo**. La entrega grupal real requiere colaboracion y enlace del repositorio creado por el grupo; no basta con subir archivos comprimidos.

## Referencias para el informe (verificar datos con la guia)

- Python Software Foundation. (2024). *Errores y excepciones*. https://docs.python.org/es/3.12/tutorial/errors.html
- Zambrano, J. P. (2025). *Introduccion al uso de GitHub* [Objeto virtual de informacion]. Repositorio Institucional UNAD. https://repository.unad.edu.co/handle/10596/75876
- Silva, F. D. (2025). *Basics of using GitHub* [Objeto virtual de informacion]. Repositorio Institucional UNAD. https://repository.unad.edu.co/handle/10596/75882
