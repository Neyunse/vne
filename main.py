import os
import shutil
import sys
import argparse
import pyzipper
from datetime import datetime
import platform
from vne import Core
from vne import aes
from vne import config as CONFIG
from vne.config import key, engine_version
import re  
import hashlib
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QSizePolicy, QTextEdit, QStackedWidget, QTabWidget, QInputDialog, 
    QMessageBox, QPlainTextEdit, QToolBar, QFileDialog, QDialog, QLineEdit, QFormLayout, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTimer, QRegularExpression, QSize, pyqtSignal, QProcess
from PyQt6.QtGui import QCursor, QKeySequence, QShortcut, QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QAction

def compile_kag(source_file, target_file, key):
    """
    Reads a source file, encodes its content using an AES operation with a given key,
    and writes the result to a target file.
    
    :param source_file: The path to the source file containing the plain text data.
    :param target_file: The file path where the compiled data will be written in binary format.
    :param key: The key used to perform AES encryption on the data.
    """
    with open(source_file, "r", encoding="utf-8") as sf:
        plain_text = sf.read()
    plain_bytes = plain_text.encode("utf-8")
    compiled_bytes = aes.AES(plain_bytes, key).encrypt()
    with open(target_file, "wb") as tf:
        tf.write(compiled_bytes)
    
 
    print(f"[compile] {source_file} -> {target_file}")
 
def compile_all_kag_in_folder(data_folder, key):
    """
    Compiles all KAG files in the specified folder using the given key.
    
    :param data_folder: The directory path where the KAG files are located.
    :param key: The key used for encryption/decryption.
    """
    for root, dirs, files in os.walk(data_folder):
        for file in files:
            if file.endswith(CONFIG.file_extension):
                source_path = os.path.join(root, file)
                target_path = os.path.splitext(source_path)[0] + CONFIG.aes_extension
                compile_kag(source_path, target_path, key)

def create_data_pkg(source_folder, output_pkg):
    """
    Recursively packs the files in the source_folder into an encrypted ZIP archive,
    excluding single .kag files (only .kagc or other files are included).

    param source_folder: Path of the folder with the data to be packed.
    :param output_pkg: Path of the ZIP file to be created.
    """
    with pyzipper.AESZipFile(
            output_pkg,
            'w',
            compression=pyzipper.ZIP_DEFLATED,
            encryption=pyzipper.WZ_AES) as pkg:
        pkg.setpassword(key)
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                
                if file.lower().endswith(CONFIG.file_extension) and not file.lower().endswith(CONFIG.aes_extension):
                    continue
                file_path = os.path.join(root, file)
            
                rel_path = os.path.relpath(file_path, source_folder)
                pkg.write(file_path, rel_path)
    print(f"[create_data_pkg] '{source_folder}' packed in '{output_pkg}' (excluding {CONFIG.file_extension} files)")

def init_game(game_path, project_name):
    """
    Initializes a game project by creating directories and generating necessary script files.
    
    :param game_path: The path where the game project will be initialized.
    """
    print(f"Initializing project in '{game_path}'...")
    directories = [
        f"{game_path}/data",
        f"{game_path}/data/system",
        f"{game_path}/data/scenes",
        f"{game_path}/data/images/bg",
        f"{game_path}/data/images/sprites",
        f"{game_path}/data/ui",
        f"{game_path}/data/ui/icon",
        # f"{game_path}/data/audio/bgm",
        # f"{game_path}/data/audio/sfx",
        # f"{game_path}/saves",
    ]
    for d in directories:
        os.makedirs(d, exist_ok=True)
        print(f"Directory created: {d}")

    main_menu_file = os.path.join(game_path, "data", "system", f"main_menu{CONFIG.file_extension}")
    scenes_file = os.path.join(game_path, "data", "system", f"scenes{CONFIG.file_extension}")
    characters_file = os.path.join(game_path, "data", "system", f"characters{CONFIG.file_extension}")
    ui_file = os.path.join(game_path, "data", "system", f"ui{CONFIG.file_extension}")
    vars_file = os.path.join(game_path, "data", "system", f"vars{CONFIG.file_extension}")
    startup_file = os.path.join(game_path, "data", f"{CONFIG.init_file}{CONFIG.file_extension}")

    # scenes
    first_scene_file = os.path.join(game_path, "data", "scenes", f"first{CONFIG.file_extension}")

    with open(main_menu_file, "w", encoding="utf-8") as f:
        f.write("# Main Menu\n")
        f.write("@mainMenu\n")
        f.write("  @button \"Start game\" event Scene(\"first\") \n")
        f.write("  @button \"Quit\" event Quit() \n")
        f.write("@endMainMenu\n")

    with open(ui_file, "w", encoding="utf-8") as f:
        f.write("# set the window size. eg: @Display(800,600)\n")
        f.write("# the recomended max size is 1280x720 \n")
        f.write("@Display(800,600)\n")
        f.write("# set the game title\n")
        f.write(f"@GameTitle(\"{project_name}\")\n")
        f.write("# set the gane icon. eg. @GameIconName(\"window_icon\")\n")
        f.write("# by default window_icon. \n")
        f.write(f"# @GameIconName()\n")


    with open(startup_file, "w", encoding="utf-8") as f:
        f.write("# Game startup script\n")
        f.write("\n")
        f.write("# Load here somthing before that system files\n")
        f.write("\n")
        f.write("@LoadSystem()\n")
        f.write("\n")
        f.write("# Load here somthing after that system files\n")
        f.write("\n")
        f.write("# Load the main menu from system/\n")
        f.write("@LoadMainMenu()\n")

    with open(scenes_file, "w", encoding="utf-8") as f:
        f.write("@scene first = \"first\"")
    
    with open(characters_file, "w", encoding="utf-8") as f:
        f.write("@char K as \"Kuro\" ")
    
    with open(vars_file, "w", encoding="utf-8") as f:
        f.write("# Include variables here")

    with open(first_scene_file, "w", encoding="utf-8") as f:
        f.write("K: Hello!\n")
        f.write("K: my name is {K}.\n")
        f.write(f"K: start editing scenes/first{CONFIG.file_extension} to add dialogues.\n")
        f.write("K: good luck in your stories.\n")
        f.write("@end\n")

    print("Files generated successfully")

def distribute_game(game_path):
    """
    Packages a game located at the specified path by compiling data files, creating a package,
    copying necessary files to a distribution folder, and outputting the distribution location.
    
    :param game_path: The path to the directory containing the game files to be distributed.
    """
    try:
        print(f"Packaging game from '{game_path}'...")
        game_path = os.path.abspath(game_path)
        game_name = os.path.basename(game_path)
    
        data_folder = os.path.join(game_path, "data")
        compile_all_kag_in_folder(data_folder, key)
    
        pkg_path = os.path.join(game_path, "data.pkg")
        create_data_pkg(data_folder, pkg_path)

        current_dir = os.getcwd()
        dist_root = os.path.join(current_dir, "dist")
        if not os.path.exists(dist_root):
            os.makedirs(dist_root)
        dest_folder = os.path.join(dist_root, game_name)
        if os.path.exists(dest_folder):
            shutil.rmtree(dest_folder)
        os.makedirs(dest_folder)

        shutil.copy2(pkg_path, os.path.join(dest_folder, f"data{CONFIG.bundle_extension}"))
        print(f"[distribute] data{CONFIG.bundle_extension} copied to {dest_folder}")
    
        os.unlink(pkg_path)
        
        exe_source = os.path.join(os.path.dirname(sys.executable),"lib", "win", "bootstrapper.exe")
        exe_source = os.path.abspath(exe_source)
   
        exe_dest = os.path.join(dest_folder, "game.exe")
        shutil.copy2(exe_source, exe_dest)
        print(f"[distribute] Binary copied: {exe_source} → {exe_dest}")

        print(f"Distribution completed at: {dest_folder}")
    except Exception as e:
        raise Exception(e)

def get_data_folder(game_path):
    data_folder = os.path.join(game_path, "data")
    if not os.path.exists(data_folder):
        raise Exception(f"Data folder '{data_folder}' does not exist.")
 
    return data_folder

def run_game(game_path):
    """
    Compiles all KAG files in the specified folder and runs the game engine with the given game path in development mode.
    
    :param game_path: The path to the directory where the game files are located.
    """
    data_folder = get_data_folder(game_path) 

    print("---------[DEVELOPER]---------")
    compile_all_kag_in_folder(data_folder, key)
    print("-----------------------------")

    engine = Core(game_path, devMode=True)
    engine.run()

def arguments():
    """
    Parses command line arguments to initialize, debug, or distribute a game based on the specified command.
    """
    exe_name = os.path.basename(sys.executable).lower()
    parser = argparse.ArgumentParser()
 
    
    parser.add_argument('-i', dest="new_project", default=False, action="store_true", help="initializes a new project")
    parser.add_argument('-p', dest="project_name", default=None, type=str, help="allows you to add a name to the project if -i is present", required='-i' in sys.argv)
    
    parser.add_argument('-r', dest="debug_project", default=False, action="store_true", help="debug a project")
    parser.add_argument('-d', dest="distribute_project", default=False, action="store_true", help="distribute a project")
    
    parser.add_argument('-f', dest="project_folder", default="launcher", type=str, help="Project Folder (required)", required='-f' in sys.argv)
    
    args = parser.parse_args()

    isNewProject = args.new_project
    project_name = args.project_name
    debug_project = args.debug_project
    distribute_project = args.distribute_project
    project_folder = args.project_folder
    
    
    if isNewProject and project_name and project_folder and not "python.exe" in exe_name:
        init_game(project_folder, project_name)
    elif debug_project and project_folder:
        run_game(project_folder)
    elif distribute_project and project_folder and not "python.exe" in exe_name:
        distribute_game(project_folder)
    else:
        raise Exception("Invalid command or missing arguments.")

def engine_path(exePath=False):
    engine = os.path.dirname(os.path.abspath(__file__))
    engine = os.path.abspath(engine)
  
    if exePath:
        if sys.executable:
            return os.path.abspath(sys.executable)
        
        return engine
    
    return engine


PROJECT_FOLDER = "projects"
class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setFixedSize(350, 120)

        self.layout = QFormLayout(self)

        self.title_input = QLineEdit()
        self.directory_input = QLineEdit()
        self.title_input.textChanged.connect(self.change_title)
 

        self.layout.addRow("Project Title:", self.title_input)
        self.layout.addRow("Directory Name:", self.directory_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)
        
        
    def change_title(self, _):
        valid_file_name = re.sub(r"\s+", "-", self.title_input.text())
        self.directory_input.setText(valid_file_name)

    def get_data(self):
        return self.title_input.text().strip(), self.directory_input.text().strip()
class VNScriptHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Formats
        self.keywordFormat = QTextCharFormat()
        self.keywordFormat.setForeground(QColor("#569CD6"))  # blue
        self.keywordFormat.setFontWeight(QFont.Weight.Bold)

        self.stringFormat = QTextCharFormat()
        self.stringFormat.setForeground(QColor("#6A9955"))  # green

        self.variableFormat = QTextCharFormat()
        self.variableFormat.setForeground(QColor("#D16969"))  # light red/orange

        self.commentFormat = QTextCharFormat()
        self.commentFormat.setForeground(QColor("#6A9955"))
        self.commentFormat.setFontItalic(True)
        
        self.modf = QTextCharFormat()
        self.modf.setForeground(QColor("#CA5A0F"))  # light red/orange

        # Rules for keywords (commands @)
        keywords = [
            "@def", "@set", "@if", "@else", "@endif", "@say", "@char", "@choice",
            "@option", "@end_choice", "@scene", "@jump_scene", "@checkpoint", "@goto",
            "@bgm", "@sfx", "@sprite", "@hide", "@bg", "@rename", "@menu", "@button",
            "@endMenu", "@end", "@Display", "@GameTitle", "@LoadSystem", "@LoadMainMenu", "Scene", "Quit"
        ]
        self.rules = []
        for kw in keywords:
            escaped_kw = re.escape(kw)
            pattern = QRegularExpression(escaped_kw)
            self.rules.append((pattern, self.keywordFormat))
        
        modf = [ ]
        
        for mdf in modf:
            escaped_mdf = re.escape(mdf)   
            pattern = QRegularExpression(escaped_mdf)
            self.rules.append((pattern, self.modf))

        # Strings in double quotes
        self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), self.stringFormat))

        # Variables in text between { }
        self.rules.append((QRegularExpression(r'\{[^}]+\}'), self.variableFormat))

        # Booleans true/false
        self.rules.append((QRegularExpression(r'\b(true|false)\b', QRegularExpression.PatternOption.CaseInsensitiveOption), self.keywordFormat))

        # Comments (if you use #)
        self.rules.append((QRegularExpression(r'#.*'), self.commentFormat))
        
        # Numbers 
        self.rules.append((QRegularExpression(r'^[0-9]*$'), self.keywordFormat))
        
        # Defined (e.g. m: Hello)
        self.rules.append((
            QRegularExpression(r'^\s*([a-zA-Z_]\w*):'), self.stringFormat))

        # Not defined (e.g. Shin*: Hello)
        self.rules.append((
            QRegularExpression(r'^\s*([a-zA-Z_]\w*)\*'), self.stringFormat))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, fmt)

        self.setCurrentBlockState(0)

class MainView(QWidget):
    openExternalProject = pyqtSignal(str)
    openNewProject = pyqtSignal(str)
    
    def __init__(self, go_to_editor, projects, projects_dir):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.go_to_editor = go_to_editor
        self.projects = projects
        self.projects_dir = projects_dir
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setObjectName("sidebar")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setSpacing(12)

        new_btn = QPushButton("\u2795 New Project")
        new_btn.clicked.connect(self.create_new_project)
        open_btn = QPushButton("\ud83d\udcc2 Import Project")
        open_btn.clicked.connect(self.open_project_directory)
 
        
        for btn in (new_btn, open_btn):
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFixedHeight(35)
            self.sidebar_layout.addWidget(btn)

        self.sidebar_layout.addStretch()

        version_label = QLabel("VNEngine Launcher v0.1")
        version_label.setStyleSheet("font-size: 10px; color: gray;")
        self.sidebar_layout.addWidget(version_label)

        layout.addWidget(self.sidebar)

        content_layout = QVBoxLayout()

        title = QLabel("Projects")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        content_layout.addWidget(title)

        for name in self.projects:
            content_layout.addWidget(self.create_project_box(name))

        content_layout.addStretch()

        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        layout.addWidget(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
    
    def create_new_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, directory = dialog.get_data()

            if not title or not directory:
                QMessageBox.warning(self, "VNEngine", "Please complete both fields.")
                return

            # Validate directory doesn't already exist in projects
            destination = os.path.join(self.projects_dir, directory)
            
            if destination:
                init_game(destination, title)
                
                path = os.path.join(destination, title)
                
                self.openNewProject.emit(path)
        else:
            dialog.close()
    
    def open_project_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder", os.path.expanduser("~"))
        if path:
            self.openExternalProject.emit(path)
    def create_project_box(self, name):
        box = QFrame()
        box.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        box.setMinimumHeight(70)
        box.setObjectName("projectBox")

        layout = QHBoxLayout(box)
        layout.setSpacing(12)

        icon = QLabel("\ud83c\udfae")
        icon.setFixedSize(40, 40)
        layout.addWidget(icon)

        text_area = QVBoxLayout()
        title = QLabel(name)
        title.setStyleSheet("font-weight: bold; font-size: 15px;")
        subtitle = QLabel(os.path.abspath(f"{self.projects_dir}/{name}"))
        subtitle.setStyleSheet("font-size: 11px; color: #9999bb;")
        text_area.addWidget(title)
        text_area.addWidget(subtitle)
        layout.addLayout(text_area)

        layout.addStretch()

        run_btn = QPushButton("\u25b6")
        run_btn.setObjectName("runbtn")
        run_btn.setFixedSize(70, 30)
        
        run_btn.clicked.connect(lambda: run_game(os.path.join(self.projects_dir, name)))
        layout.addWidget(run_btn)

        box.mousePressEvent = lambda e: self.go_to_editor(name)
        return box

class EditorView(QWidget):
    def __init__(self, back_func, file_structure):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.back_func = back_func
        self.mock_fs = file_structure
        self.opened_files = {}      # {path: QTextEdit}
        self.file_hashes = {}       # {path: hash_str}
        self.timers = {}            # {path: QTimer for auto save}
        self.mock_fs_base_path = ""  # absolute path of the project
        self.exclude = [".aes", ".sav", "saves"]
        self.init_ui()
    
    def run_project(self,_):
        play = run_game(self.mock_fs_base_path)
    def build_project(self,_):
        exe_name = os.path.basename(sys.executable).lower()
        if "python.exe" in exe_name:
            return
        dist = distribute_game(self.mock_fs_base_path)
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setObjectName("sidebar")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setSpacing(12)
        self.original_file_hashes = {}

        self.back_btn = QPushButton("\u2190 Back")
        self.back_btn.clicked.connect(self.back_func)
        self.sidebar_layout.addWidget(self.back_btn)

        self.files_container = QVBoxLayout()
        self.files_container.setSpacing(0)
        self.sidebar_layout.addLayout(self.files_container)
        self.sidebar_layout.addStretch()

        layout.addWidget(self.sidebar)

        self.editor_layout = QVBoxLayout()
        # ToolBar
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #1e1e1e;
                border-bottom: 1px solid #3C3C3C;
                spacing: 6px;
                padding: 4px;
            }
            QToolButton {
                background: transparent;
                color: #CCCCCC;
              
                border: none;
                padding: 6px 10px;
               
            }
            QToolButton:hover {
                background-color: #2d2d2d;
            }
        """)
        self.toolbar.setIconSize(QSize(16, 16))

        
        save_action = QAction("💾", self)
        save_action.setToolTip("Save the currently opened file")
        
        save_action.triggered.connect(self.save_current_file)
        self.toolbar.addAction(save_action)
        # Action: Run
        run_action = QAction("▶", self)
        run_action.setToolTip("Run project")

        run_action.triggered.connect(self.run_project)
        self.toolbar.addAction(run_action)
        
        build_action = QAction("🔨", self)
        build_action.setToolTip("Build project")
        build_action.triggered.connect( self.build_project)
        self.toolbar.addAction(build_action)
        

        # Add more actions here if you want

        self.editor_layout.addWidget(self.toolbar)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.editor_layout.addWidget(self.tabs)
        
        if self.tabs.count() == 0:
            save_action.setVisible(False)
        else:
            save_action.setVisible(True)
        
        container = QWidget()
        container.setLayout(self.editor_layout)

        layout.addWidget(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut_save.activated.connect(self.save_current_file)
        
    
    def save_current_file(self):
        current_editor = self.tabs.currentWidget()
        if current_editor:
            for path, editor in self.opened_files.items():
                if editor == current_editor:
                    content = editor.toPlainText()
                    new_hash = self.calculate_hash(content)
                    if new_hash != self.original_file_hashes.get(path, ""):
                        try:
                            full_path = os.path.join(self.mock_fs_base_path, path)
                            with open(full_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            self.original_file_hashes[path] = new_hash  # Update base hash
                            self.file_hashes[path] = new_hash
                            print(f"Saved with Ctrl+S: {path}")
                        except Exception as e:
                            QMessageBox.critical(self, "VNEngine", f"Error saving file:\n{e}")
                    else:
                        print("No changes. Not saved.")
                    break
    def load_files(self, structure, path=""):
        self.clear_layout(self.files_container)
        self._create_file_tree(self.files_container, structure, path)

    def _create_file_tree(self, parent_layout, structure, base_path):
        # Separate folders and files
        folders = {k: v for k, v in structure.items() if isinstance(v, dict)}
        files = {k: v for k, v in structure.items() if not isinstance(v, dict)}
    
        # Process folders first (alphabetical order)
        for name, content in sorted(folders.items()):
            
            if any(name.lower().endswith(ext) for ext in self.exclude):
                continue

            full_path = f"{base_path}/{name}" if base_path else name

            container = QHBoxLayout()
            container.setContentsMargins(0, 2, 0, 2)
            container.setSpacing(4)

            folder_btn = QPushButton(f"\ud83d\udcc1 {name}")
            folder_btn.setCheckable(True)
            folder_btn.setChecked(False)
            folder_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            folder_btn.setProperty("class", "fileOrFolderBtn")
            container.addWidget(folder_btn)

            if name == "scenes":
                add_btn = QPushButton("+")
                add_btn.setFixedWidth(20)
                add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                add_btn.setProperty("class", "addScriptBtn")
                add_btn.clicked.connect(lambda _, n=name, base=full_path: self.add_script(base))
                container.addWidget(add_btn)

            parent_widget = QWidget()
            parent_widget.setLayout(container)
            parent_layout.addWidget(parent_widget)

            folder_layout = QVBoxLayout()
            folder_layout.setContentsMargins(12, 2, 0, 2)
            folder_layout.setSpacing(2)
            folder_widget = QWidget()
            folder_widget.setLayout(folder_layout)
            folder_widget.setVisible(False)

            folder_btn.toggled.connect(lambda checked, w=folder_widget: w.setVisible(checked))

            parent_layout.addWidget(folder_widget)

            self._create_file_tree(folder_layout, content, full_path)

        # Process files (alphabetical order)
        for name, content in sorted(files.items()):
            if any(name.lower().endswith(ext) for ext in self.exclude):
                continue

            full_path = f"{base_path}/{name}" if base_path else name

            container = QHBoxLayout()
            container.setContentsMargins(0, 0, 0, 0)
            container.setSpacing(6)

            ext = name.lower().split(".")[-1]
            if ext in ("png", "jpg", "jpeg", "bmp", "gif"):
                file_btn = QPushButton(f"\U0001F5BC {name}")  # Image icon
                file_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                file_btn.setProperty("class", "fileOrFolderBtn")
                file_btn.clicked.connect(lambda: None)  # Do not open editor
            else:
                file_btn = QPushButton(f"\ud83d\udcc4 {name}")  # Regular file icon
                file_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                file_btn.setProperty("class", "fileOrFolderBtn")
                file_btn.clicked.connect(lambda _, r=full_path: self.open_file(r))

            container.addWidget(file_btn)

            parent_widget = QWidget()
            parent_widget.setLayout(container)
            parent_layout.addWidget(parent_widget)

    def add_script(self, base_path):
        new_name, ok = QInputDialog.getText(self, "New Script", "Script name:")
        if ok and new_name:
            if not new_name.endswith(".script"):
                new_name += ".script"

            # Create structure if it doesn't exist
            parts = base_path.split("/")
            ref = self.mock_fs
            for p in parts:
                if p not in ref or not isinstance(ref[p], dict):
                    ref[p] = {}
                ref = ref[p]

            if new_name in ref:
                QMessageBox.warning(self, "VNEngine", "⚠️ A script with that name already exists.")
                return

            ref[new_name] = ""

            # Create physical file
            absolute_path = os.path.join(self.mock_fs_base_path, base_path.replace("/", os.sep), new_name)
            os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
            try:
                with open(absolute_path, "w", encoding="utf-8") as f:
                    f.write("")  # Empty script
            except Exception as e:
                QMessageBox.critical(self, "VNEngine", f"Error creating script:\n{e}")
                return

            self.load_files(self.mock_fs)
            self.open_file(base_path + '/' + new_name, "")

    def open_file(self, path, _ignored_content=""):
        ext = path.lower().split(".")[-1]
        if ext in ("png", "jpg", "jpeg", "bmp", "gif"):
            QMessageBox.information(self, "VNEngine Launcher", "Image files cannot be opened in the editor.")
            return

        if path in self.opened_files:
            index = self.tabs.indexOf(self.opened_files[path])
            if index != -1:
                self.tabs.setCurrentIndex(index)
            return
        
        if self.tabs.count() >= 10:
            QMessageBox.warning(self, "VNEngine Launcher", "⚠️ Limit of 10 active tabs reached.",
                                QMessageBox.StandardButton.Ok)
            return

        # 🔽 Read from the real file on disk
        absolute_path = os.path.join(self.mock_fs_base_path, path)
        try:
            with open(absolute_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            QMessageBox.critical(self, "VNEngine", f"Error opening file:\n{e}")
            return

        editor = QPlainTextEdit()
        highlighter = VNScriptHighlighter(editor.document())
        
        editor.setPlainText(content)
        self.tabs.addTab(editor, path.split("/")[-1])
        self.tabs.setCurrentWidget(editor)
        self.opened_files[path] = editor
      

        # Save original and initial hash
        initial_hash = self.calculate_hash(content)
        self.file_hashes[path] = initial_hash
        self.original_file_hashes[path] = initial_hash

        # Auto save timer
        timer = QTimer(self)
        timer.setInterval(60_000)  # 60 seconds
        timer.timeout.connect(lambda r=path: self.auto_save_file(r))
        timer.start()
        self.timers[path] = timer

        editor.textChanged.connect(lambda r=path, e=editor: self.on_text_changed(r, e))

    def on_text_changed(self, path, editor):
        current_text = editor.toPlainText()
        new_hash = self.calculate_hash(current_text)
        self.file_hashes[path] = new_hash
    def calculate_hash(self, text):
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def auto_save_file(self, path):
        if path not in self.opened_files:
            return  # File closed

        editor = self.opened_files[path]
        content = editor.toPlainText()
        current_hash = self.calculate_hash(content)

        if current_hash != self.original_file_hashes.get(path, ""):
            # Changes detected, save file
            try:
                full_path = os.path.join(self.mock_fs_base_path, path)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.original_file_hashes[path] = current_hash
                self.file_hashes[path] = current_hash
                print(f"Auto saved file: {path}")
            except Exception as e:
                print(f"Error auto saving file {path}: {e}")
    

    def close_tab(self, index):
        widget = self.tabs.widget(index)
        path_to_close = None
        for path, editor in list(self.opened_files.items()):
            if editor == widget:
                path_to_close = path
                break
        if path_to_close:
            self.save_on_close(path_to_close)
            # Stop and delete timer
            if path_to_close in self.timers:
                self.timers[path_to_close].stop()
                del self.timers[path_to_close]
            del self.opened_files[path_to_close]
            if path_to_close in self.file_hashes:
                del self.file_hashes[path_to_close]
            self.tabs.removeTab(index)

    

    def save_on_close(self, path):
        if path not in self.opened_files:
            return
        editor = self.opened_files[path]
        content = editor.toPlainText()
        current_hash = self.calculate_hash(content)
        saved_hash = self.original_file_hashes.get(path, "")
        if current_hash != saved_hash:
            try:
                full_path = os.path.join(self.mock_fs_base_path, path)
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.original_file_hashes[path] = current_hash
                self.file_hashes[path] = current_hash
                print(f"Saved on close file: {path}")
            except Exception as e:
                print(f"Error saving on close file {path}: {e}")

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VNEngine Launcher")
        self.resize(1100, 650)
        self.setStyleSheet(self.qss())

        # Projects directory at same level as this script
        self.engineDir = engine_path(True)
        self.projects_dir = os.path.join(os.path.dirname(self.engineDir), PROJECT_FOLDER)

        self.projects = self.load_projects()
        self.mock_fs = {}

        self.stack = QStackedWidget(self)
        self.main_view = MainView(self.go_to_editor, self.projects, self.projects_dir)
        self.editor_view = EditorView(self.go_to_list, self.mock_fs)

        self.stack.addWidget(self.main_view)
        self.stack.addWidget(self.editor_view)
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.addWidget(self.stack)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.main_view.openExternalProject.connect(self.add_project_from_path)
        self.main_view.openNewProject.connect(self.add_new_project)
        
        
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_process_output)
        self.process.readyReadStandardError.connect(self.read_process_error)
        self.process.finished.connect(self.process_finished)
        
    def run_external(self, exe_path, arguments):
        """
        Runs a .exe with arguments without blocking the UI.
        exe_path: string, path to executable.
        arguments: list of strings, arguments for the exe.
        """
        if self.process.state() == QProcess.ProcessState.Running:
            QMessageBox.warning(self, "VNEngine", "There is already a process running.")
            return
        
        self.process.start(exe_path, arguments)

    def read_process_output(self):
        output = self.process.readAllStandardOutput().data().decode()
        print(f"[Process output]: {output}")

    def read_process_error(self):
        error = self.process.readAllStandardError().data().decode()
        print(f"[Process error]: {error}")

    def process_finished(self, exitCode, exitStatus):
        print(f"Process finished with code {exitCode}, status {exitStatus}")
        QMessageBox.information(self, "VNEngine", f"Process finished with code {exitCode}")
    
    def add_new_project(self, path):
        name = os.path.basename(path)
   
        self.projects.append(name)
        # Rebuild main view to reflect changes:
        self.main_view.deleteLater()
        self.main_view = MainView(self.go_to_editor, self.projects, self.projects_dir)
        self.main_view.openNewProject.connect(self.add_new_project)
        self.stack.insertWidget(0, self.main_view)
        self.stack.setCurrentWidget(self.main_view)
    
    def add_project_from_path(self, path):
  
        name = os.path.basename(path)
        destination = os.path.join(self.projects_dir, name)
        
        if name in self.projects:
            QMessageBox.information(self, "VNEngine", f"The project '{name}' is already in the list.")
            return
        
        try:
            if not os.path.exists(destination):
                shutil.copytree(path, destination)
                shutil.rmtree(path)
            else:
                QMessageBox.warning(self, "VNEngine", f"There is already a folder with the name '{name}' in projects.")
                return
        except Exception as e:
            QMessageBox.critical(self, "VNEngine", f"Error importing project:\n{e}")
            return
        
        self.projects.append(name)
        # Rebuild main view to reflect changes:
        self.main_view.deleteLater()
        self.main_view = MainView(self.go_to_editor, self.projects, self.projects_dir)
        self.main_view.openExternalProject.connect(self.add_project_from_path)
        self.stack.insertWidget(0, self.main_view)
        self.stack.setCurrentWidget(self.main_view)
        
        QMessageBox.information(self, "VNEngine", f"Project '{name}' imported successfully.")

    def load_projects(self):
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir)
            return []
        projects = []
        for entry in os.listdir(self.projects_dir):
            full_path = os.path.join(self.projects_dir, entry)
            if os.path.isdir(full_path):
                projects.append(entry)
        return projects

    def load_file_structure(self, project):
        project_path = os.path.join(self.projects_dir, project)
        return self.walk_directory(project_path)

    def walk_directory(self, path):
        structure = {}
        try:
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    structure[entry] = self.walk_directory(full_path)
                else:
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            content = f.read()
                    except Exception:
                        content = ""
                    structure[entry] = content
        except Exception:
            pass
        return structure

    def go_to_editor(self, name):
        print(f"Open editor for: {name}")
        self.mock_fs = self.load_file_structure(name)
        self.editor_view.mock_fs = self.mock_fs
        self.editor_view.mock_fs_base_path = os.path.join(self.projects_dir, name)
        self.editor_view.load_files(self.mock_fs)
        self.stack.setCurrentWidget(self.editor_view)

    def go_to_list(self):
        self.stack.setCurrentWidget(self.main_view)

    def qss(self):
        return """
        QWidget {
            color: #CCCCCC;
            font-family: "Segoe UI", Consolas, sans-serif;
            font-size: 14px;
            margin: 0px;
        }
        QFrame#sidebar {
            background-color: #181818;
            border-right: 1px solid #2B2B2B;
        }
        QFrame#projectBox {
            background-color: #252526;
            border: 1px solid #3C3C3C;
            border-radius: 5px;
        }
        QPushButton {
            background-color: #333;
            color: #ccc;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 6px;
        }
        QPushButton:hover {
            background-color: #3d3d3d;
        }
        QPushButton#runbtn {
            font-size: 18px;
            background-color: darkgreen;
            color: white;
            border-radius: 8px;
        }
        QTextEdit {
            background-color: #1F1F1F;
            color: #CCCCCC;
            padding: 8px;
            border: 1px solid #2B2B2B;
            border-radius: 4px;
        }
        QPlainTextEdit {
            background-color: #1F1F1F;
            color: #CCCCCC;
            padding: 8px;
            border: 1px solid #2B2B2B;
            border-radius: 4px;
        }
        QTabBar::tab {
            background: #2B2B2B;
            padding: 5px;
        }
        QTabBar::tab:selected {
            background: #3D3D3D;
        }

        /* Styles for folders and files in sidebar */
        QPushButton.fileOrFolderBtn {
            background-color: transparent;
            border: none;
            color: #ccc;
            text-align: left;
            padding-left: 4px;
            padding-top: 2px;
            padding-bottom: 2px;
        }
        QPushButton.fileOrFolderBtn:hover {
            background-color: #2d2d2d;
        }
        QPushButton.fileOrFolderBtn:checked {
            background-color: transparent;
        }

        /* Style for the + button */
        QPushButton.addScriptBtn {
            background-color: transparent;
            border: none;
            color: #ccc;
            font-weight: bold;
        }
        QPushButton.addScriptBtn:hover {
            background-color: #2d2d2d;
        }
        """

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
        
    except Exception as e:
        traceback_template = '''Exception error:
  %(message)s\n

  %(plataform)s
  '''
        traceback_details = {
            'message' : e,
            'plataform': f"{platform.system()}-{platform.version()}"
        }

        print(traceback_template % traceback_details)
        with open('engine-error.txt', 'w') as f:
            f.write(traceback_template % traceback_details)
            f.close()