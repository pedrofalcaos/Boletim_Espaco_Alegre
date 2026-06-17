#!/usr/bin/env python3
"""
Seed da estrutura avaliativa (Tópico → Tema → Subtema) da Ed. Infantil 2026.
Escopo: todas as turmas de Infantil 1 a 5 (A e B).
Seguro para rodar múltiplas vezes (idempotente).

Uso:
    python seed_estrutura_avaliativa.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_relatorio import (
    TURMAS_INFANTIL,
    get_all_topicos, create_topico, update_topico_turmas,
    create_tema, update_tema_turmas,
    create_subtema,
)

ESTRUTURA = [
    ("O EU, O OUTRO E O NÓS", "Habilidade", [
        "Reconhece a si mesmo e/ou responde ao próprio nome",
        "Interage com adultos de referência",
        "Interage com outras crianças",
        "Expressa emoções e necessidades",
        "Participa de atividades coletivas",
        "Compartilha objetos com mediação",
        "Respeita combinados simples da rotina",
        "Demonstra empatia e interesse pelo outro",
        "Busca realizar ações de forma independente",
        "Constrói vínculos afetivos no ambiente escolar",
    ]),
    ("ESCUTA, FALA, PENSAMENTO E IMAGINAÇÃO", "Habilidade", [
        "Reage a sons, histórias e músicas",
        "Compreende comandos simples",
        "Utiliza gestos, sons ou palavras para comunicar-se",
        "Amplia o vocabulário gradativamente",
        "Demonstra interesse por livros e imagens",
        "Participa de cantigas e brincadeiras cantadas",
        "Imita sons, palavras e expressões",
        "Expressa ideias e desejos",
        "Participa de brincadeiras simbólicas",
        "Demonstra imaginação em situações lúdicas",
    ]),
    ("TRAÇOS, SONS, CORES E FORMAS", "Habilidade", [
        "Explora diferentes materiais",
        "Manipula objetos com diferentes texturas",
        "Produz marcas gráficas espontâneas",
        "Demonstra interesse por músicas e sons",
        "Participa de atividades artísticas",
        "Explora instrumentos musicais",
        "Observa e aprecia produções visuais",
        "Reconhece ou demonstra interesse por cores",
        "Experimenta diferentes formas de expressão",
        "Cria produções livres",
    ]),
    ("CORPO, GESTOS E MOVIMENTOS", "Habilidade", [
        "Explora diferentes formas de deslocamento",
        "Utiliza gestos para comunicar-se",
        "Imita movimentos",
        "Participa de circuitos e desafios motores",
        "Demonstra equilíbrio compatível com a faixa etária",
        "Desenvolve coordenação motora ampla",
        "Desenvolve coordenação motora fina",
        "Reconhece partes do corpo",
        "Responde corporalmente à música",
        "Movimenta-se com segurança nos espaços",
    ]),
    ("ESPAÇOS, TEMPOS, QUANTIDADES, RELAÇÕES E TRANSFORMAÇÕES", "Habilidade", [
        "Explora o ambiente com curiosidade",
        "Reconhece objetos familiares",
        "Participa da rotina diária",
        "Observa mudanças no ambiente",
        "Manipula objetos para descobrir propriedades",
        "Agrupa ou compara objetos",
        "Demonstra noções espaciais simples",
        "Percebe relações de causa e efeito",
        "Explora experiências e descobertas",
        "Demonstra noções iniciais de quantidade",
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
        update_topico_turmas(topico["id"], TURMAS_INFANTIL)

        tema_existente = next(
            (t for t in topico.get("temas", []) if t["nome"] == nome_tema), None
        )
        if tema_existente is None:
            tema = create_tema(nome_tema, topico_id=topico["id"])
            tema["subtemas"] = []
            temas_criados += 1
        else:
            tema = tema_existente
        update_tema_turmas(tema["id"], TURMAS_INFANTIL)

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
    print("  Seed - Estrutura Avaliativa Ed. Infantil 2026")
    print("=" * 56)
    result = run_seed()
    print(f"  Tópicos criados:  {result['topicos']}")
    print(f"  Temas criados:    {result['temas']}")
    print(f"  Subtemas criados: {result['subtemas']}")
    print("=" * 56)


if __name__ == "__main__":
    main()
