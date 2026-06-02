from pathlib import Path

ROOT = Path(__file__).resolve().parent


SOURCE = ROOT / 'source'
CORPUS = SOURCE / 'corpus'
OUTPUT = ROOT / 'output'


OUTPUT.mkdir(exist_ok=True)