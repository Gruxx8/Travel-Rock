README

**Integrantes:** Juan Araya - Diego Contreras - Diego Gómez - Daniel Guzmán
**Asignatura:** Sistemas de información para la gestión
**Universidad:** Universidad Federico Santa María
**Fecha:** 3 de Julio de 2025

---

**1. Introducción al Proyecto**

Este proyecto es una aplicación de escritorio desarrollada en Python utilizando el framework PyQt5, que permite la gestión de una base de datos de "Travel Rock". La aplicación interactúa con una base de datos MySQL 
para realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar) sobre varias tablas, como Estudiantes, Coordinadores, Viajes, Reservas, Seguros y Vuelos.

El objetivo principal fue desarrollar una interfaz de usuario intuitiva que facilitara la interacción con la base de datos, implementando control de permisos por nivel de usuario y gestionando 
de forma robusta los identificadores únicos (IDs) de los registros.

---

**2. Estructura del Proyecto y Archivos Clave**

El proyecto se compone de los siguientes elementos principales:

* **`codetravel.py`**: El archivo principal de la aplicación Python. Contiene la lógica de conexión a la base de datos, la gestión de ventanas, las operaciones CRUD y la configuración de la interfaz de usuario.
* **`ingreso.ui`**: Archivo de diseño de interfaz de usuario para la ventana de inicio de sesión 
* **`tabla.ui`**: Archivo de diseño de interfaz de usuario para la ventana de selección de tablas
* **`estudiantes.ui`**: Archivo de diseño para la gestión de la tabla "Estudiantes" 
* **`coordinadores.ui`**: Archivo de diseño para la gestión de la tabla "Coordinadores"
* **`viajes.ui`**: Archivo de diseño para la gestión de la tabla "Viajes" 
* **`reservas.ui`**: Archivo de diseño para la gestión de la tabla "Reservas" 
* **`seguros.ui`**: Archivo de diseño para la gestión de la tabla "Seguros" 
* **`vuelos.ui`**: Archivo de diseño para la gestión de la tabla "Vuelos"
* **`final.txt`**: Archivo de los datos para la gestión de las tablas.
---

**3. Secuencia de Configuración y Ejecución**

Para configurar y ejecutar este proyecto, sigue los siguientes pasos en el orden indicado:

**3.1. Configuración de la Base de Datos (MySQL)**

1.  Asegúrate de tener MySQL instalado y en funcionamiento.
2.  Accede a tu cliente MySQL** (por ejemplo, MySQL Workbench, DBeaver, o la línea de comandos).
3.  Ejecuta el script SQL proporcionado (`final.txt`)**. Este script se encarga de:
    	Eliminar la base de datos `travel_rock` si existe y crearla de nuevo.
    	Definir el esquema de todas las tablas (`Colegios`, `Estudiantes`, `Coordinadores`, `Viajes`, `Reservas`, `Contratos`, `Pagos`, `Seguros`, `Vuelos`).
    		Importante:** En esta fase, las columnas de ID (claves primarias) se definen como `INT PRIMARY KEY` pero **SIN `AUTO_INCREMENT`**. Esto es fundamental para permitir 
			      la inserción de los IDs específicos que se encuentran en los datos de ejemplo.
    	Poblar todas las tablas con los datos iniciales predefinidos. Esto establece una base de datos con información coherente y relaciones ya establecidas.

**3.2. Preparación del Entorno Python**

1.  **Instala Python 3.**
2.  **Instala las bibliotecas necesarias** utilizando pip:
    ```bash
    pip install PyQt5 PyMySQL
    ```
3.  **Coloca todos los archivos `.ui`** y el archivo `codetravel.py` en el mismo directorio.

**3.3. Ejecución de la Aplicación Python**

1.  Abre una terminal o línea de comandos.
2.  Navega hasta el directorio donde guardaste los archivos del proyecto.
3.  Ejecuta la aplicación:
    ```bash
    python codetravel.py
    ```
4.  La aplicación se iniciará mostrando la ventana de inicio de sesión (`ingreso.ui`).

**3.4. Flujo de la Aplicación y Gestión de IDs**

1.  **Inicio de Sesión:** Ingresa las credenciales de tu base de datos.
    * **Usuario `root` (o cualquier usuario con permisos de administrador, nivel '03'):** Al iniciar sesión con este nivel de permiso, la aplicación ejecutará internamente una función que 
      **modificará el esquema de todas las tablas para añadir la propiedad `AUTO_INCREMENT`** a sus respectivas columnas de ID (`ID_Colegio`, `ID_Estudiante`, etc.). Esto se hace una única vez, 
      después de que los datos iniciales (con IDs manuales) ya están en la base de datos. Esto es crucial para la funcionalidad de "Agregar" datos por parte del usuario.
    * Otros niveles de usuario (`01`, `02`) no ejecutarán esta modificación de esquema, ya que no tienen permisos para ello.
2.  **Selección de Tabla:** Una vez conectado, se mostrará la ventana `tabla.ui`, donde podrás seleccionar la tabla a gestionar.
3.  **Ventanas CRUD:** Al seleccionar una tabla, se abrirá la ventana CRUD correspondiente (ej., `estudiantes.ui`).
    * **Carga de Datos:** Los datos existentes se cargarán desde la base de datos y se mostrarán en la tabla.
    * **Permisos:** Los botones "Añadir", "Actualizar" y "Borrar" se habilitarán o deshabilitarán según el `user_level` con el que se haya iniciado sesión.
    * **Agregar Datos:** Cuando el usuario utiliza la función "Agregar", la aplicación Python realiza lo siguiente:
        * Consulta la base de datos para obtener el `MAX(ID_)` actual de la tabla.
        * Calcula el `next_id` como `MAX(ID_) + 1`.
        * Inserta el nuevo registro en la base de datos **proporcionando este `next_id` calculado**. Esto es necesario porque, aunque la columna ahora es `AUTO_INCREMENT`, el mecanismo de cálculo manual dentro del código garantiza que los nuevos IDs continúan la secuencia a partir de los IDs preexistentes. Esta es una estrategia para entornos donde la aplicación debe predecir o controlar el siguiente ID, o donde los IDs iniciales no son secuenciales desde 1.
    * **Editar/Borrar Datos:** Estas operaciones se basan en el ID proporcionado por el usuario y siguen la lógica estándar de SQL `UPDATE` y `DELETE`.

---

**4. Consideraciones de Diseño y Estilo (PyQt5 CSS)**

La interfaz de usuario ha sido estilizada utilizando Hojas de Estilo en Cascada (CSS) de Qt. Esto permite una personalización avanzada del aspecto visual de la aplicación:

* **Estilo Global de QMessageBox:** Se ha aplicado un `app.setStyleSheet()` al inicio de la aplicación para asegurar que todos los cuadros de mensaje (`QMessageBox`) tengan un fondo oscuro (`#333333`), 
                                 texto blanco y botones naranja, garantizando coherencia y legibilidad.
* **Estilo de QTableWidget Headers:** Los encabezados de las tablas (`QTableWidget`) han sido estilizados para coincidir con el tema oscuro general de la aplicación, utilizando un fondo `#1e1e1e` y texto
                                 blanco. El botón de la esquina superior izquierda de la tabla (`QTableCornerButton::section`) también se ha ajustado a este color para una integración visual completa.
* **Colores y Paleta:** Se utilizan tonos de gris oscuro/negro para el fondo, naranja (`#FF692E`) para los elementos interactivos (botones principales, bordes resaltados), y blanco para el texto, proporcionando 
                        un contraste adecuado y una estética moderna.
