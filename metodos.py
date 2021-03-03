import json
import time

from PyQt5 import QtSql

from main import *


def conexion_base_de_datos(name):
    """

    Nos conectamos a la BBDD. Para ello, recibimos el nombre de la misma.

    :param name: name
    :type name: String
    :return: True or False
    :rtype: Boolean
    """
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(name)
    if not db.open():
        QtWidgets.QMessageBox.Critical(None, 'No se puede abrir la base de datos',
                                       'No se puede establecer la conexión. \n'
                                       'Haz Click para Cancelar.', QtWidgets.QMessageBox.Cancel)
        print('Error conexion')
        return False
    else:
        print('Conexion bien')
    return True


def cargar_jugadores():
    """

    Añadimos un nuevo jugador a la BBDD.
    Seleccionamos el nombre del editText, le quitamos todos los espacios en blanco que tenga
    y lo añadimos si el nombre, aún no está registrado.

    """
    nombre_jugador = var.ui.editNombre.text().replace(' ', '')

    if nombre_jugador == '':
        print('Nombre del jugador vacio')
    else:
        query = QtSql.QSqlQuery()
        query.prepare('insert into Jugadores (nombre, puntos, nivel, fecha)'
                      'VALUES (:nombre, :puntos, :nivel, :fecha)')
        query.bindValue(':nombre', str(nombre_jugador))
        query.bindValue(':puntos', 0)
        query.bindValue(':nivel', 0)
        query.bindValue(':fecha', str(time.strftime("%d/%m/%y"+" - "+"%H:%M")))


        if query.exec_():
            print('Insercción Correcta')
        else:
            print('Error alta jugadores:', query.lastError().text())
        var.ui.editNombre.setText('')


def modificar_jugador(nombre, puntos, nivel):
    """
    Metodo que modifica los datos del jugador.
    La fecha se modifica automáticamente (usa la del sistema)

    :param nombre: str
    :param puntos: int
    :param nivel: int
    """
    if nombre != '':
        query = QtSql.QSqlQuery()
        query.prepare('update Jugadores set puntos=:puntos, nivel=:nivel, fecha=:fecha where nombre=:nombre')

        query.bindValue(':nombre', str(nombre))
        query.bindValue(':puntos', int(puntos))
        query.bindValue(':nivel', int(nivel))
        query.bindValue(':fecha', str(time.strftime("%d/%m/%y"+" - "+"%H:%M")))

        if query.exec_():
            mostrar_nombre_jugadores()
            print('Update Correcto')
        else:
            print('Error modificar jugadores:', query.lastError().text())

def buscar_jugador_nombre(nombre):
    """

    Recibimos el nombre del jugador y lo buscamos en la base de datos para retornar todos sus datos.

    :param nombre: str
    :return: datos or None
    :rtype: Diccionario
    """
    if nombre != '':
        query = QtSql.QSqlQuery()
        query.prepare('select * from Jugadores where nombre = :nombreJugador')
        query.bindValue(':nombreJugador', str(nombre))
        if query.exec_():
            if query.next():
                datos = ({'nombre': query.value(0), 'puntos': query.value(1), 'nivel': query.value(2),
                          'fecha': query.value(3)})
                return datos
        else:
            return None


def mostrar_jugador_tabla():

    """

    Método que cuando buscamos a un jugador, nos muestra sus datos.

    """

    nombre = var.ui.editNombre.text()
    datos = buscar_jugador_nombre(nombre)

    try:
        if datos is None:
            print('Error buscar jugador')
        else:
            var.ui.tablaJugadores.setRowCount(1)
            var.ui.tablaJugadores.setItem(0, 0, QtWidgets.QTableWidgetItem(str(datos['nombre'])))
            var.ui.tablaJugadores.setItem(0, 1, QtWidgets.QTableWidgetItem(str(datos['puntos'])))
            var.ui.tablaJugadores.setItem(0, 2, QtWidgets.QTableWidgetItem(str(datos['nivel'])))
            var.ui.tablaJugadores.setItem(0, 3, QtWidgets.QTableWidgetItem(str(datos['fecha'])))
            var.ui.tablaJugadores.item(0, 0).setTextAlignment(QtCore.Qt.AlignCenter)
            var.ui.tablaJugadores.item(0, 1).setTextAlignment(QtCore.Qt.AlignCenter)
            var.ui.tablaJugadores.item(0, 2).setTextAlignment(QtCore.Qt.AlignCenter)
            var.ui.tablaJugadores.item(0, 3).setTextAlignment(QtCore.Qt.AlignCenter)
    except Exception as error:
        print('Erro buscar jugador : ' + str(error))


def mostrar_nombre_jugadores():

    """

    Método para mostrar todos los jugadores que hay en la BBDD

    """

    index = 0
    query = QtSql.QSqlQuery()
    query.prepare('select * from Jugadores order by puntos desc')
    if query.exec_():
        while query.next():
            nombre = str(query.value(0))
            puntos = str(query.value(1))
            nivel = str(query.value(2))
            fecha = str(query.value(3))

            var.ui.tablaJugadores.setRowCount(index + 1)

            var.ui.tablaJugadores.setItem(index, 0, QtWidgets.QTableWidgetItem(nombre))
            var.ui.tablaJugadores.setItem(index, 1, QtWidgets.QTableWidgetItem(puntos))
            var.ui.tablaJugadores.setItem(index, 2, QtWidgets.QTableWidgetItem(nivel))
            var.ui.tablaJugadores.setItem(index, 3, QtWidgets.QTableWidgetItem(fecha))
            var.ui.tablaJugadores.item(index, 0).setTextAlignment(QtCore.Qt.AlignCenter)
            var.ui.tablaJugadores.item(index, 1).setTextAlignment(QtCore.Qt.AlignCenter)
            var.ui.tablaJugadores.item(index, 2).setTextAlignment(QtCore.Qt.AlignCenter)
            var.ui.tablaJugadores.item(index, 3).setTextAlignment(QtCore.Qt.AlignCenter)
            index += 1
    else:
        print('Error en mostrar los jugadores')


def seleccion_jugador():
    """

    Método que cuando hacemos click en un jugador de la tabla, nos carga su nombre en un label.

    Como hemos hecho click en un jugador, el botón de empezar pasa a estar disponible.

    """
    try:
        fila = var.ui.tablaJugadores.selectedItems()
        if fila:
            fila = [dato.text() for dato in fila]
        var.ui.lblJugador.setText(str(fila[0]))

        var.ui.btnEmpezar.setEnabled(True)

    except Exception as error:
        print('Error al seleccionar jugador : ' + str(error))


def salir():
    """

    Método que llama a la ventana de aviso de salir.

    """
    try:
        var.avisoSalir.show()
        if var.avisoSalir.exec_():
            sys.exit()
        else:
            var.avisoSalir.hide()
    except Exception as error:
        print('Error %s' % str(error))


def recoger_configuracion():
    """

    Método que lee las opciones que escogió el usuario y devulve los datos.

    :return: configuracion
    :rtype: diccionario
    """
    try:

        opc_developer = var.ui.chkDeveloper.isChecked()
        mus_volume = round(var.ui.SliderMusica.value() * 0.01, 2)
        sfx_volume = round(var.ui.SliderEfectos.value() * 0.01, 2)

        texto_resolucion = str(var.ui.cmbResolucion.currentText()).split(' x ')
        valor_resolucion = [int(texto_resolucion[0]), int(texto_resolucion[1])]

        configuracion = {"resolucion": valor_resolucion, "mus_volume": mus_volume, "sfx_volume": sfx_volume,"debug_mode": opc_developer}

        return configuracion
    except Exception as error:
        print('Error cambioValor : ' + str(error))


def guardar_config():
    """

    Método que guarda los datos de configuración

    """
    datos = recoger_configuracion()

    j = open("config.json", 'w')
    json.dump(datos, j)
    j.close()


def cargar_config():
    """

    Método que carga los datos de configuración que han sido guardados previamente.

    """
    f = open("config.json", 'r')
    config = json.load(f)
    f.close()

    music_vol = config.get("mus_volume") * 100
    sfx_vol = config.get("sfx_volume") * 100
    resolucion = str(config.get("resolucion")[0]) + " x " + str(config.get("resolucion")[1])
    opc_developer = config.get("debug_mode")

    var.ui.SliderMusica.setValue(music_vol)
    var.ui.SliderEfectos.setValue(sfx_vol)
    var.ui.cmbResolucion.setCurrentText(resolucion)
    var.ui.chkDeveloper.setChecked(opc_developer)

def cargar_cmb_res():
    """

    Método que carga las resoluciones disponibles en el comboBox.

    """
    try:
        diccio_res = ['1920 x 1080', '1600 x 900', '1280 x 720', '854 x 480', '640 x 360', '480 x 270']
        for i in diccio_res:
            var.ui.cmbResolucion.addItem(i)

    except Exception as error:
        print('Error al cargar las resoluciones en el comboBox' + str(error))

