from pathlib import Path

ROOT = Path(__file__).parents[1]

ROUTES = ROOT / 'routes'

LOG = ROOT / 'logs' / 'responder.log'

FILES = ROOT / 'files'
PDFJS = FILES / 'pdf.js'



APP_HOST = '0.0.0.0'
APP_PORT = 14222