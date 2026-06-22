#!/usr/bin/env python3
"""
Seed dos usuários de Coordenação 2026.
Seguro para rodar múltiplas vezes (idempotente — não duplica usuários existentes).

Uso:
    python seed_coordenacao.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth import generate_temp_password
from db_relatorio import get_all_usuarios, create_usuario

_USUARIOS = [
    {"username": "cristiane.dantas", "nome": "Cristiane Dantas"},
    {"username": "adriana.falcao",   "nome": "Adriana Falcão"},
]


def run_seed() -> dict:
    existentes = {u["username"] for u in get_all_usuarios()}
    criados = []
    for dados in _USUARIOS:
        if dados["username"] in existentes:
            continue
        senha = generate_temp_password()
        create_usuario(dados["username"], senha, dados["nome"], role="coordenacao")
        criados.append({"username": dados["username"], "nome": dados["nome"], "senha": senha})
    return {"criados": criados}


if __name__ == "__main__":
    resultado = run_seed()
    if not resultado["criados"]:
        print("Nenhum usuário novo — coordenação já cadastrada.")
    for u in resultado["criados"]:
        print(f"{u['nome']} | usuário: {u['username']} | senha temporária: {u['senha']}")
