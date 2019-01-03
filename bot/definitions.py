"""
Some definitions for file paths to make my life easier.
"""
from os import path

ROOT_DIR = path.dirname(path.abspath(__file__))
LOG_DIR = path.join(ROOT_DIR, "logs")
CONFIG_DIR = path.join(ROOT_DIR, "config")
TREE_PATH = path.join(ROOT_DIR, "tree.json")
