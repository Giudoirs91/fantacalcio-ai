"""
tools/sync_injuries_fantacalcio_online.py
=========================================
Wrapper di compatibilità: reindirizza alla sincronizzazione ufficiale
da Fantacalcio.it (tools/sync_injuries_fantacalcio.py).
"""

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from tools.sync_injuries_fantacalcio import sync_injuries

if __name__ == '__main__':
    sync_injuries()
