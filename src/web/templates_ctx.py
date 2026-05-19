from pathlib import Path

from fastapi.templating import Jinja2Templates

from src.web.helpers import today_iso

BASE_DIR = Path(__file__).resolve().parents[2]
templates = Jinja2Templates(directory=str(BASE_DIR / 'templates'))
templates.env.globals['today_iso'] = today_iso
