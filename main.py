import metodos
import sys
import var
from Ui_MainWindow import *
from VentanaSalir import *
from dymond_game import game


def lanzar_juego():
    jugador = str(var.ui.lblJugador.text())
    conf = metodos.recoger_configuracion()
    juego = game.Game(jugador, conf)
    juego.run()


class DialogSalir(QtWidgets.QDialog):
    def __init__(self):
        super(DialogSalir, self).__init__()
        var.avisoSalir = Ui_DialogAvisoSalir()
        var.avisoSalir.setupUi(self)
        var.avisoSalir.buttonBoxSalir.button(QtWidgets.QDialogButtonBox.Yes).clicked.connect(metodos.salir)


class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super(Main, self).__init__()

        var.ui = Ui_MainWindow()
        var.ui.setupUi(self)
        var.avisoSalir = DialogSalir()

        ''' CARGAR COMBOBOX '''
        metodos.cargar_cmb_res()

        ''' BOTONES '''
        var.ui.btnCargarJugador.clicked.connect(metodos.cargar_jugadores)

        var.ui.btnEmpezar.clicked.connect(cerrar_ventana)
        var.ui.btnEmpezar.clicked.connect(metodos.lanzar_juego)

        var.ui.btnCargarJugador.clicked.connect(metodos.mostrar_nombre_jugadores)
        var.ui.btnBuscar.clicked.connect(metodos.mostrar_jugador_tabla)
        var.ui.btnRecargar.clicked.connect(metodos.mostrar_nombre_jugadores)
        var.ui.btnSalir.clicked.connect(metodos.salir)
        var.ui.btnGuardarCambios.clicked.connect(metodos.guardar_config)

        ''' CARGAR CONFIGURACION JSON '''
        metodos.cargar_config()

        ''' CONEXIÓN BBDD '''
        metodos.conexion_base_de_datos(var.archivoDB)

        ''' MOSTRAR DATOS EN LA TABLA '''
        metodos.mostrar_nombre_jugadores()
        var.ui.tablaJugadores.clicked.connect(metodos.seleccion_jugador)
        var.ui.tablaJugadores.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)


def cerrar_ventana():
    var.window.hide()


def abrir_ventana():
    var.window.showNormal()


if __name__ == '__main__':
    qapp = QtWidgets.QApplication([])
    var.window = Main()
    var.window.setWindowTitle("Black Dyamonds")
    var.window.showNormal()
    sys.exit(qapp.exec())
