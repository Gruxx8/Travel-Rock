import sys
import os
import pymysql
import datetime
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QWidget, QLabel, QVBoxLayout
from PyQt5.uic import loadUi

def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para desarrollo y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Ventana Principal y de Selección (Lógica General) ---

class MainWindow(QMainWindow):
    """ Ventana inicial para la conexión a la base de datos. """
    def __init__(self):
        super().__init__()
        try:
            loadUi(resource_path('ingreso.ui'), self)
        except Exception as e:
            self.setup_fallback_ui("Inicio de Sesión", "Conectar")
            print(f"No se pudo cargar 'ingreso.ui', usando fallback. Error: {e}")
        
        self.connection = None
        self.user_level = None
        self.pushButton_ingreso.clicked.connect(self.connect_to_database)

    def setup_fallback_ui(self, title, button_text):
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 300, 200)
        layout = QtWidgets.QVBoxLayout()
        self.lineEdit_host = QtWidgets.QLineEdit()
        self.lineEdit_host.setPlaceholderText("Host (ej., localhost)")
        self.lineEdit_2_user = QtWidgets.QLineEdit()
        self.lineEdit_2_user.setPlaceholderText("Usuario")
        self.lineEdit_3_pas = QtWidgets.QLineEdit()
        self.lineEdit_3_pas.setPlaceholderText("Contraseña")
        self.lineEdit_3_pas.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pushButton_ingreso = QtWidgets.QPushButton(button_text)
        layout.addWidget(self.lineEdit_host)
        layout.addWidget(self.lineEdit_2_user)
        layout.addWidget(self.lineEdit_3_pas)
        layout.addWidget(self.pushButton_ingreso)
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def connect_to_database(self):
        host = self.lineEdit_host.text()
        user = self.lineEdit_2_user.text()
        password = self.lineEdit_3_pas.text()
        database = "travel_rock"

        if not all([host, user]):
            # Aplicar estilo al QMessageBox localmente si es un error de entrada
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle('Error de Entrada')
            msg_box.setText('El host y el usuario no pueden estar vacíos.')
            msg_box.setStandardButtons(QMessageBox.Ok)
            # El estilo global debería encargarse de esto, pero se podría sobreescribir aquí
            # msg_box.setStyleSheet("QMessageBox { background-color: #333333; color: white; border: 1px solid red; } QLabel { color: white; background-color: #333333; } QPushButton { background-color: #FF692E; color: white; border-radius: 5px; padding: 5px 10px; min-width: 60px; }")
            msg_box.exec_()
            return

        if user == 'root':
            self.user_level = '03'
        elif user.endswith('01'):
            self.user_level = '01'
        elif user.endswith('02'):
            self.user_level = '02'
        elif user.endswith('03'):
            self.user_level = '03'
        else:
            self.user_level = '01'

        try:
            self.connection = pymysql.connect(host=host, user=user, password=password, database=database, cursorclass=pymysql.cursors.DictCursor)
            QMessageBox.information(self, 'Éxito', f'¡Conectado a la base de datos!\nNivel de permiso: {self.user_level}')
            
            # Mostrar advertencia solo para nivel 02, 03 o root
            if self.user_level in ['02', '03'] or user == 'root':
                self.advertencia_window = AdvertenciaOrdenWindow()
                self.advertencia_window.show()
            
            self.tab_selection_window = TablaWindow(self.connection, self.user_level)
            self.tab_selection_window.show()
            self.close()
        except pymysql.Error as e:
            QMessageBox.critical(self, 'Error de Base de Datos', f"No se pudo conectar: {str(e)}")

class TablaWindow(QMainWindow):
    """ Ventana para seleccionar qué tabla gestionar. """
    def __init__(self, connection, user_level):
        super().__init__()
        self.connection = connection
        self.user_level = user_level
        self.ventana = None
        try:
            loadUi(resource_path('tabla.ui'), self)
        except Exception as e:
            self.setWindowTitle("Selección de Tabla")
            self.setGeometry(100, 100, 300, 150)
            layout = QtWidgets.QVBoxLayout()
            self.comboBox_tabla = QtWidgets.QComboBox()
            self.pushButton_ingresartabla = QtWidgets.QPushButton("Abrir Tabla")
            layout.addWidget(QtWidgets.QLabel("Seleccione una tabla para gestionar:"))
            layout.addWidget(self.comboBox_tabla)
            layout.addWidget(self.pushButton_ingresartabla)
            central_widget = QtWidgets.QWidget()
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)
            print(f"No se pudo cargar 'tabla.ui', usando fallback. Error: {e}")

        self.comboBox_tabla.clear()
        # --- Opciones de tabla finalizadas ---
        self.comboBox_tabla.addItems([
            "Estudiantes", "Coordinadores", "Viajes", 
            "Reservas", "Seguros", "Vuelos"
        ])
        self.pushButton_ingresartabla.clicked.connect(self.abrir_tabla)

    def abrir_tabla(self):
        tabla = self.comboBox_tabla.currentText()
        # --- Lógica de apertura de ventanas finalizada ---
        if tabla == "Estudiantes":
            self.ventana = EstudiantesWindow(self.connection, self.user_level)
        elif tabla == "Coordinadores":
            self.ventana = CoordinadoresWindow(self.connection, self.user_level)
        elif tabla == "Viajes":
            self.ventana = ViajesWindow(self.connection, self.user_level)
        elif tabla == "Reservas":
            self.ventana = ReservasWindow(self.connection, self.user_level)
        elif tabla == "Seguros":
            self.ventana = SegurosWindow(self.connection, self.user_level)
        elif tabla == "Vuelos":
            self.ventana = VuelosWindow(self.connection, self.user_level)
        
        if self.ventana:
            self.ventana.show()
            self.close()

# --- Clase Base para Ventanas CRUD (Estructura General) ---
class BaseCrudWindow(QMainWindow):
    def __init__(self, connection, user_level):
        super().__init__()
        self.connection = connection
        self.user_level = user_level

    def setup_permissions(self, btn_add, btn_edit, btn_delete):
        if self.user_level == '01':
            btn_add.setEnabled(False)
            btn_edit.setEnabled(False)
            btn_delete.setEnabled(False)
        elif self.user_level == '02':
            btn_add.setEnabled(True)
            btn_edit.setEnabled(True)
            btn_delete.setEnabled(False)
        elif self.user_level == '03':
            btn_add.setEnabled(True)
            btn_edit.setEnabled(True)
            btn_delete.setEnabled(True)

    def cargar_datos_base(self, table_name, table_widget):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table_name}")
                resultados = cursor.fetchall()
            
            if not resultados:
                table_widget.setRowCount(0)
                table_widget.setColumnCount(0)
                return

            columnas = list(resultados[0].keys())
            table_widget.setColumnCount(len(columnas))
            table_widget.setRowCount(len(resultados))
            table_widget.setHorizontalHeaderLabels(columnas)

            for fila, datos_dict in enumerate(resultados):
                for col, key in enumerate(columnas):
                    table_widget.setItem(fila, col, QTableWidgetItem(str(datos_dict[key])))
            table_widget.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "Error de Carga", f"No se pudo cargar la tabla {table_name}: {str(e)}")

    def volver(self):
        self.close()
        self.tabla_window = TablaWindow(self.connection, self.user_level)
        self.tabla_window.show()

# --- Implementación de la Ventana Estudiantes (Completa) ---
class EstudiantesWindow(BaseCrudWindow):
    def __init__(self, connection, user_level):
        super().__init__(connection, user_level)
        self.ui_file = 'estudiantes.ui'
        self.table_name = 'Estudiantes'
        self.id_column = 'ID_Estudiante'
        
        try:
            loadUi(resource_path(self.ui_file), self)
        except Exception as e:
            QMessageBox.critical(self, "Error de UI", f"No se pudo cargar el archivo de interfaz '{self.ui_file}'.\nError: {e}")
            return

        # Conectar botones usando los nombres específicos de estudiantes.ui
        self.pushButton_visualestu.clicked.connect(self.cargar_datos)
        self.pushButton_4_estuadd.clicked.connect(self.agregar)
        self.pushButton_3_estuact.clicked.connect(self.editar)
        self.pushButton_2_estuborrar.clicked.connect(self.borrar)
        self.pushButton_estuvolver.clicked.connect(self.volver)

        self.setup_permissions(self.pushButton_4_estuadd, self.pushButton_3_estuact, self.pushButton_2_estuborrar)
        self.cargar_datos()

    def cargar_datos(self):
        self.cargar_datos_base(self.table_name, self.tableWidget_cliente)

    def agregar(self):
        if self.user_level not in ['02', '03']:
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para añadir registros.")
            return

        try:
            # Obtener el siguiente ID automáticamente
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT MAX(ID_Estudiante) AS max_id FROM Estudiantes")
                result = cursor.fetchone()
                next_id = (result['max_id'] or 0) + 1

            datos = (
                next_id,
                self.lineEdit_9_nombreestuadd.text(),
                self.lineEdit_rutestuadd.text(),
                self.lineEdit_2_idcolegioestuadd.text()
            )
            if not all(datos[1:]):  # Solo validar los campos excepto el ID
                QMessageBox.warning(self, "Campos Vacíos", "Todos los campos son obligatorios para agregar un estudiante.")
                return

            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO Estudiantes (ID_Estudiante, Nombre, RUT, ID_Colegio) VALUES (%s, %s, %s, %s)", datos)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", f"Estudiante añadido correctamente con ID {next_id}.")
            self.cargar_datos()
        except Exception as e:
            registrar_error(self.connection)
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo añadir el estudiante: {e}")

    def editar(self):
        if self.user_level not in ['02', '03']:
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para editar registros.")
            return
        
        try:
            datos = (
                self.lineEdit_3_nombreestuedi.text(),
                self.lineEdit_4_rutestuedi.text(),
                self.lineEdit_5_idcolegioestuedi.text(),
                self.lineEdit_14_idestuedi.text()  # ID para el WHERE
            )
            if not all(datos):
                QMessageBox.warning(self, "Campos Vacíos", "Por favor, complete todos los campos para editar.")
                return
            
            with self.connection.cursor() as cursor:
                cursor.execute("UPDATE Estudiantes SET Nombre=%s, RUT=%s, ID_Colegio=%s WHERE ID_Estudiante=%s", datos)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Estudiante actualizado correctamente.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el estudiante: {e}")

    def borrar(self):
        if self.user_level != '03':
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para eliminar registros.")
            return
        
        id_estudiante = self.lineEdit_19_idestueli.text()
        if not id_estudiante:
            QMessageBox.warning(self, "ID Faltante", "Ingrese el ID del estudiante a borrar.")
            return

        # Aplicar el estilo al QMessageBox de confirmación
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle('Confirmar')
        msg_box.setText(f"¿Seguro que desea eliminar al estudiante {id_estudiante}? Se eliminarán todos sus seguros y reservas (incluyendo pagos y contratos).")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        # No se necesita setear styleSheet aquí si se hace globalmente en QApplication

        reply = msg_box.exec_()

        if reply == QMessageBox.No:
            return

        try:
            with self.connection.cursor() as cursor:
                # 1. Buscar todas las reservas asociadas al estudiante
                cursor.execute("SELECT ID_Reserva FROM Reservas WHERE ID_Estudiante = %s", (id_estudiante,))
                reservas_a_borrar = cursor.fetchall()
                
                # 2. Para cada reserva, borrar sus dependencias (Pagos, Contratos)
                if reservas_a_borrar:
                    for reserva in reservas_a_borrar:
                        reserva_id = reserva['ID_Reserva']
                        cursor.execute("DELETE FROM Pagos WHERE ID_Reserva = %s", (reserva_id,))
                        cursor.execute("DELETE FROM Contratos WHERE ID_Reserva = %s", (reserva_id,))
                
                # 3. Borrar las reservas del estudiante
                cursor.execute("DELETE FROM Reservas WHERE ID_Estudiante = %s", (id_estudiante,))
                
                # 4. Borrar los seguros del estudiante
                cursor.execute("DELETE FROM Seguros WHERE ID_Estudiante = %s", (id_estudiante,))
                
                # 5. Finalmente, borrar al estudiante
                cursor.execute(f"DELETE FROM {self.table_name} WHERE {self.id_column} = %s", (id_estudiante,))

            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Estudiante y todos sus datos asociados eliminados correctamente.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el estudiante: {e}")


# --- Implementación de las otras ventanas (Completas) ---

class VuelosWindow(BaseCrudWindow):
    def __init__(self, connection, user_level):
        super().__init__(connection, user_level)
        self.ui_file = 'vuelos.ui'
        self.table_name = 'Vuelos'
        self.id_column = 'ID_Vuelo'
        
        try:
            loadUi(resource_path(self.ui_file), self)
        except Exception as e:
            QMessageBox.critical(self, "Error de UI", f"No se pudo cargar el archivo de interfaz '{self.ui_file}'.\nError: {e}")
            return

        self.pushButton_visualvuelos.clicked.connect(self.cargar_datos)
        self.pushButton_4_vueload.clicked.connect(self.agregar)
        self.pushButton_3_vueloact.clicked.connect(self.editar)
        self.pushButton_2_vuelobo.clicked.connect(self.borrar)
        self.pushButton_vuelosvolver.clicked.connect(self.volver)

        self.setup_permissions(self.pushButton_4_vueload, self.pushButton_3_vueloact, self.pushButton_2_vuelobo)
        self.cargar_datos()

    def cargar_datos(self):
        self.cargar_datos_base(self.table_name, self.tableWidget_cliente)

    def agregar(self):
        if self.user_level not in ['02', '03']:
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para añadir registros.")
            return
        
        try:
            # ID automático
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT MAX(ID_Vuelo) AS max_id FROM Vuelos")
                result = cursor.fetchone()
                next_id = (result['max_id'] or 0) + 1

            datos = (
                next_id,
                self.lineEdit_8_vueloidviajeag.text(),
                self.lineEdit_vueloaeroag.text(),
                self.lineEdit_2_vuelonumag.text()
            )
            if not all(datos[1:]):
                QMessageBox.warning(self, "Campos Vacíos", "Por favor, complete todos los campos para agregar.")
                return

            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO Vuelos (ID_Vuelo, ID_Viaje, Aerolinea, Numero_Vuelo) VALUES (%s, %s, %s, %s)", datos)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", f"Vuelo añadido correctamente con ID {next_id}.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo añadir el vuelo: {e}")

    def editar(self):
        if self.user_level not in ['02', '03']:
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para editar registros.")
            return
        
        try:
            datos = (
                self.lineEdit_3_idviajeed.text(),
                self.lineEdit_4_aerovueloed.text(),
                self.lineEdit_5_numvueloed.text(),
                self.lineEdit_14_idvueloed.text()
            )
            if not all(datos):
                QMessageBox.warning(self, "Campos Vacíos", "Por favor, complete todos los campos para editar.")
                return
            
            with self.connection.cursor() as cursor:
                cursor.execute("UPDATE Vuelos SET ID_Viaje=%s, Aerolinea=%s, Numero_Vuelo=%s WHERE ID_Vuelo=%s", datos)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Vuelo actualizado correctamente.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el vuelo: {e}")

    def borrar(self):
        if self.user_level != '03':
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para eliminar registros.")
            return
        
        id_valor = self.lineEdit_19_idvuelobo.text()
        if not id_valor:
            QMessageBox.warning(self, "ID Faltante", "Ingrese el ID del vuelo a borrar.")
            return

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle('Confirmar')
        msg_box.setText(f"¿Seguro que desea eliminar el vuelo {id_valor}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        reply = msg_box.exec_()

        if reply == QMessageBox.No:
            return

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {self.table_name} WHERE {self.id_column} = %s", (id_valor,))
            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Vuelo eliminado correctamente.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")

class ViajesWindow(BaseCrudWindow):
    def __init__(self, connection, user_level):
        super().__init__(connection, user_level)
        self.ui_file = 'viajes.ui'
        self.table_name = 'Viajes'
        self.id_column = 'ID_Viaje'
        
        try:
            loadUi(resource_path(self.ui_file), self)
        except Exception as e:
            QMessageBox.critical(self, "Error de UI", f"No se pudo cargar el archivo de interfaz '{self.ui_file}'.\nError: {e}")
            return

        self.pushButton_visualviaje.clicked.connect(self.cargar_datos)
        self.pushButton_4_viajead.clicked.connect(self.agregar)
        self.pushButton_3_viajeaact.clicked.connect(self.editar)
        self.pushButton_2_viajeeli.clicked.connect(self.borrar)
        self.pushButton_viajevolver.clicked.connect(self.volver)

        self.setup_permissions(self.pushButton_4_viajead, self.pushButton_3_viajeaact, self.pushButton_2_viajeeli)
        self.cargar_datos()

    def cargar_datos(self):
        self.cargar_datos_base(self.table_name, self.tableWidget_cliente)

    def agregar(self):
        if self.user_level not in ['02', '03']:
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para añadir registros.")
            return
        
        try:
            # ID automático
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT MAX(ID_Viaje) AS max_id FROM Viajes")
                result = cursor.fetchone()
                next_id = (result['max_id'] or 0) + 1

            datos = (
                next_id,
                self.lineEdit_9_destinoviajead.text(),
                self.lineEdit_fechasalviajead.text() or None,
                self.lineEdit_2_fecharetorviajead.text() or None,
                self.lineEdit_8_idcolegioviajead.text(),
                self.lineEdit_9_idcoorviajead.text()
            )
            if not all([datos[1], datos[2], datos[4], datos[5]]):
                QMessageBox.warning(self, "Campos Vacíos", "Destino, Fecha Salida, ID Colegio e ID Coordinador son obligatorios.")
                return

            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO Viajes (ID_Viaje, Destino, Fecha_Salida, Fecha_Retorno, ID_Colegio, ID_Coordinador) VALUES (%s, %s, %s, %s, %s, %s)", datos)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", f"Viaje añadido correctamente con ID {next_id}.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo añadir el viaje: {e}")

    def editar(self):
        if self.user_level not in ['02', '03']:
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para editar registros.")
            return
        
        try:
            datos = (
                self.lineEdit_3_destinoviajeedi.text(),
                self.lineEdit_4_fechasalviajeedi.text() or None,
                self.lineEdit_5_fecharetviajeedi.text() or None,
                self.lineEdit_6_idcolegioviajeedi.text(),
                self.lineEdit_7_idcoorviajeedi.text(),
                self.lineEdit_14_idviajeedi.text()
            )
            if not all(datos):
                QMessageBox.warning(self, "Campos Vacíos", "Por favor, complete todos los campos para editar.")
                return
            
            with self.connection.cursor() as cursor:
                cursor.execute("UPDATE Viajes SET Destino=%s, Fecha_Salida=%s, Fecha_Retorno=%s, ID_Colegio=%s, ID_Coordinador=%s WHERE ID_Viaje=%s", datos)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Viaje actualizado correctamente.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el viaje: {e}")

    def borrar(self):
        if self.user_level != '03':
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para eliminar registros.")
            return
        
        id_viaje = self.lineEdit_19_idviajeeli.text()
        if not id_viaje:
            QMessageBox.warning(self, "ID Faltante", "Ingrese el ID del viaje a borrar.")
            return

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle('Confirmar')
        msg_box.setText(f"¿Seguro que desea eliminar el viaje {id_viaje}? Se eliminarán todos los vuelos y reservas asociados.")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        reply = msg_box.exec_()

        if reply == QMessageBox.No:
            return

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT ID_Reserva FROM Reservas WHERE ID_Viaje = %s", (id_viaje,))
                reservas_a_borrar = cursor.fetchall()
                
                if reservas_a_borrar:
                    for reserva in reservas_a_borrar:
                        reserva_id = reserva['ID_Reserva']
                        cursor.execute("DELETE FROM Pagos WHERE ID_Reserva = %s", (reserva_id,))
                        cursor.execute("DELETE FROM Contratos WHERE ID_Reserva = %s", (reserva_id,))
                
                cursor.execute("DELETE FROM Reservas WHERE ID_Viaje = %s", (id_viaje,))
                cursor.execute("DELETE FROM Vuelos WHERE ID_Viaje = %s", (id_viaje,))
                cursor.execute(f"DELETE FROM {self.table_name} WHERE {self.id_column} = %s", (id_viaje,))

            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Viaje y todos sus datos asociados eliminados correctamente.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el viaje: {e}")

class ReservasWindow(BaseCrudWindow):
    def __init__(self, connection, user_level):
        super().__init__(connection, user_level)
        self.ui_file = 'reservas.ui'
        self.table_name = 'Reservas'
        self.id_column = 'ID_Reserva'
        
        try:
            loadUi(resource_path(self.ui_file), self)
        except Exception as e:
            QMessageBox.critical(self, "Error de UI", f"No se pudo cargar el archivo de interfaz '{self.ui_file}'.\nError: {e}")
            return

        self.pushButton_visualreserva.clicked.connect(self.cargar_datos)
        self.pushButton_4_reservaadd.clicked.connect(self.agregar)
        self.pushButton_3_reservaact.clicked.connect(self.editar)
        self.pushButton_2_reserborrar.clicked.connect(self.borrar)
        self.pushButton_reservasvolver.clicked.connect(self.volver)

        self.setup_permissions(self.pushButton_4_reservaadd, self.pushButton_3_reservaact, self.pushButton_2_reserborrar)
        self.cargar_datos()

    def cargar_datos(self):
        self.cargar_datos_base(self.table_name, self.tableWidget_cliente)

    def agregar(self):
        if self.user_level not in ['02', '03']:
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para añadir registros.")
            return
        
        try:
            # ID automático
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT MAX(ID_Reserva) AS max_id FROM Reservas")
                result = cursor.fetchone()
                next_id = (result['max_id'] or 0) + 1

            datos = (
                next_id,
                self.lineEdit_9_idestureseradd.text(),
                self.lineEdit_idviajereseradd.text(),
                self.lineEdit_2_estadoreseradd.text()
            )
            if not all(datos[1:]):
                QMessageBox.warning(self, "Campos Vacíos", "Todos los campos son obligatorios para agregar una reserva.")
                return

            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO Reservas (ID_Reserva, ID_Estudiante, ID_Viaje, Estado) VALUES (%s, %s, %s, %s)", datos)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", f"Reserva añadida correctamente con ID {next_id}.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo añadir la reserva: {e}")

    def editar(self):
        if self.user_level not in ['02', '03']:
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para editar registros.")
            return
        
        try:
            datos = (
                self.lineEdit_3_idestureseredi.text(),
                self.lineEdit_4_idviajereseredi.text(),
                self.lineEdit_5_estadoviajeedi.text(),
                self.lineEdit_14_idreseredi.text()
            )
            if not all(datos):
                QMessageBox.warning(self, "Campos Vacíos", "Por favor, complete todos los campos para editar.")
                return
            
            with self.connection.cursor() as cursor:
                cursor.execute("UPDATE Reservas SET ID_Estudiante=%s, ID_Viaje=%s, Estado=%s WHERE ID_Reserva=%s", datos)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Reserva actualizada correctamente.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo actualizar la reserva: {e}")

    def borrar(self):
        if self.user_level != '03':
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para eliminar registros.")
            return
        
        id_reserva = self.lineEdit_19_idresereli.text()
        if not id_reserva:
            QMessageBox.warning(self, "ID Faltante", "Ingrese el ID de la reserva a borrar.")
            return

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle('Confirmar')
        msg_box.setText(f"¿Seguro que desea eliminar la reserva {id_reserva}? Se eliminarán todos los pagos y contratos asociados.")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        reply = msg_box.exec_()

        if reply == QMessageBox.No:
            return

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("DELETE FROM Pagos WHERE ID_Reserva = %s", (id_reserva,))
                cursor.execute("DELETE FROM Contratos WHERE ID_Reserva = %s", (id_reserva,))
                cursor.execute(f"DELETE FROM {self.table_name} WHERE {self.id_column} = %s", (id_reserva,))

            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Reserva y todos sus datos asociados eliminados correctamente.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo eliminar la reserva: {e}")

class CoordinadoresWindow(BaseCrudWindow):
    def __init__(self, connection, user_level):
        super().__init__(connection, user_level)
        self.ui_file = 'coordinadores.ui'
        self.table_name = 'Coordinadores'
        self.id_column = 'ID_Coordinador'
        
        try:
            loadUi(resource_path(self.ui_file), self)
        except Exception as e:
            QMessageBox.critical(self, "Error de UI", f"No se pudo cargar el archivo de interfaz '{self.ui_file}'.\nError: {e}")
            return

        self.pushButton_visualcoor.clicked.connect(self.cargar_datos)
        self.pushButton_4_cooradd.clicked.connect(self.agregar)
        self.pushButton_3_cooract.clicked.connect(self.editar)
        self.pushButton_2_coorborrar.clicked.connect(self.borrar)
        self.pushButton_coorvolver.clicked.connect(self.volver)

        self.setup_permissions(self.pushButton_4_cooradd, self.pushButton_3_cooract, self.pushButton_2_coorborrar)
        self.cargar_datos()

    def cargar_datos(self):
        self.cargar_datos_base(self.table_name, self.tableWidget_cliente)

    def agregar(self):
        if self.user_level not in ['02', '03']:
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para añadir registros.")
            return
        
        try:
            # ID automático
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT MAX(ID_Coordinador) AS max_id FROM Coordinadores")
                result = cursor.fetchone()
                next_id = (result['max_id'] or 0) + 1

            datos = (
                next_id,
                self.lineEdit_9_nombrecooradd.text(),
                self.lineEdit_cuidadcooradd.text(),
                self.lineEdit_2_contactocooradd.text()
            )
            if not all(datos[1:]):
                QMessageBox.warning(self, "Campos Vacíos", "Todos los campos son obligatorios para agregar un coordinador.")
                return

            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO Coordinadores (ID_Coordinador, Nombre, Telefono, Disponibilidad) VALUES (%s, %s, %s, %s)", datos)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", f"Coordinador añadido correctamente with ID {next_id}.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo añadir el coordinador: {e}")

    def editar(self):
        if self.user_level not in ['02', '03']:
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para editar registros.")
            return
        
        try:
            datos = (
                self.lineEdit_3_nombrecooredi.text(),
                self.lineEdit_4_cuidadcooredi.text(),
                self.lineEdit_5_contactocooredi.text(),
                self.lineEdit_14_idcooredi.text()
            )
            if not all(datos):
                QMessageBox.warning(self, "Campos Vacíos", "Por favor, complete todos los campos para editar.")
                return
            
            with self.connection.cursor() as cursor:
                # Corrected column order for UPDATE statement
                cursor.execute("UPDATE Coordinadores SET Nombre=%s, Telefono=%s, Disponibilidad=%s WHERE ID_Coordinador=%s", datos)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Coordinador actualizado correctamente.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el coordinador: {e}")

    def borrar(self):
        if self.user_level != '03':
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para eliminar registros.")
            return
        
        id_coordinador = self.lineEdit_19_idcoorborrar.text()
        if not id_coordinador:
            QMessageBox.warning(self, "ID Faltante", "Ingrese el ID del coordinador a borrar.")
            return

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle('Confirmar')
        msg_box.setText(f"¿Seguro que desea eliminar al coordinador {id_coordinador}? Se eliminarán todos los viajes (y sus reservas, pagos, etc.) asociados a este coordinador.")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        reply = msg_box.exec_()

        if reply == QMessageBox.No:
            return

        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT ID_Viaje FROM Viajes WHERE ID_Coordinador = %s", (id_coordinador,))
                viajes_a_borrar = cursor.fetchall()

                if viajes_a_borrar:
                    for viaje in viajes_a_borrar:
                        viaje_id = viaje['ID_Viaje']
                        cursor.execute("SELECT ID_Reserva FROM Reservas WHERE ID_Viaje = %s", (viaje_id,))
                        reservas_a_borrar = cursor.fetchall()
                        if reservas_a_borrar:
                            for reserva in reservas_a_borrar:
                                reserva_id = reserva['ID_Reserva']
                                cursor.execute("DELETE FROM Pagos WHERE ID_Reserva = %s", (reserva_id,))
                                cursor.execute("DELETE FROM Contratos WHERE ID_Reserva = %s", (reserva_id,))
                        cursor.execute("DELETE FROM Reservas WHERE ID_Viaje = %s", (viaje_id,))
                        cursor.execute("DELETE FROM Vuelos WHERE ID_Viaje = %s", (viaje_id,))
                
                cursor.execute("DELETE FROM Viajes WHERE ID_Coordinador = %s", (id_coordinador,))
                cursor.execute(f"DELETE FROM {self.table_name} WHERE {self.id_column} = %s", (id_coordinador,))

            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Coordinador y todos sus datos asociados eliminados correctamente.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el coordinador: {e}")

class SegurosWindow(BaseCrudWindow):
    def __init__(self, connection, user_level):
        super().__init__(connection, user_level)
        self.ui_file = 'seguros.ui'
        self.table_name = 'Seguros'
        self.id_column = 'ID_Seguro'
        
        try:
            loadUi(resource_path(self.ui_file), self)
        except Exception as e:
            QMessageBox.critical(self, "Error de UI", f"No se pudo cargar el archivo de interfaz '{self.ui_file}'.\nError: {e}")
            return

        self.pushButton_visualseg.clicked.connect(self.cargar_datos)
        self.pushButton_4_segadd.clicked.connect(self.agregar)
        self.pushButton_3_segact.clicked.connect(self.editar)
        self.pushButton_2_segborrar.clicked.connect(self.borrar)
        self.pushButton_segvolver.clicked.connect(self.volver)

        self.setup_permissions(self.pushButton_4_segadd, self.pushButton_3_segact, self.pushButton_2_segborrar)
        self.cargar_datos()

    def cargar_datos(self):
        self.cargar_datos_base(self.table_name, self.tableWidget_cliente)

    def agregar(self):
        if self.user_level not in ['02', '03']:
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para añadir registros.")
            return
        
        try:
            # ID automático
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT MAX(ID_Seguro) AS max_id FROM Seguros")
                result = cursor.fetchone()
                next_id = (result['max_id'] or 0) + 1

            datos = (
                next_id,
                self.lineEdit_9_idestusegadd.text(),
                self.lineEdit_proveesegadd.text(),
                self.lineEdit_cobersegadd.text()
            )
            if not all(datos[1:]):
                QMessageBox.warning(self, "Campos Vacíos", "Todos los campos son obligatorios para agregar un seguro.")
                return

            with self.connection.cursor() as cursor:
                cursor.execute("INSERT INTO Seguros (ID_Seguro, ID_Estudiante, Proveedor, Cobertura) VALUES (%s, %s, %s, %s)", datos)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", f"Seguro añadido correctamente con ID {next_id}.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo añadir el seguro: {e}")

    def editar(self):
        if self.user_level not in ['02', '03']:
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para editar registros.")
            return
        
        try:
            datos = (
                self.lineEdit_3_idestusegedi.text(),
                self.lineEdit_4_proveesegedi.text(),
                self.lineEdit_5_cobersegedi.text(),
                self.lineEdit_14_idsegedi.text()
            )
            if not all(datos):
                QMessageBox.warning(self, "Campos Vacíos", "Por favor, complete todos los campos para editar.")
                return
            
            with self.connection.cursor() as cursor:
                cursor.execute("UPDATE Seguros SET ID_Estudiante=%s, Proveedor=%s, Cobertura=%s WHERE ID_Seguro=%s", datos)
            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Seguro actualizado correctamente.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el seguro: {e}")

    def borrar(self):
        if self.user_level != '03':
            QMessageBox.warning(self, "Acceso Denegado", "No tiene permiso para eliminar registros.")
            return
        
        id_seguro = self.lineEdit_19_idsegeli.text()
        if not id_seguro:
            QMessageBox.warning(self, "ID Faltante", "Ingrese el ID del seguro a borrar.")
            return

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle('Confirmar')
        msg_box.setText(f"¿Seguro que desea eliminar el seguro {id_seguro}?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        reply = msg_box.exec_()

        if reply == QMessageBox.No:
            return

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {self.table_name} WHERE {self.id_column} = %s", (id_seguro,))
            self.connection.commit()
            QMessageBox.information(self, "Éxito", "Seguro eliminado correctamente.")
            self.cargar_datos()
        except Exception as e:
            self.connection.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el seguro: {e}")

class AdvertenciaOrdenWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advertencia de Orden de Ingreso de Datos")
        self.setGeometry(300, 300, 350, 250)
        layout = QVBoxLayout()
        label = QLabel(
            "<b>¡Atención!</b><br><br>"
            "Para evitar errores de integridad en la base de datos, agregue los datos en el siguiente orden:<br><br>"
            "1) Coordinadores<br>"
            "2) Estudiantes<br>"
            "3) Seguros<br>"
            "4) Viajes<br>"
            "5) Reservas<br>"
            "6) Vuelos<br><br>"
            "<i>Esta ventana puede permanecer abierta mientras trabaja.</i>"
        )
        label.setWordWrap(True)
        layout.addWidget(label)
        self.setLayout(layout)

def registrar_error(connection):
    hoy = datetime.date.today()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT Cantidad FROM ErroresPorDia WHERE Fecha = %s", (hoy,))
            resultado = cursor.fetchone()
            if resultado:
                cursor.execute("UPDATE ErroresPorDia SET Cantidad = Cantidad + 1 WHERE Fecha = %s", (hoy,))
            else:
                cursor.execute("INSERT INTO ErroresPorDia (Fecha, Cantidad) VALUES (%s, 1)", (hoy,))
        connection.commit()
    except Exception as e:
        # Si falla el registro del error, solo imprime (no mostrar otro QMessageBox para evitar bucles)
        print(f"Error registrando error: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # ***** CAMBIO CLAVE AQUÍ: Aplicar styleSheet a QApplication para QMessageBox *****
    app.setStyleSheet("""
        QMessageBox {
            background-color: #333333; /* Fondo gris oscuro para el QMessageBox */
            color: white; /* Color de texto predeterminado */
            border: 1px solid #FFA500; /* Borde naranja */
            font-size: 10pt; /* Tamaño de fuente, ajusta si es necesario */
        }
        QMessageBox QLabel { /* Estilo para el texto del mensaje dentro del QMessageBox */
            color: white; /* Texto blanco para el mensaje */
            background-color: #333333; /* Asegura que el fondo del QLabel sea el mismo */
            padding: 5px; /* Pequeño padding alrededor del texto */
        }
        QMessageBox QPushButton { /* Estilo para los botones del QMessageBox */
            background-color: #FF692E; /* Naranja */
            color: white;
            border-radius: 5px;
            padding: 5px 10px;
            min-width: 80px; /* Ancho mínimo para los botones */
            min-height: 25px; /* Altura mínima para los botones */
        }
        QMessageBox QPushButton:hover {
            background-color: #FF8C4B; /* Naranja más claro al pasar el ratón */
        }
        QMessageBox QPushButton:pressed {
            background-color: #CD5721; /* Naranja más oscuro al presionar */
        }
        /* Opcional: Estilo para los iconos de QMessageBox */
        QMessageBox QLabel[pixmap="true"] {
            background-color: transparent; /* No aplicar fondo al icono */
            margin: 5px;
        }
    """)
    # ***** FIN DEL CAMBIO CLAVE *****

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())