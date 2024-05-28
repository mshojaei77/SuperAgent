import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths to specific directories
KNOWLEDGE_DIR = os.path.join(BASE_DIR, 'Knowledge')
TOOLS_DIR = os.path.join(BASE_DIR, 'Tools')
FILES_DIR = os.path.join(BASE_DIR, 'files')
MEMORY_DIR = os.path.join(BASE_DIR, 'Memory')
