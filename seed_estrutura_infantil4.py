#!/usr/bin/env python3
"""
Seed da estrutura avaliativa (Tópico → Tema → Subtema) específica do Infantil 4.
Escopo: apenas Infantil 4 – A e Infantil 4 – B.
Seguro para rodar múltiplas vezes (idempotente).

Uso:
    python seed_estrutura_infantil4.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_relatorio import (
    get_all_topicos, create_topico, update_topico_turmas,
    create_tema, update_tema_turmas,
    create_subtema,
)

TURMAS_INFANTIL_4 = ["Infantil 4 – A", "Infantil 4 – B"]

ESTRUTURA = [
    ("EIXO COMPORTAMENTAL/ATITUDINAL", "Conteúdos e Habilidades", [
        "Dialoga com os outros a fim de exprimir sentimentos, opiniões, etc.",
        "Explora e descreve diferenças e semelhanças entre objetos.",
    ]),
    ("LINGUAGEM ORAL", "Conteúdos e Habilidades", [
        "Faz exposição oral de ideias com clareza e sequência lógica.",
        "Faz desenhos como forma de representação.",
        "Narra, descreve, explica, relata, ouve e argumenta com outras crianças.",
        "Demonstrou gradativa ampliação do vocabulário.",
    ]),
    ("LINGUAGEM ESCRITA", "Conteúdos e Habilidades", [
        "Reconhece as letras do próprio nome.",
        "Escreve nome e sobrenome sem utilizar ficha de apoio.",
        "Identifica as consoantes estudadas em palavras soltas, frases e/ou textos.",
        "Lê e escreve as consoantes estudadas.",
        "Completa palavras com as vogais correspondentes.",
    ]),
    ("MATEMÁTICA", "Conteúdos e Habilidades", [
        "Classifica elementos conforme diferentes critérios, como cor, forma, tamanho e quantidades.",
        "Conhece os números e desenvolve a contagem de 1 até 10.",
        "Conhece os números e desenvolve a contagem de 10 até 20.",
        "Reconhece os numerais e associa-os às quantidades.",
        "Demonstra noção acerca da sequência numérica (antecessor e sucessor).",
        "Identifica e nomeia as figuras planas.",
        "Compara elementos de seu meio para relações entre leve e pesado, cheio e vazio, "
        "grande/pequeno, maior/menor.",
        "Identifica e nomeia os sólidos geométricos.",
        "Faz agrupamentos utilizando como critério a quantidade para estabelecer aproximações "
        "com diferentes possibilidades de contagem.",
    ]),
    ("PSICOMOTRICIDADE", "Conteúdos e Habilidades", [
        "Apresenta conhecimento do corpo, como reconhecimento da própria imagem do corpo.",
    ]),
]


def run_seed() -> dict:
    """
    Executa o seed de forma idempotente.
    Retorna contadores para exibição no admin.
    """
    # Casa por nome + turmas (e não só nome) para não misturar com tópicos
    # de mesmo nome usados por outras turmas (ex: Infantil 3/5).
    topicos_existentes = get_all_topicos()

    topicos_criados = 0
    temas_criados = 0
    subtemas_criados = 0

    for ordem, (nome_topico, nome_tema, subtemas) in enumerate(ESTRUTURA, start=1):
        topico = next(
            (tp for tp in topicos_existentes
             if tp["nome"] == nome_topico and (tp.get("turmas") or []) == TURMAS_INFANTIL_4),
            None,
        )
        if topico is None:
            topico = create_topico(nome_topico, ordem=ordem)
            topico["temas"] = []
            topicos_criados += 1
        update_topico_turmas(topico["id"], TURMAS_INFANTIL_4)

        tema_existente = next(
            (t for t in topico.get("temas", []) if t["nome"] == nome_tema), None
        )
        if tema_existente is None:
            tema = create_tema(nome_tema, topico_id=topico["id"])
            tema["subtemas"] = []
            temas_criados += 1
        else:
            tema = tema_existente
        update_tema_turmas(tema["id"], TURMAS_INFANTIL_4)

        descricoes_existentes = {s["descricao"] for s in tema.get("subtemas", [])}
        for ordem_sub, descricao in enumerate(subtemas, start=1):
            if descricao not in descricoes_existentes:
                create_subtema(tema["id"], descricao, ordem=ordem_sub)
                subtemas_criados += 1

    return {
        "topicos": topicos_criados,
        "temas": temas_criados,
        "subtemas": subtemas_criados,
    }


def main():
    print("=" * 56)
    print("  Seed - Estrutura Avaliativa Infantil 4 (A e B)")
    print("=" * 56)
    result = run_seed()
    print(f"  Tópicos criados:  {result['topicos']}")
    print(f"  Temas criados:    {result['temas']}")
    print(f"  Subtemas criados: {result['subtemas']}")
    print("=" * 56)


if __name__ == "__main__":
    main()
