# Escola Espaço Alegre — Plataforma Escolar Digital

Sistema web completo para gestão escolar de uma escola de Educação Infantil e Fundamental, cobrindo boletins online, relatórios semestrais por competência, painel administrativo, área de professoras, coordenação e portal do responsável. Desenvolvido com Python + FastAPI, implantado em produção no Railway com PostgreSQL.

> Construído de forma iterativa com o auxílio de IA (Claude Sonnet) como ferramenta de aceleração — o design de produto, as decisões de arquitetura e a curadoria de qualidade foram conduzidos pelo desenvolvedor ao longo de todo o processo.

---

## Índice

1. [Visão geral do produto](#visão-geral-do-produto)
2. [Funcionalidades por perfil](#funcionalidades-por-perfil)
3. [Design System — Liquid Glass](#design-system--liquid-glass)
4. [Arquitetura](#arquitetura)
5. [Módulos do backend](#módulos-do-backend)
6. [Segurança](#segurança)
7. [Banco de dados e deploy](#banco-de-dados-e-deploy)
8. [Stack tecnológica](#stack-tecnológica)
9. [Rodando localmente](#rodando-localmente)
10. [Variáveis de ambiente](#variáveis-de-ambiente)
11. [Estrutura de arquivos](#estrutura-de-arquivos)

---

## Visão geral do produto

A escola precisava substituir boletins e relatórios em papel por um sistema digital acessível para pais, professoras e a equipe de gestão. O resultado é uma aplicação web responsiva com três camadas distintas:

| Camada | Acesso | Objetivo |
|---|---|---|
| **Portal do Responsável** | Público (por matrícula) | Consultar boletim e relatório do filho sem login |
| **Área da Professora** | Login por professora | Preencher e confirmar relatórios da sua turma |
| **Painel Admin / Coordenação** | Login autenticado | Gestão completa: alunos, notas, relatórios, usuários |

---

## Funcionalidades por perfil

### Responsável (pai/mãe)
- Consulta o boletim de notas do filho via número de matrícula
- Acessa o relatório semestral de competências (Ed. Infantil)
- Visualiza foto do aluno, turma, período e histórico de notas por bimestre
- Lê a avaliação de Inglês por semestre com escala descritiva
- Tudo responsivo para mobile — sem necessidade de app ou login

### Professora
- Login seguro com troca de senha obrigatória no primeiro acesso
- Dashboard com lista de turmas e status dos relatórios (Pendente / Em andamento / Concluído)
- Preenchimento dos relatórios semestrais por competência (tópico → tema → subtema), com escala CA / CC / ED
- Editor de texto rico para a descrição narrativa final do relatório
- Confirmação do relatório (bloqueio de edição após envio)
- Visualização do boletim dos próprios alunos

### Coordenação
- Mesmas permissões da professora, mas pode visualizar e editar relatórios de **qualquer turma**
- Pode imprimir relatórios avulsos, por turma ou todos de uma vez
- Acesso ao controle de trava/destrava dos relatórios

### Administrador
- Gestão completa de alunos (Fundamental e Ed. Infantil)
- Cadastro/edição/remoção de professoras e coordenadoras
- Reset de senha temporária para colaboradoras
- Controle da estrutura avaliativa (tópicos → temas → subtemas por turma)
- Lançamento de notas e avaliações de Inglês (upload em lote ou manual)
- Upload de fotos via Cloudinary com recortador interativo (zoom + arrastar)
- Painel de relatórios com filtros por turma, semestre e status
- Trava em massa de relatórios por semestre
- Impressão em lote: todos os relatórios de um semestre / turma como PDF
- Trilha de auditoria com registro de todas as ações da equipe
- Histórico de acessos dos responsáveis (quem abriu qual documento e quando)
- Controle de visibilidade de campos nos boletins por turma
- Dark mode e player de música ambiente na interface

---

## Design System — Liquid Glass

A interface segue a linguagem visual **Liquid Glass**, inspirada nas interfaces Apple 2025/WWDC25, implementada 100% com CSS nativo sem nenhuma dependência de framework UI.

**Componentes do design system (`design_system.py`):**

- **Glassmorphism**: `backdrop-filter: blur(22px) saturate(180%)` com bordas semi-translúcidas e highlight de borda (`inset 0 1px 0 rgba(255,255,255,.65)`) em cartões, topbars e modais
- **Background animado**: 3 blobs coloridos com `filter: blur(60px)`, animados com `@keyframes lg-float` e respeitando `prefers-reduced-motion`
- **Tokens CSS (`:root`)**: escala tipográfica (`--fs-display` a `--fs-label`), espaçamento em múltiplos de 4px, raios padronizados (`--radius-sm/md/lg/pill`) e sombras nomeadas
- **Retrofit de contraste**: seletores de atributo CSS (`[style*="color:#aaa"]`) com `!important` para corrigir cores de baixo contraste em toda a base de código sem tocar cada arquivo individualmente
- **Tipografia**: Plus Jakarta Sans (corpo) + Fredoka One (headings/branding) via Google Fonts
- **Ícones SVG inline** (`icons.py`): biblioteca própria de ícones outline (estilo Lucide/Heroicons) para substituir emojis nos botões de ação, garantindo consistência cross-platform
- **Acessibilidade**: `:focus-visible` para todos os controles interativos, `aria-label` e `role="alert"` nos pontos críticos, contraste mínimo WCAG AA
- **Print-safety**: `@media print` desativa blobs, glassmorphism e o player de música, restaurando fundo branco para impressão fiel

---

## Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                            │
└──────────────┬───────────────────────────────────┬──────────┘
               │ HTTPS                             │ HTTPS
    ┌──────────▼───────────┐         ┌─────────────▼──────────┐
    │  Responsável (pai)   │         │  Equipe (staff)        │
    │  /  /boletim  /rel.  │         │  /admin  /professora   │
    └──────────┬───────────┘         └─────────────┬──────────┘
               │                                   │
    ┌──────────▼───────────────────────────────────▼──────────┐
    │                    FastAPI (main.py)                     │
    │  • Rate-limit anti-varredura (in-memory sliding window)  │
    │  • Cookie de sessão assinado (itsdangerous, 8h TTL)      │
    │  • Content-Security-Policy header em todas as respostas  │
    │  • Sanitização de HTML rico com nh3 (allowlist)          │
    └────┬──────────┬────────────┬─────────────┬──────────────┘
         │          │            │             │
    ┌────▼────┐ ┌───▼────┐ ┌────▼────┐ ┌─────▼──────┐
    │  db.py  │ │db_rel. │ │db_acesso│ │db_auditoria│
    │ Alunos  │ │Relat.  │ │Acessos  │ │Trilha ações│
    │ Notas   │ │Semest. │ │pais     │ │staff       │
    └────┬────┘ └───┬────┘ └────┬────┘ └─────┬──────┘
         │          │            │             │
    ┌────▼──────────▼────────────▼─────────────▼──────┐
    │            PostgreSQL (Railway)                  │
    │     ou JSON local (desenvolvimento)              │
    └──────────────────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  Cloudinary  │
                    │ Fotos alunos │
                    │ e equipe     │
                    └─────────────┘
```

**Padrão de dual-backend (PostgreSQL / JSON):**

Cada módulo de persistência detecta `DATABASE_URL` em tempo de importação e registra duas implementações completas da mesma interface — uma com `psycopg2` e uma com `json` + `threading.Lock`. Isso permite desenvolver e testar localmente sem nenhuma dependência externa, e em produção o mesmo código usa PostgreSQL sem nenhuma alteração.

---

## Módulos do backend

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | ~80 rotas FastAPI, middleware de segurança, rate-limit, registro de acessos e auditoria |
| `auth.py` | Sessões assinadas (itsdangerous), roles (admin/professora/coordenacao), senhas temporárias |
| `db.py` | CRUD de alunos, notas por disciplina/bimestre, visibilidade de campos |
| `db_relatorio.py` | Relatórios semestrais, tópicos/temas/subtemas, usuários, lock/unlock, impressão |
| `db_avaliacao.py` | Avaliações de Inglês por semestre, upload em lote |
| `db_acesso.py` | Histórico de acessos dos responsáveis com IP, timestamp e documento consultado |
| `db_auditoria.py` | Trilha imutável de ações da equipe (quem, o quê, quando) |
| `db_foto.py` | Persistência das URLs de foto no banco (Cloudinary) |
| `fotos_cloud.py` | Upload para Cloudinary com crop inteligente e fallback de avatar por iniciais |
| `boletim_html.py` | Geração do HTML do boletim (cálculo de médias, layout de impressão) |
| `relatorio_print.py` | HTML otimizado para impressão dos relatórios semestrais (individual e em lote) |
| `templates.py` | Shell de página, dashboard admin, formulário de aluno, login |
| `templates_admin_extras.py` | Telas de professoras, relatórios, temas avaliativos, auditoria, acessos |
| `templates_professora.py` | Dashboard, lista de turmas e botões de ação da professora |
| `templates_relatorio.py` | Formulário de preenchimento do relatório (editor rico + escala CA/CC/ED) |
| `design_system.py` | Liquid Glass CSS, fontes, tokens, blobs animados |
| `icons.py` | Biblioteca de ícones SVG inline (outline, 14px padrão) |
| `sanitize.py` | Sanitização de HTML rico com `nh3` (allowlist de tags/atributos) |
| `music_player.py` | Widget de player de música flutuante, com print-safety |
| `foto_cropper.py` | Interface de recorte de foto com zoom e drag antes do upload |
| `auth.py` | Sessões assinadas com itsdangerous, TTL de 8h, HTTPS-only em produção |

---

## Segurança

| Camada | Implementação |
|---|---|
| **Autenticação** | Cookie de sessão assinado com HMAC (itsdangerous) — sem JWT, sem localStorage |
| **Autorização** | Checagem de role em cada rota (`check_admin`, `check_staff`, `check_session`) |
| **Rate-limit** | Sliding window in-memory por IP para consultas públicas de matrícula (anti-varredura) — HTTP 429 com página amigável |
| **XSS armazenado** | Sanitização de HTML rico com `nh3` antes de persistir descrições de relatório |
| **Content-Security-Policy** | Header CSP em todas as respostas, restringindo `script-src`, `img-src` (Cloudinary) e `frame-src` |
| **HTTPS-only cookies** | `Secure=True` nos cookies de sessão quando `DATABASE_URL` está definida (produção) |
| **Chave derivada** | Em produção sem `SECRET_KEY` explícita, a chave é derivada do `DATABASE_URL` via SHA-256 — nunca hardcoded |
| **Senhas temporárias** | Geradas com `secrets.choice` sobre alfabeto sem ambiguidade visual (sem 0/O/1/l/I) |
| **Trilha de auditoria** | Toda ação da equipe (criar, editar, excluir, trancar, imprimir) é registrada com usuário, role, alvo e timestamp (fuso Brasília) |

---

## Banco de dados e deploy

### Dual-backend automático

```python
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # PostgreSQL — psycopg2
    ...
else:
    # JSON local — threading.Lock()
    ...
```

Todos os módulos (`db.py`, `db_relatorio.py`, `db_acesso.py`, `db_auditoria.py`) seguem esse padrão. O schema PostgreSQL é criado automaticamente com `CREATE TABLE IF NOT EXISTS` na primeira conexão.

### Deploy no Railway

1. Fork/push para GitHub
2. New Project → Deploy from GitHub repo
3. Add PostgreSQL plugin → `DATABASE_URL` é injetada automaticamente
4. Adicionar variáveis: `SECRET_KEY`, `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## Stack tecnológica

### Backend
| Tecnologia | Uso |
|---|---|
| **Python 3.11+** | Linguagem principal |
| **FastAPI** | Framework web assíncrono, rotas, formulários, arquivos estáticos |
| **Uvicorn** | Servidor ASGI de produção |
| **psycopg2** | Driver PostgreSQL |
| **itsdangerous** | Assinatura HMAC dos cookies de sessão |
| **nh3** | Sanitização de HTML (bindings Rust do Ammonia) |
| **cloudinary** | SDK de upload e gestão de imagens |

### Frontend
| Tecnologia | Uso |
|---|---|
| **HTML + CSS puro** | Sem framework UI — todo o design é CSS nativo com variáveis customizadas |
| **CSS Glassmorphism** | `backdrop-filter`, `rgba`, sombras em camadas |
| **Google Fonts** | Plus Jakarta Sans + Fredoka One |
| **Vanilla JS** | Interações: modal de impressão, recortador de foto, player de música, dark mode, sidebar |
| **SVG inline** | Ícones próprios no estilo Lucide/Heroicons |

### Infraestrutura
| Tecnologia | Uso |
|---|---|
| **Railway** | Plataforma de deploy (PaaS), PostgreSQL managed |
| **Cloudinary** | CDN e armazenamento de imagens com transformações |
| **GitHub** | Versionamento |

---

## Rodando localmente

```bash
# 1. Clonar
git clone https://github.com/pedrofalcaos/Boletim_Espaco_Alegre.git
cd Boletim_Espaco_Alegre

# 2. Ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 3. Dependências
pip install fastapi uvicorn psycopg2-binary itsdangerous nh3 cloudinary

# 4. Rodar (sem banco — usa JSON local)
uvicorn main:app --reload

# Acesse http://localhost:8000
# Login admin: usuario=admin / senha=escola2026
```

> Sem `DATABASE_URL`, o sistema cria `banco.json` e `banco_relatorio.json` automaticamente. **Não commite esses arquivos** — contêm dados de alunos.

---

## Variáveis de ambiente

| Variável | Obrigatória em prod | Descrição |
|---|---|---|
| `DATABASE_URL` | Sim | Connection string PostgreSQL (Railway injeta automaticamente) |
| `SECRET_KEY` | Recomendada | Chave de assinatura dos cookies. Se ausente, derivada do `DATABASE_URL` |
| `ADMIN_USER` | Não | Username do admin padrão (default: `admin`) |
| `ADMIN_PASSWORD` | Sim | Senha do admin (default fraco: `escola2026`) |
| `CLOUDINARY_CLOUD_NAME` | Para fotos | Nome do cloud no Cloudinary |
| `CLOUDINARY_API_KEY` | Para fotos | Chave da API Cloudinary |
| `CLOUDINARY_API_SECRET` | Para fotos | Secret da API Cloudinary |

---

## Estrutura de arquivos

```
boletim_v2/
├── main.py                    # Rotas FastAPI (~80 endpoints)
├── auth.py                    # Autenticação e sessões
├── db.py                      # CRUD alunos/notas (PostgreSQL + JSON)
├── db_relatorio.py            # CRUD relatórios, usuários, estrutura avaliativa
├── db_avaliacao.py            # Avaliações de Inglês
├── db_acesso.py               # Log de acessos dos responsáveis
├── db_auditoria.py            # Trilha de auditoria da equipe
├── db_foto.py                 # Persistência de URLs de foto
├── fotos_cloud.py             # Integração Cloudinary
├── boletim_html.py            # Geração HTML do boletim (Fundamental)
├── relatorio_print.py         # HTML de impressão dos relatórios (Ed. Infantil)
├── templates.py               # Shell, admin dashboard, login, formulários
├── templates_admin_extras.py  # Professoras, relatórios, temas, auditoria
├── templates_professora.py    # Área da professora
├── templates_relatorio.py     # Formulário de relatório semestral
├── design_system.py           # Liquid Glass CSS, tokens, fontes, blobs
├── icons.py                   # Ícones SVG inline
├── sanitize.py                # Sanitização de HTML rico (nh3)
├── music_player.py            # Widget de player de música
├── foto_cropper.py            # UI de recorte de foto
├── dados.py                   # Dados de seed (estrutura inicial)
├── seed_*.py                  # Scripts de seed da estrutura avaliativa
├── static/
│   ├── logo.png               # Logo com transparência
│   ├── favicon.png
│   └── musica_escola.mp3
└── banco.json                 # Gerado localmente (não versionado)
```

---

## Fluxo de dados — Relatório Semestral

```
Admin cria estrutura avaliativa
  └── Tópico (ex: "Linguagem e Comunicação")
        └── Tema (ex: "Expressão Oral")
              └── Subtema (ex: "Participa de rodas de conversa")
                    └── Associado a turmas específicas

Professora acessa /professora/relatorio/{matricula}/{semestre}
  └── Vê formulário gerado dinamicamente pela estrutura acima
  └── Preenche CA / CC / ED para cada subtema
  └── Escreve descrição narrativa no editor rico
  └── Confirma o relatório (status: concluido)

Admin/Coordenação revisa
  └── Pode editar, trancar (bloqueia edição), reabrir ou imprimir
  └── Impressão em lote: todos os relatórios de um semestre/turma

Responsável acessa /relatorio/{matricula}
  └── Vê o relatório do filho em HTML responsivo
  └── Pode imprimir como PDF pelo browser
```

---

## Créditos

Desenvolvido por **Pedro Falcão** para a **Escola Espaço Alegre**.

A inteligência artificial (Claude Sonnet — Anthropic) foi utilizada como ferramenta de aceleração de desenvolvimento em pares: geração de código, revisão de bugs, sugestões de arquitetura e implementação de design. Todas as decisões de produto, curadoria de qualidade e gestão do projeto foram conduzidas pelo desenvolvedor.
