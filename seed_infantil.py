#!/usr/bin/env python3
"""
Seed dos alunos e professoras da Educação Infantil 2026.
Seguro para rodar múltiplas vezes (idempotente).

Uso:
    python seed_infantil.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import upsert_aluno, get_aluno
from db_relatorio import get_all_usuarios, create_usuario


def _fmt(s: str) -> str:
    """Converte CAIXA ALTA para Title Case respeitando conectivos portugueses."""
    conectivos = {'de','da','do','dos','das','e','em','por','a','o','é','ao','às'}
    words = s.strip().lower().split()
    return ' '.join(
        w.capitalize() if i == 0 or w not in conectivos else w
        for i, w in enumerate(words)
    )


# ── Professoras ───────────────────────────────────────────────────────────────

PROFESSORAS = [
    # (nome, username, senha)
    ("Vanessa",  "vanessa@espacoalegre.com",  "EA@2026"),
    ("Erika",    "erika@espacoalegre.com",    "EA@2026"),
    ("Cilene",   "cilene@espacoalegre.com",   "EA@2026"),
    ("Patrícia", "patricia@espacoalegre.com", "EA@2026"),
    ("Fabiana",  "fabiana@espacoalegre.com",  "EA@2026"),
    ("Andrea",   "andrea@espacoalegre.com",   "EA@2026"),
]


# ── Alunos ────────────────────────────────────────────────────────────────────
# (matrícula, nome em CAPS, turma, período, professora)

ALUNOS = [
    # ── Infantil 1 – A · Vanessa · Manhã ──────────────────────────────────────
    ("20261001", "CLARICE LIMA DA SILVA",     "Infantil 1 – A", "Manhã", "Vanessa"),
    ("20261002", "EDUARDO DE LUNA RODRIGUES", "Infantil 1 – A", "Manhã", "Vanessa"),
    ("20261003", "SERENA DANTAS ANTONINO",    "Infantil 1 – A", "Manhã", "Vanessa"),

    # ── Infantil 2 – A · Vanessa · Manhã ──────────────────────────────────────
    ("20262001", "ARTHUR HENRIQUE DE AQUINO ASSUNÇÃO", "Infantil 2 – A", "Manhã", "Vanessa"),
    ("20262002", "AURORA DE SOUZA PEREIRA GOMES",      "Infantil 2 – A", "Manhã", "Vanessa"),
    ("20262003", "BERNARDO NASCIMENTO LINS",            "Infantil 2 – A", "Manhã", "Vanessa"),
    ("20262004", "DAVI QUINTELA ANDRADE",               "Infantil 2 – A", "Manhã", "Vanessa"),
    ("20262005", "FANNY LUÍZA CAVALCANTI AMORIM",       "Infantil 2 – A", "Manhã", "Vanessa"),
    ("20262006", "GABRIEL LUCAS DA SILVA MARQUES",      "Infantil 2 – A", "Manhã", "Vanessa"),
    ("20262007", "HEITOR GOMES CAVALCANTI",             "Infantil 2 – A", "Manhã", "Vanessa"),
    ("20262008", "JOÃO GUILHERME LIRA MARQUES",         "Infantil 2 – A", "Manhã", "Vanessa"),
    ("20262009", "LAURA ALVES DE MACÊDO",               "Infantil 2 – A", "Manhã", "Vanessa"),
    ("20262010", "LAURA CORREIA SALES",                 "Infantil 2 – A", "Manhã", "Vanessa"),
    ("20262011", "RAVI DA SILVA ESMERALDO",             "Infantil 2 – A", "Manhã", "Vanessa"),
    ("20262012", "SAMUEL MARCELINO DE ARAÚJO",          "Infantil 2 – A", "Manhã", "Vanessa"),

    # ── Infantil 1 – B · Erika · Tarde ───────────────────────────────────────
    ("20261101", "FRANCISCO SANTOS SIMÕES DE SIQUEIRA", "Infantil 1 – B", "Tarde", "Erika"),
    ("20261102", "GREGÓRIO MATIAS DE ANDRADE GADÊLHA",  "Infantil 1 – B", "Tarde", "Erika"),
    ("20261103", "MARIA ISADORA SANTOS DE ALMEIDA",     "Infantil 1 – B", "Tarde", "Erika"),

    # ── Infantil 2 – B · Erika · Tarde ───────────────────────────────────────
    ("20262101", "BERNARDO QUEIROZ MOUSINHO",                     "Infantil 2 – B", "Tarde", "Erika"),
    ("20262102", "CLARICE CHAVES FALCÃO",                         "Infantil 2 – B", "Tarde", "Erika"),
    ("20262103", "DAVI COSTA REGO GERMANO",                       "Infantil 2 – B", "Tarde", "Erika"),
    ("20262104", "GABRIEL LEITE GALINDO CARVALHO DE FRANÇA",      "Infantil 2 – B", "Tarde", "Erika"),
    ("20262105", "ISABEL WOOLLEY BEZERRA VILANOVA",               "Infantil 2 – B", "Tarde", "Erika"),
    ("20262106", "JOAQUIM DE JESUS FERREIRA SILVA",               "Infantil 2 – B", "Tarde", "Erika"),
    ("20262107", "MARIA ALICE DE NADAL ALVES DE MELO",            "Infantil 2 – B", "Tarde", "Erika"),
    ("20262108", "MARIA VIOLET TAVARES GUERREIRO",                "Infantil 2 – B", "Tarde", "Erika"),
    ("20262109", "SAMUEL VIOLET TAVARES GUERREIRO",               "Infantil 2 – B", "Tarde", "Erika"),
    ("20262110", "SARAH PEDROZA AFONSO FERREIRA DE MENEZES",      "Infantil 2 – B", "Tarde", "Erika"),
    ("20262111", "SOFIA CARVALHO DO NASCIMENTO",                  "Infantil 2 – B", "Tarde", "Erika"),

    # ── Infantil 3 – A · Cilene · Manhã ──────────────────────────────────────
    ("20263001", "GABRIEL DE SOUZA BARBOZA",        "Infantil 3 – A", "Manhã", "Cilene"),
    ("20263002", "HEITOR DE FREITAS CAVALCANTI",    "Infantil 3 – A", "Manhã", "Cilene"),
    ("20263003", "JOÃO FELIPE MESQUITA RODRIGUES",  "Infantil 3 – A", "Manhã", "Cilene"),
    ("20263004", "LUCAS MEDEIROS FERREIRA LIMA",    "Infantil 3 – A", "Manhã", "Cilene"),
    ("20263005", "MANUELA DE VASCONCELOS SIQUEIRA", "Infantil 3 – A", "Manhã", "Cilene"),
    ("20263006", "MARIA CECÍLIA DE LIRA SOUZA",     "Infantil 3 – A", "Manhã", "Cilene"),
    ("20263007", "MARIA LETÍCIA GUERRA SALES",      "Infantil 3 – A", "Manhã", "Cilene"),
    ("20263008", "MARTIN LUCAS AZEVEDO ALMEIDA",    "Infantil 3 – A", "Manhã", "Cilene"),
    ("20263009", "RENÊ OLIVEIRA SILVA",             "Infantil 3 – A", "Manhã", "Cilene"),

    # ── Infantil 3 – B · Cilene · Tarde ──────────────────────────────────────
    ("20263101", "EMANUEL JOSÉ DE MORAIS E SILVA SANTANA", "Infantil 3 – B", "Tarde", "Cilene"),
    ("20263102", "GABRIEL DE MOURA MARX",                  "Infantil 3 – B", "Tarde", "Cilene"),
    ("20263103", "ISADORA MELO REY OLIVEIRA",              "Infantil 3 – B", "Tarde", "Cilene"),
    ("20263104", "LARISSA AGUIAR PEDROSA DE MELO",         "Infantil 3 – B", "Tarde", "Cilene"),
    ("20263105", "PEDRO GAEL DE LIRA GUEDES",              "Infantil 3 – B", "Tarde", "Cilene"),
    ("20263106", "RUI MORAIS CORRÊA DE ARAÚJO",            "Infantil 3 – B", "Tarde", "Cilene"),
    ("20263107", "YURI VIEIRA MACHADO",                    "Infantil 3 – B", "Tarde", "Cilene"),

    # ── Infantil 4 – A · Patrícia · Manhã ────────────────────────────────────
    ("20264001", "ADAM ALEIXO PEREIRA",                    "Infantil 4 – A", "Manhã", "Patrícia"),
    ("20264002", "ATHOS CAVALCANTI DE BARROS LIMA",        "Infantil 4 – A", "Manhã", "Patrícia"),
    ("20264003", "ELIS LIMA BENÉ ASSIS",                   "Infantil 4 – A", "Manhã", "Patrícia"),
    ("20264004", "ELISA MAGALHÃES NOGUEIRA",               "Infantil 4 – A", "Manhã", "Patrícia"),
    ("20264005", "GABRIEL CAMILO MATTOS GALVÃO",           "Infantil 4 – A", "Manhã", "Patrícia"),
    ("20264006", "HELOÍSA RODRIGUES VILELA",               "Infantil 4 – A", "Manhã", "Patrícia"),
    ("20264007", "LEONARDO BENÍCIO GONÇALO COELHO",        "Infantil 4 – A", "Manhã", "Patrícia"),
    ("20264008", "MARIA LUÍSA ALVES SOUZA",                "Infantil 4 – A", "Manhã", "Patrícia"),
    ("20264009", "MATTEO OLIVEIRA DA VEIGA PESSOA",        "Infantil 4 – A", "Manhã", "Patrícia"),
    ("20264010", "MATEUS BEZERRA GUSMÃO",                  "Infantil 4 – A", "Manhã", "Patrícia"),
    ("20264011", "MIGUEL CAVALCANTI DE ALBUQUERQUE ROCHA", "Infantil 4 – A", "Manhã", "Patrícia"),

    # ── Infantil 4 – B · Fabiana · Tarde ─────────────────────────────────────
    ("20264101", "ANA BEATRIZ SOUSA MOURA LIMA",         "Infantil 4 – B", "Tarde", "Fabiana"),
    ("20264102", "HELENA ALMEIDA LUCENA BARBOSA",        "Infantil 4 – B", "Tarde", "Fabiana"),
    ("20264103", "MANUELA LINS IMBELLONI",               "Infantil 4 – B", "Tarde", "Fabiana"),
    ("20264104", "MARIA CELINA PEDROSA RIBEIRO COELHO",  "Infantil 4 – B", "Tarde", "Fabiana"),
    ("20264105", "PAULO HENRIQUE ARAÚJO DE GODOY BRITO", "Infantil 4 – B", "Tarde", "Fabiana"),

    # ── Infantil 5 – A · Andrea · Manhã ──────────────────────────────────────
    ("20265001", "ANTHONY ANGELIM SOARES",                "Infantil 5 – A", "Manhã", "Andrea"),
    ("20265002", "BEATRIZ DA SILVA SANTOS",               "Infantil 5 – A", "Manhã", "Andrea"),
    ("20265003", "BERNARDO FALCÃO MELO VASCONCELOS",      "Infantil 5 – A", "Manhã", "Andrea"),
    ("20265004", "GUILHERME NUNES PEREIRA",               "Infantil 5 – A", "Manhã", "Andrea"),
    ("20265005", "ISABELA SIMÕES DE SIQUEIRA CAVALCANTE", "Infantil 5 – A", "Manhã", "Andrea"),
    ("20265006", "JOAQUIM PARAÍSO CAMPOS DE ARAÚJO",      "Infantil 5 – A", "Manhã", "Andrea"),
    ("20265007", "JÚLIA BEZERRA MARIANO",                 "Infantil 5 – A", "Manhã", "Andrea"),
    ("20265008", "JULIA GAMA BELTRÃO",                    "Infantil 5 – A", "Manhã", "Andrea"),
    ("20265009", "MARIA LAURA COSTA ROCHA",               "Infantil 5 – A", "Manhã", "Andrea"),
    ("20265010", "NOAH PEREIRA PARRA ARAUJO",             "Infantil 5 – A", "Manhã", "Andrea"),
    ("20265011", "SOFIA DE ARAÚJO DUARTE RICARDO",        "Infantil 5 – A", "Manhã", "Andrea"),
    ("20265012", "THÉO DE PAULA VIEIRA DOS ANJOS",        "Infantil 5 – A", "Manhã", "Andrea"),
    ("20265013", "YASMIN ANGELIM SOARES",                 "Infantil 5 – A", "Manhã", "Andrea"),
]


def run_seed() -> dict:
    """
    Executa o seed de forma idempotente.
    Retorna contadores para exibição no admin.
    """
    existentes = {u["username"] for u in get_all_usuarios()}
    prof_criadas = 0
    for nome, username, senha in PROFESSORAS:
        if username not in existentes:
            create_usuario(username, senha, nome, role="professora")
            prof_criadas += 1

    alunos_criados = 0
    for mat, nome_caps, turma, periodo, professora in ALUNOS:
        if get_aluno(mat) is None:
            upsert_aluno(mat, {
                "nome":       _fmt(nome_caps),
                "turma":      turma,
                "periodo":    periodo,
                "professora": professora,
                "ano_letivo": "2026",
                "notas":      {},
                "frequencia": {"total_aulas": "", "total_faltas": ""},
                "observacoes":"",
            })
            alunos_criados += 1

    return {"professoras": prof_criadas, "alunos": alunos_criados}


def main():
    print("=" * 56)
    print("  Seed - Educacao Infantil 2026 - Espaco Alegre")
    print("=" * 56)
    result = run_seed()
    print(f"  Professoras criadas: {result['professoras']}")
    print(f"  Alunos criados:      {result['alunos']}")
    print("=" * 56)
    print(f"  Seed concluido: {len(ALUNOS)} alunos, {len(PROFESSORAS)} professoras")
    print(f"{'=' * 56}\n")


if __name__ == "__main__":
    main()
