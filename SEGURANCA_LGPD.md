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

1. **Enumeração de matrícula / IDOR (não corrigido — decisão de produto).** ⏳
   As matrículas são **sequenciais** (`20261001`, `20261002`…) e são o **único segredo**
   de acesso do responsável. Qualquer pessoa pode iterar e abrir boletim, relatório e PDF
   de **qualquer criança**. O `matriculas.csv` inclusive contém links públicos prontos.
   *Recomendações (escolher uma):* (a) exigir um 2º fator simples conhecido só pela família
   (ex.: data de nascimento do aluno) antes de exibir; (b) trocar a URL por **token
   aleatório por aluno** (o QR já distribuído passaria a apontar para o token); (c)
   manter por matrícula mas com rate-limit por IP nas consultas. — *Posso implementar a opção
   escolhida; afeta os QR codes já distribuídos, por isso não alterei sozinho.*

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

7. **XSS armazenado via texto rico do relatório.** ⏳ `descricao_final` é renderizada como
   **HTML cru** para o responsável (editor de texto rico da professora). Conta-corrente
   entre usabilidade e risco: se uma conta de professora for comprometida, é um vetor de XSS.
   *Recomendação:* sanitizar o HTML no salvamento (ex.: lista branca de tags com `bleach` ou
   `nh3`). Não apliquei para não alterar a formatação existente sem validação.
8. **Logs guardavam IP completo.** ✅ IP agora **anonimizado** (último octeto zerado / prefixo
   /48 em IPv6) — minimização de dados.
9. **Sem política de privacidade.** ✅ Página `/privacidade` (LGPD) criada e linkada no rodapé.

### 🟢 BAIXO

10. **Sem trilha de auditoria de alterações da equipe** (quem editou nota/relatório). ⏳
    Há `editado_por_nome` em relatórios; estender a um log de auditoria geral é desejável.
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
| `auth.py` | SECRET_KEY sem valor público fixo; `COOKIE_SECURE`; rate-limit de login |
| `main.py` | Middleware de cabeçalhos de segurança + `no-store`; cookies `Secure`; rate-limit nos 2 logins; página `/privacidade`; link no rodapé |
| `db_acesso.py` | Anonimização de IP nos registros de acesso |
| `templates.py`, `templates_professora.py` | Mensagem de bloqueio por excesso de tentativas |

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
- [ ] Corrigir enumeração de matrícula (item crítico nº 1) ⏳
- [ ] Definir `SECRET_KEY`/`ADMIN_PASSWORD` no Railway e trocar senha admin ⏳
- [ ] Sanitizar HTML do relatório (anti-XSS armazenado) ⏳
- [ ] Trilha de auditoria de alterações da equipe ⏳

**LGPD**
- [x] Inventário de dados pessoais (este documento)
- [x] Política de privacidade visível
- [x] Minimização (IP anonimizado, sem dados sensíveis)
- [ ] Procedimento formal de atendimento aos direitos do titular ⏳
- [ ] Prazo formal de retenção/descarte ⏳
