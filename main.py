import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *


# Motor de busca do Navegador
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl('https://duckduckgo.com/'))
        self.setCentralWidget(self.browser)
        self.showMaximized()

        navbar = QToolBar()
        self.addToolBar(navbar)

        # botão para voltar o URL
        back_btn = QAction('Voltar', self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)
        back_btn.setIcon(QIcon('./images/voltar.png'))

        # botão para avançar o URL
        forward_btn = QAction('Avançar', self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)
        forward_btn.setIcon(QIcon('./images/avançar.png'))

        # botão para recarregar F5
        reload_btn = QAction('Recarregar', self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)
        reload_btn.setIcon(QIcon('./images/f5.png'))

        # botão para ir para a home page
        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)
        home_btn.setIcon(QIcon('./images/home.png'))

        # barra de endereço
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)
        self.browser.urlChanged.connect(self.update_url)

    # link da página de início [Meu Portfólio]
    def navigate_home(self):
        self.browser.setUrl(QUrl('https://raphael-laurentino.netlify.app/index.html'))

    def navigate_to_url(self):
        url = self.url_bar.text()
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())


app = QApplication(sys.argv)
QApplication.setApplicationName('Via Expressa Browser')
window = MainWindow()
app.exec_()

# application = QApplication([])
# mainWindow = QMainWindow()
# mainWindow.setGeometry('0, 0, 1600, 900')
# mainWindow.setMinimumHeight(900)
# mainWindow.setMaximumHeight(900)
# mainWindow.setMinimumWidth(1600)
# mainWindow.setMaximumWidth(1600)
# mainWindow.setStyleSheet("background-color: rgb(0, 0, 0);")


# web = QWebEngineView(mainWindow)
# web.setGeometry('0, 0, 1600, 900')
# mainWindow.setStyleSheet("background-color: rgb(255, 255, 255);")

# home_button = QToolButton(mainWindow)
# home_button.setGeometry('0, 80, 30, 30')
# home_button_icon = QIcon()
# home_button.icon.addPixmap(QPixmap('home.png'), QIcon.Normal, QIcon.Off)
# home_button.setIcon(home_button_icon)

# mainWindow.setWindowTitle('Sactun Browser')

# mainWindow.show()
# application.exec_()

# app = QApplication(sys.argv)
# QApplication.setApplicationName('Sactun Browser')
# window = MainWindow()
# app.exec_()




# versão Browser Sacturno V0.0.0.1 Alpha