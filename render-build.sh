#!/usr/bin/env bash
# Limpiar cualquier versión vieja de discord.py antes de instalar Pycord
pip uninstall -y discord.py discord nextcord disnake || true
pip install -U pip
pip install -U py-cord==2.4.1
