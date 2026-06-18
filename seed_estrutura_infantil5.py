#!/usr/bin/env python3
"""
Seed da estrutura avaliativa (Tópico → Tema → Subtema) específica do Infantil 5.
Escopo: apenas Infantil 5 – A.
Seguro para rodar múltiplas vezes (idempotente).

Uso:
    python seed_estrutura_infantil5.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_relatorio import (
    get_all_topicos, create_topico, update_topico_turmas,
    create_tema, update_tema_turmas,
    create_subtema,
)

TURMAS_INFANTIL_5 = ["Infantil 5 – A"]

ESTRUTURA = [
    ("EIXO COMPORTAMENTAL/ATITUDINAL", "Conteúdos e Habilidades", [
        "Dialoga com os outros a fim de exprimir sentimentos, opiniões, etc.",
        "Explora e descreve diferenças e semelhanças entre objetos.",
    ]),
    ("LINGUAGEM ORAL", "Conteúdos e Habilidades", [
        "Expressa ideias, desejos e sentimentos sobre suas vivências por meio da linguagem oral.",
        "Compreende e transmite avisos, recados e mensagens.",
        "Identifica e reproduz oralmente textos literários e de tradição cultural.",
        "Faz relação grafofônica dos padrões estudados.",
    ]),
    ("LINGUAGEM ESCRITA", "Conteúdos e Habilidades", [
        "Identifica visual e auditivamente as letras do alfabeto.",
        "Classifica e identifica letras, números, símbolos e sinais.",
        "Identifica e agrupa por semelhança palavras que comecem ou terminem com a mesma letra e/ou sílaba.",
        "Identifica e reconhece seu nome completo.",
        "Escreve seu nome completo e o dos seus colegas de sala.",
        "Reconhece foneticamente e graficamente palavras que possuam os padrões silábicos estudados.",
    ]),
    ("MATEMÁTICA", "Conteúdos e Habilidades", [
        "Identifica e nomeia os numerais.",
        "Relaciona quantidade ao numeral trabalhando o agrupamento.",
        "Registra de maneira próxima à convencional os numerais.",
        "Conhece os números e desenvolve a contagem de 1 até 10.",
        "Conhece os números e desenvolve a contagem de 10 até 20.",
        "Conhece os números e desenvolve a contagem de 20 até 30.",
        "Ordena os numerais (ordem crescente e decrescente).",
        "Reconhece o número maior e menor.",
        "Identifica numa série a posição de um objeto ou número, demonstrando noção de "
        "antecessor e sucessor.",
        "Identifica e nomeia as formas geométricas (círculo, quadrado, triângulo e retângulo).",
        "Reconhece e compara diferentes grandezas.",
        "Compara grandezas utilizando conceitos como mais/menos, muito/pouco, maior/menor e igual/diferente.",
        "Identifica diferenças e semelhanças entre sólidos geométricos e figuras planas.",
        "Compara elementos do meio para relações entre leve e pesado, cheio e vazio, "
        "grande/pequeno e maior/menor.",
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
    # de mesmo nome usados por outras turmas (ex: Infantil 3/4).
    topicos_existentes = get_all_topicos()

    topicos_criados = 0
    temas_criados = 0
    subtemas_criados = 0

    for ordem, (nome_topico, nome_tema, subtemas) in enumerate(ESTRUTURA, start=1):
        topico = next(
            (tp for tp in topicos_existentes
             if tp["nome"] == nome_topico and (tp.get("turmas") or []) == TURMAS_INFANTIL_5),
            None,
        )
        if topico is None:
            topico = create_topico(nome_topico, ordem=ordem)
            topico["temas"] = []
            topicos_criados += 1
        update_topico_turmas(topico["id"], TURMAS_INFANTIL_5)

        tema_existente = next(
            (t for t in topico.get("temas", []) if t["nome"] == nome_tema), None
        )
        if tema_existente is None:
            tema = create_tema(nome_tema, topico_id=topico["id"])
            tema["subtemas"] = []
            temas_criados += 1
        else:
            tema = tema_existente
        update_tema_turmas(tema["id"], TURMAS_INFANTIL_5)

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
    print("  Seed - Estrutura Avaliativa Infantil 5 (A)")
    print("=" * 56)
    result = run_seed()
    print(f"  Tópicos criados:  {result['topicos']}")
    print(f"  Temas criados:    {result['temas']}")
    print(f"  Subtemas criados: {result['subtemas']}")
    print("=" * 56)


if __name__ == "__main__":
    main()
