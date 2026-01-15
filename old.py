import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import *

# Classe para cada aba do navegador
class BrowserTab(QWebEngineView):
    def __init__(self, parent=None):
        super(BrowserTab, self).__init__(parent)

        # Configurar para aceitar todos os tipos de vídeo e plugins
        self.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.AutoLoadImages, True)
        self.settings().setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)

        # Aceitar arquivos de vídeo como .mp4 e outros
        self.page().setFeaturePermission(self.url(), QWebEnginePage.MediaAudioVideoCapture, QWebEnginePage.PermissionGrantedByUser)

# Classe principal do navegador
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Interface de Gerenciamento de Abas
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        # Adicionar widget de abas à janela principal
        self.setCentralWidget(self.tabs)
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Barra de navegação
        navbar = QToolBar("Navegação")
        self.addToolBar(navbar)

        # Botão de voltar
        back_btn = QAction(QIcon('images/voltar.png'), 'Voltar', self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        navbar.addAction(back_btn)

        # Botão de avançar
        forward_btn = QAction(QIcon('images/avançar.png'), 'Avançar', self)
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navbar.addAction(forward_btn)

        # Botão de recarregar
        reload_btn = QAction(QIcon('images/f5.png'), 'Recarregar', self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navbar.addAction(reload_btn)

        # Botão de ir para a página inicial
        home_btn = QAction(QIcon('images/home.png'), 'Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        # Campo de URL
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # Botão verde para adicionar uma nova aba
        new_tab_btn = QAction(QIcon('images/green_new_tab.png'), 'Nova Aba', self)
        new_tab_btn.triggered.connect(lambda _: self.add_new_tab())
        navbar.addAction(new_tab_btn)

        # Histórico de Navegação
        history_btn = QAction(QIcon('images/history.png'), 'Histórico', self)
        history_btn.triggered.connect(self.show_history)
        navbar.addAction(history_btn)

        # Configurações da janela
        self.setWindowTitle("Navegador Saturno")
        self.showMaximized()

        # Criar a primeira aba
        self.add_new_tab(QUrl('https://duckduckgo.com/'), 'Home')
        
        # Método para adicionar uma nova aba ao navegador
    def add_new_tab(self, qurl=None, label="Nova Aba"):
        if qurl is None:
            qurl = QUrl('https://duckduckgo.com/')

        browser = BrowserTab()
        browser.setUrl(qurl)

        index = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(index)

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=index, browser=browser: self.tabs.setTabText(i, browser.page().title()))

    # Abrir uma nova aba ao clicar duas vezes
    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    # Fechar a aba atual e criar uma nova aba em branco se for a última
    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            self.add_new_tab(QUrl('https://duckduckgo.com/'), 'Nova Aba')
        self.tabs.removeTab(i)

    # Atualizar a URL quando a aba atual muda
    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    # Atualizar o título da aba
    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle(f"{title} - Navegador Saturno")

    # Atualizar a barra de URL quando a página mudar
    def update_urlbar(self, qurl, browser=None):
        if browser != self.tabs.currentWidget():
            return

        self.url_bar.setText(qurl.toString())
        self.url_bar.setCursorPosition(0)

    # Navegar para a URL especificada
    def navigate_to_url(self):
        qurl = QUrl(self.url_bar.text())
        if self.tabs.currentWidget():
            self.tabs.currentWidget().setUrl(qurl)

    # Navegar para a página inicial
    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl('https://raphael-laurentino.netlify.app/index.html'))

    # Exibir Histórico de Navegação
    def show_history(self):
        history_window = QDialog(self)
        history_window.setWindowTitle("Histórico de Navegação")
        history_layout = QVBoxLayout()

        for i in range(self.tabs.count()):
            history = self.tabs.widget(i).history()
            for entry in history.items():
                history_layout.addWidget(QLabel(entry.url().toString()))

        history_window.setLayout(history_layout)
        history_window.exec_()

# Executar a aplicação
app = QApplication(sys.argv)
QApplication.setApplicationName('Navegador Saturno')

# Definindo o ícone da aplicação
app.setWindowIcon(QIcon('images/icone.png'))

window = MainWindow()
window.setWindowIcon(QIcon('images/icone.png'))  # Define o ícone da janela principal
app.exec_()

