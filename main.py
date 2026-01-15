import sys
import os
import json
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

HISTORY_FILE = "history.json"
BOOKMARKS_FILE = "bookmarks.json"
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "images")

# =========================
# Utilidades
# =========================
def load_json(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # arquivo corrompido ou inválido — reescreve com default
            save_json(file, default)
            return default
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def get_asset_path(name: str) -> str:
    return os.path.join(ASSETS_DIR, name)


def get_icon(name: str) -> QIcon:
    path = get_asset_path(name)
    if os.path.exists(path):
        return QIcon(path)
    return QIcon()

# =========================
# Aba do Navegador
# =========================
class BrowserTab(QWebEngineView):
    def __init__(self, incognito=False):
        super().__init__()

        if incognito:
            profile = QWebEngineProfile()
            profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
            self.setPage(QWebEnginePage(profile, self))
        # layout mínimo para performance
        self.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)

# =========================
# Janela Principal
# =========================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.history = load_json(HISTORY_FILE, [])
        self.bookmarks = load_json(BOOKMARKS_FILE, [])

        # normalizar bookmarks antigos que só tinham URL
        for b in list(self.bookmarks):
            if isinstance(b, str):
                b_index = self.bookmarks.index(b)
                self.bookmarks[b_index] = {"url": b, "title": b}
            elif isinstance(b, dict) and "title" not in b:
                b.setdefault("title", b.get("url", ""))

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.setCentralWidget(self.tabs)

        self.setWindowTitle("Navegador Saturno")
        self.setWindowIcon(get_icon("icone.png"))
        self.showMaximized()

        self.init_navbar()
        self.apply_dark_theme()

        self.add_new_tab(QUrl("https://duckduckgo.com"), "Home")

    # =========================
    # Navbar
    # =========================
    def init_navbar(self):
        navbar = QToolBar()
        self.addToolBar(navbar)
        navbar.setIconSize(QSize(20, 20))

        back = QAction(get_icon("voltar.png"), "Voltar", self)
        back.triggered.connect(lambda: self.safe_call_current("back"))
        navbar.addAction(back)

        forward = QAction(get_icon("avançar.png"), "Avançar", self)
        forward.triggered.connect(lambda: self.safe_call_current("forward"))
        navbar.addAction(forward)

        reload = QAction(get_icon("f5.png"), "Recarregar", self)
        reload.triggered.connect(lambda: self.safe_call_current("reload"))
        navbar.addAction(reload)

        self.https_icon = QLabel()
        self.https_icon.setFixedWidth(20)
        navbar.addWidget(self.https_icon)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Pesquisar ou digitar endereço — Enter para ir")
        self.url_bar.returnPressed.connect(self.navigate)
        self.url_bar.setMinimumWidth(350)
        navbar.addWidget(self.url_bar)

        # Completer com títulos e urls
        completer_list = []
        for b in self.bookmarks:
            if isinstance(b, dict):
                completer_list.append(b.get("title", b.get("url")))
                completer_list.append(b.get("url"))
            else:
                completer_list.append(b)
        completer = QCompleter(list(dict.fromkeys(completer_list)))
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.url_bar.setCompleter(completer)

        new_tab = QAction(get_icon("home.png"), "Nova Aba", self)
        new_tab.triggered.connect(self.add_new_tab)
        navbar.addAction(new_tab)

        bookmark = QAction(get_icon("icone.png"), "Adicionar Favorito", self)
        bookmark.triggered.connect(self.add_bookmark)
        navbar.addAction(bookmark)

        incognito = QAction(get_icon("pesquisa.png"), "Incógnito", self)
        incognito.triggered.connect(self.open_incognito)
        navbar.addAction(incognito)

    def safe_call_current(self, method: str):
        try:
            browser = self.tabs.currentWidget()
            if not browser:
                return
            getattr(browser, method)()
        except Exception:
            pass

    # =========================
    # Abas
    # =========================
    def add_new_tab(self, qurl=None, title="Nova Aba", incognito=False):
        browser = BrowserTab(incognito)
        qurl = qurl or QUrl("https://duckduckgo.com")
        browser.setUrl(qurl)

        index = self.tabs.addTab(browser, title)
        self.tabs.setCurrentIndex(index)

        browser.urlChanged.connect(lambda qurl: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _: self.update_title(browser))
        browser.urlChanged.connect(self.save_history)
        # define ícone padrão da aba
        self.tabs.setTabIcon(index, get_icon("home.png"))

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def current_tab_changed(self, index):
        browser = self.tabs.currentWidget()
        if browser:
            self.update_urlbar(browser.url(), browser)

    # =========================
    # Navegação inteligente
    # =========================
    def parse_input(self, text):
        if text.startswith(("http://", "https://")):
            return QUrl(text)

        if "." in text and " " not in text:
            return QUrl("https://" + text)

        query = QUrl.toPercentEncoding(text)
        return QUrl(f"https://duckduckgo.com/?q={query.data().decode()}")

    def navigate(self):
        qurl = self.parse_input(self.url_bar.text())
        self.tabs.currentWidget().setUrl(qurl)

    # =========================
    # UI Updates
    # =========================
    def update_title(self, browser):
        title = browser.page().title() or "Nova Aba"
        self.setWindowTitle(title + " - Navegador Saturno")
        self.tabs.setTabText(self.tabs.currentIndex(), title)

    def update_urlbar(self, qurl, browser):
        if browser != self.tabs.currentWidget():
            return

        self.url_bar.setText(qurl.toString().replace("https://", "").replace("http://", ""))
        # usa ícone simples para https quando disponível
        if qurl.scheme() == "https":
            pix = QPixmap(get_asset_path("icone.png"))
            if not pix.isNull():
                self.https_icon.setPixmap(pix.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.https_icon.setText("🔒")
        else:
            self.https_icon.setText("⚠")

    # =========================
    # Histórico
    # =========================
    def save_history(self, qurl):
        url = qurl.toString()
        # evita duplicatas e limita tamanho
        if not self.history or self.history[-1] != url:
            self.history.append(url)
            if len(self.history) > 200:
                self.history = self.history[-200:]
            save_json(HISTORY_FILE, self.history)

    # =========================
    # Favoritos
    # =========================
    def add_bookmark(self):
        browser = self.tabs.currentWidget()
        url = browser.url().toString()
        title = browser.page().title() or url
        # evita duplicatas
        for b in self.bookmarks:
            if b.get("url") == url:
                return
        self.bookmarks.append({"url": url, "title": title})
        save_json(BOOKMARKS_FILE, self.bookmarks)

    # =========================
    # Incógnito
    # =========================
    def open_incognito(self):
        self.add_new_tab(incognito=True, title="Aba Anônima")

    # =========================
    # Tema Escuro
    # =========================
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QMainWindow { background: #121212; }
            QLineEdit { background: #1e1e1e; color: white; padding: 6px; }
            QToolBar { background: #1c1c1c; }
        """)

# =========================
# Execução
# =========================
app = QApplication(sys.argv)
app.setApplicationName("Navegador Saturno")
window = MainWindow()
sys.exit(app.exec_())
