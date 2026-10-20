import sys
import os
from pathlib import Path
import json

class Info:
    NAME = "FIN"

    @staticmethod
    def base_dir() -> Path:
        """
        Diretório base SOMENTE PARA LEITURA
        - Dev: raiz do projeto
        - EXE: _MEIPASS
        """
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS)
        return Path(__file__).parents[1]

    @staticmethod
    def user_dir() -> Path:
        """
        Diretório gravável do usuário
        """
        base = Path(os.getenv("LOCALAPPDATA", Path.home()))
        path = base / "FIN"
        path.mkdir(parents=True, exist_ok=True)
        return path

    # ===== LEITURA =====
    BASE_DIR = base_dir()
    WEB = BASE_DIR / "web"
    JSON = BASE_DIR / "config"
    MENU_LOGIN = WEB / "menu_login.html"

    # ===== ESCRITA =====
    DB = user_dir() / "data"
    CSV = user_dir() / "file_csv"
    USERS_JSON = user_dir() / "users.json"  # arquivo JSON para usuários

    # garante existência das pastas
    DB.mkdir(parents=True, exist_ok=True)
    CSV.mkdir(parents=True, exist_ok=True)

    # cria arquivo JSON vazio se não existir
    if not USERS_JSON.exists():
        USERS_JSON.write_text(json.dumps({}, indent=4, ensure_ascii=False))
