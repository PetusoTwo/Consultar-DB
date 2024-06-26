from PyQt6.QtWidgets import QMainWindow, QApplication, QGraphicsDropShadowEffect, QFileDialog, QSizeGrip
from PyQt6.uic import loadUi
from PyQt6.QtCore import QPoint, Qt, QByteArray, QIODevice, QBuffer
from PyQt6.QtGui import QImage, QPixmap, QColor, QIntValidator
import sys
import sqlite3
import PyQt6 

class Formulario(QMainWindow):
    def __init__(self):
        super(Formulario, self).__init__()
        loadUi("design.ui", self)
        #loadUi("init.ui", self)
        self.conexion = sqlite3.connect("base_datos.db")
        
        self.btn_normal.hide()
        self.click_position = QPoint()
        self.btn_minimize.clicked.connect(lambda: self.showMinimized())
        self.btn_normal.clicked.connect(self.control_btn_normal)
        self.btn_close.clicked.connect(lambda: self.close())
        
        # Eliminar la barra de titulo y la opacidad
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowOpacity(1)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Sizegrip
        self.gripSize = 10
        self.grip = QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)
        
        # Mover ventana
        self.frame_superior.mousePressEvent = self.click_ventana
        self.frame_superior.mouseMoveEvent = self.mover_ventana
        
        # Botones
        self.btn_importar_img.clicked.connect(self.load_image)
        self.btn_limpiar.clicked.connect(self.clear_data)
        self.btn_guardar.clicked.connect(self.save_data)
        self.btn_buscar.clicked.connect(self.search_data)
        
        self.shadow_frame(self.frame_datos)
        self.shadow_frame(self.frame_buscar)
        self.in_telefono.setValidator(QIntValidator())
    
    def shadow_frame(self, frame):
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setOffset(5, 5)
        shadow.setColor(QColor(7, 0, 0, 60))
        frame.setGraphicsEffect(shadow)
            
    def load_image(self):
        filename = QFileDialog.getOpenFileName(self, filter="Image Files (*.png *.jpg *.jpeg *.bmp)")[0]
        if filename:
            pixmapImagen = QPixmap(filename).scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.img_preview.setPixmap(pixmapImagen)
                
    def clear_data(self):
        self.in_nombre.clear()
        self.in_telefono.clear()
        self.in_correo.clear()
        self.img_preview.clear()
            
    def save_data(self):
        nombre = self.in_nombre.text()
        telefono = self.in_telefono.text()
        correo = self.in_correo.text()
        foto = self.img_preview.pixmap()
        # Convertir la imagen en bytes
        if foto:
            bArray = QByteArray()
            buff = QBuffer(bArray)
            buff.open(QIODevice.OpenModeFlag.ReadWrite)
            foto.save(buff, "PNG")
                
        cursor = self.conexion.cursor()
        if cursor.execute("SELECT * FROM datos WHERE NOMBRE = ?", (nombre,)).fetchone():
            self.img_preview.setText("Registro ya existente")
        elif len(nombre) <= 4:
            self.img_preview.setText("El nombre es demasiado corto")
        elif len(telefono) <= 3:
            self.img_preview.setText("El teléfono es demasiado corto")
        elif len(correo) <= 4:
            self.img_preview.setText("El correo es demasiado corto")
        elif foto:
            cursor.execute("INSERT INTO datos VALUES (?, ?, ?, ?)", (nombre, telefono, correo, bArray))
            self.conexion.commit()
            cursor.close()
            self.clear_data()
        else:
            self.img_preview.setText("Por favor cargue una imagen")
                
    def search_data(self):
        nombre_a_buscar = self.in_buscar_nombre.text()
        # Obtener datos de SQLite3
        cursor = self.conexion.cursor()
        cursor.execute("SELECT * FROM datos WHERE NOMBRE = ?", (nombre_a_buscar,))
        nombrex = cursor.fetchall()
        cursor.close()
        if nombrex:
            self.telefono.setText(f'Correo: {nombrex[0][1]}')
            self.correo.setText(f'Telefono: {nombrex[0][2]}')
            foto = QPixmap()
            foto.loadFromData(nombrex[0][3])
            self.imagen.setPixmap(foto)
        else:
            self.telefono.setText("Correo:  No existente")
            self.correo.setText("Telefono: No existente")
            self.imagen.clear()
                
    def control_btn_normal(self):
        self.showNormal()
        self.btn_normal.hide()
        self.btn_minimize.show()
            
    def control_btn_minimize(self):
        self.showMinimized()
        self.btn_normal.show()
        self.btn_minimize.hide()
    
    def click_ventana(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.click_position = event.globalPosition().toPoint()
    
    def mover_ventana(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(self.pos() + event.globalPosition().toPoint() - self.click_position)
            self.click_position = event.globalPosition().toPoint()
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_app = Formulario()
    my_app.show()
    sys.exit(app.exec())
