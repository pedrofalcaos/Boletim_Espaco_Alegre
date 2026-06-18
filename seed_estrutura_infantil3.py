#!/usr/bin/env python3
"""
Seed da estrutura avaliativa (Tópico → Tema → Subtema) específica do Infantil 3.
Escopo: apenas Infantil 3 – A e Infantil 3 – B.
Seguro para rodar múltiplas vezes (idempotente).

Uso:
    python seed_estrutura_infantil3.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_relatorio import (
    get_all_topicos, create_topico, update_topico_turmas,
    create_tema, update_tema_turmas,
    create_subtema,
)

TURMAS_INFANTIL_3 = ["Infantil 3 – A", "Infantil 3 – B"]

ESTRUTURA = [
    ("EIXO COMPORTAMENTAL/ATITUDINAL", "Conteúdos e Habilidades", [
        "Dialoga com os outros a fim de exprimir sentimentos, opiniões, etc.",
        "Explora e descreve diferenças e semelhanças entre objetos.",
    ]),
    ("LINGUAGEM ORAL", "Conteúdos e Habilidades", [
        "Demonstra expressão: fluência, articulação e elaboração da fala.",
        "Apresenta estrutura de pensamento (sequência lógica da linguagem).",
        "Demonstrou gradativa ampliação do vocabulário.",
        "Reconhece auditivamente e reproduz as primeiras sílabas do próprio nome e dos colegas.",
    ]),
    ("LINGUAGEM ESCRITA", "Conteúdos e Habilidades", [
        "Reconhece o nome próprio.",
        "Reconhece e nomeia as letras do próprio nome.",
        "Escreve e reconhece as vogais A, E, I, O, U.",
    ]),
    ("MATEMÁTICA", "Conteúdos e Habilidades", [
        "Ler e representa os números naturais de 1 até 10.",
        "Faz contagem oral e reconhecimento dos numerais de 1 até 10.",
        "Estabelece relações espaciais, identificando a posição de pessoas e objetos, "
        "utilizando as noções topológicas: em cima, embaixo, de um lado, do outro lado, na frente, atrás.",
        "Relaciona número (grafia) a sua quantidade.",
        "Demonstra conhecimento acerca de ideias comparativas: grande/pequeno; dentro/fora; "
        "aberto/fechado; leve/pesado; cheio/vazio; mais/menos.",
        "Identifica cores primárias: vermelho, azul e amarelo; secundárias: laranja, verde e roxo; "
        "e outras: preto, branco, rosa, cinza, etc.",
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
    existentes = {tp["nome"]: tp for tp in get_all_topicos()}

    topicos_criados = 0
    temas_criados = 0
    subtemas_criados = 0

    for ordem, (nome_topico, nome_tema, subtemas) in enumerate(ESTRUTURA, start=1):
        topico = existentes.get(nome_topico)
        if topico is None:
            topico = create_topico(nome_topico, ordem=ordem)
            topico["temas"] = []
            topicos_criados += 1
        update_topico_turmas(topico["id"], TURMAS_INFANTIL_3)

        tema_existente = next(
            (t for t in topico.get("temas", []) if t["nome"] == nome_tema), None
        )
        if tema_existente is None:
            tema = create_tema(nome_tema, topico_id=topico["id"])
            tema["subtemas"] = []
            temas_criados += 1
        else:
            tema = tema_existente
        update_tema_turmas(tema["id"], TURMAS_INFANTIL_3)

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
    print("  Seed - Estrutura Avaliativa Infantil 3 (A e B)")
    print("=" * 56)
    result = run_seed()
    print(f"  Tópicos criados:  {result['topicos']}")
    print(f"  Temas criados:    {result['temas']}")
    print(f"  Subtemas criados: {result['subtemas']}")
    print("=" * 56)


if __name__ == "__main__":
    main()
