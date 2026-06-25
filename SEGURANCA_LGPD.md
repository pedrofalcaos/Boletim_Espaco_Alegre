# Mapeamento de Segurança e LGPD — Escola Espaço Alegre

> Relatório técnico do sistema de boletins/relatórios. Lida com **dados de crianças,
> pais e equipe escolar** — categoria que exige cuidado reforçado (LGPD art. 14).
>
> Legenda de status: ✅ implementado neste mapeamento · ⏳ pendente (decisão/ação da escola)

---

## 1. Diagnóstico atual

Stack: **FastAPI + PostgreSQL** (Railway) com fallback JSON local. Sessão por **cookie
assinado** (itsdangerous). Frontend renderizado no servidor (f-strings de HTML).

**Pontos fortes já existentes**
- Senhas com **PBKDF2-HMAC-SHA256**, 260.000 iterações e *salt* por usuário (`auth.py`).
- **SQL 100% parametrizado** (psycopg2 `%s`) — sem injeção de SQL.
- Upload de PDF valida **extensão + assinatura `%PDF-` + tamanho (15 MB)** e bloqueia
  **path traversal** (`db_avaliacao.py:resolver_caminho`).
- Documentação da API desabilitada (`docs_url=None, redoc_url=None`).
- PDFs servidos por **rota controlada** (sem diretório público montado).
- Sessão **expira em 8h**; tokens assinados detectam adulteração.

**Fragilidades tratadas neste mapeamento** (detalhe na seção 4).

---

## 2. Inventário de dados pessoais

| Dado | Categoria | Onde | Quem acessa | Retenção |
|------|-----------|------|-------------|----------|
| Nome, turma, período, matrícula do aluno | Pessoal (criança) | Tabela `alunos` | Equipe + responsável do próprio aluno | Vínculo escolar |
| Notas, frequência, observações | Pessoal (criança) | `alunos` | Equipe + responsável | Vínculo escolar |
| Relatórios semestrais / descrições | Pessoal (criança) | `relatorios_semestrais` | Equipe + responsável | Vínculo escolar |
| Avaliações em PDF | Pessoal (criança) | Pasta `avaliacao_ingles/` + `avaliacoes_pdf` | Equipe + responsável | Vínculo escolar |
| Nome/usuário/senha da equipe | Pessoal | `usuarios` | Sistema (senha = hash) | Enquanto colaborador |
| Logs de acesso (data, documento, dispositivo, **IP parcial**) | Pessoal (navegação) | `acessos_documentos` | Admin/coordenação | Acompanhamento |

**Não há dados sensíveis** (saúde, biometria, etc.) nem coleta de e-mail/telefone de
responsável — **não existe cadastro de responsável**; o acesso é por matrícula.

---

## 3. Mapa de fluxo dos dados

```
RESPONSÁVEL (sem login)                EQUIPE (login + cookie assinado)
   │ digita matrícula                     │ admin / coordenação / professora
   ▼                                       ▼
/boletim /relatorio /avaliacao-ingles    Painel /admin/*  (check_admin/check_staff)
   │  (gate de visibilidade dos pais)      │  CRUD alunos, relatórios, PDFs, usuários
   ▼                                       ▼
   └──> registra acesso (IP parcial) ──> PostgreSQL (Railway)  /  JSON local (dev)
                                          arquivos PDF em disco (avaliacao_ingles/)
```

---

## 4. Riscos encontrados, correções e prioridade

### 🔴 CRÍTICO

1. **Enumeração de matrícula / IDOR — mitigado por rate-limit.** ⚠️ As matrículas são
   **sequenciais** e são o único segredo de acesso do responsável. Decisão da escola: manter o
   acesso por matrícula (sem reemitir QR codes) e aplicar **rate-limit anti-varredura** ✅ —
   um IP que consulta muitas matrículas distintas numa janela é bloqueado (`auth.py:
   consulta_bloqueada`; não afeta a equipe nem famílias com poucos filhos). É uma **mitigação**,
   não eliminação: um atacante com muitos IPs ainda poderia varrer lentamente. Proteção forte
   (2º fator por data de nascimento, ou token por aluno) fica como melhoria futura.

2. **SECRET_KEY / ADMIN_PASSWORD com valor público fixo.** ✅ parcial
   `SECRET_KEY` não usa mais um valor fixo público: deriva uma chave estável do
   `DATABASE_URL` (secreto) quando a env não está definida (`auth.py`). ⏳ **Ação na escola:**
   definir `SECRET_KEY` e `ADMIN_PASSWORD` próprios no Railway e **trocar a senha admin
   padrão** (`escola2026`).

### 🟠 ALTO

3. **Cookie de sessão sem flag `Secure`.** ✅ Agora `Secure` em produção (`COOKIE_SECURE=IS_PROD`)
   — cookie só trafega por HTTPS. Mantém `HttpOnly` + `SameSite=Lax`.
4. **Sem proteção contra força bruta no login.** ✅ Rate-limit em memória (8 falhas/15 min
   por IP) nos logins admin e professora, com mensagem amigável.
5. **Ausência de cabeçalhos de segurança.** ✅ Middleware adiciona `Content-Security-Policy`,
   `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` e
   `HSTS` (em produção).
6. **Páginas com dados pessoais cacheáveis.** ✅ `Cache-Control: private, no-store` em
   `/boletim`, `/relatorio`, `/avaliacao-ingles`, `/admin`, `/professora`.

### 🟡 MÉDIO

7. **XSS armazenado via texto rico do relatório.** ✅ A `descricao_final` agora é **sanitizada**
   (`sanitize.py` com `nh3`): lista branca de tags + `font[color]`, removendo `script`,
   `onerror`/handlers, `style` e `javascript:`. Aplicada ao **salvar** e ao **renderizar**
   (cobre dados antigos). Mantém negrito, itálico, listas, cor.
8. **Logs guardavam IP completo.** ✅ IP agora **anonimizado** (último octeto zerado / prefixo
   /48 em IPv6) — minimização de dados.
9. **Sem política de privacidade.** ✅ Página `/privacidade` (LGPD) criada e linkada no rodapé.

### 🟢 BAIXO

10. **Trilha de auditoria de alterações da equipe.** ✅ `db_auditoria.py` registra quem/quando/o
    quê (cadastro e edição de alunos, confirmação/trancamento de relatórios, vínculos de
    avaliação, visibilidade dos pais, gestão de colaboradoras). Tela `/admin/auditoria`
    (somente admin) com busca.
11. **Mensagem de erro genérica** já é usada no login (sem vazar se o usuário existe) — manter.
12. **`itsdangerous`/dependências** — manter atualizadas (Dependabot/`pip list --outdated`).

---

## 5. Conformidade LGPD — pontos de atenção

- **Base legal:** execução do contrato educacional + legítimo interesse pedagógico — descrito
  na nova política de privacidade. ✅
- **Transparência:** política de privacidade visível. ✅
- **Minimização:** não há coleta excessiva; IP anonimizado. ✅
- **Direitos do titular** (acesso/correção/exclusão): a edição/exclusão de aluno já existe no
  painel; a política indica canal de contato. ⏳ Formalizar procedimento de atendimento.
- **Retenção:** definir prazo formal de descarte ao fim do vínculo. ⏳
- **Dados de crianças (art. 14):** acesso restrito por perfil e por matrícula; reforçar com a
  correção do item crítico nº 1. ⏳

---

## 6. O que foi implementado neste mapeamento

| Arquivo | Mudança |
|---------|---------|
| `auth.py` | SECRET_KEY sem valor público fixo; `COOKIE_SECURE`; rate-limit de login; **rate-limit anti-varredura das consultas dos pais** |
| `main.py` | Middleware de cabeçalhos de segurança + `no-store`; cookies `Secure`; rate-limit nos 2 logins; página `/privacidade`; **bloqueio de varredura nas rotas dos pais (429)**; **sanitização da descrição ao salvar**; **trilha de auditoria nas mutações** + rota `/admin/auditoria` |
| `db_acesso.py` | Anonimização de IP; data/hora em horário de Brasília |
| `sanitize.py` (novo) | Sanitização anti-XSS do texto rico (nh3) |
| `db_auditoria.py` (novo) | Trilha de auditoria (dual backend) |
| `relatorio_print.py`, `templates_relatorio.py` | Sanitização da descrição ao renderizar |
| `templates.py` | Mensagem de bloqueio de login; itens de nav (Auditoria) |

Nenhuma funcionalidade existente foi alterada em comportamento (apenas reforço de segurança).

---

## 7. Checklist final

**Segurança**
- [x] Senhas com hash forte (PBKDF2 + salt)
- [x] SQL parametrizado (sem injeção)
- [x] Upload validado + anti path traversal
- [x] Cookie `HttpOnly` + `SameSite` + `Secure` (prod)
- [x] SECRET_KEY sem valor público fixo
- [x] Rate-limit no login
- [x] Cabeçalhos de segurança (CSP, HSTS, X-Frame-Options, nosniff, Referrer-Policy)
- [x] `no-store` em páginas com dados pessoais
- [x] Rate-limit anti-varredura nas consultas dos pais (mitiga enumeração)
- [x] Sanitização anti-XSS do HTML do relatório
- [x] Trilha de auditoria de alterações da equipe
- [ ] Definir `SECRET_KEY`/`ADMIN_PASSWORD` no Railway e trocar senha admin ⏳ (ação na escola)
- [ ] Proteção forte contra enumeração (2º fator data de nascimento ou token por aluno) ⏳ (melhoria futura)

**LGPD**
- [x] Inventário de dados pessoais (este documento)
- [x] Política de privacidade visível
- [x] Minimização (IP anonimizado, sem dados sensíveis)
- [ ] Procedimento formal de atendimento aos direitos do titular ⏳
- [ ] Prazo formal de retenção/descarte ⏳
