---
name: categorize-modifications
description: >-
  Use this skill to categorize codebase modifications by functionality and create a plan to commit them.
  It analyzes line-by-line changes, groups them following the conventional commits standard,
  proposes a commit plan, waits for user approval, and then executes the commits.
---

# Categorize and Commit Modifications

This skill analyzes current modifications, groups them by functional intent, creates an implementation plan proposing individual commits, and executes them upon user approval.

## Workflow

### 1. Retrieve Modifications
- Use `git diff` and `git diff --cached` to gather all current modifications.

### 2. Granular Analysis & Grouping
- Carefully analyze the diffs line-by-line or hunk-by-hunk.
- **CRITICAL**: Do NOT summarize changes file by file. Group the scattered changes into cohesive functional features or fixes (e.g., changes across `ui.py` and `manager.py` for a single feature go together).
- Assign a conventional commit type to each grouped functionality (`feat`, `fix`, `refactor`, `chore`, `docs`, etc.).

### 3. Create a Commit Plan (Planning Mode)
- Crie ou atualize o artefato `implementation_plan.md` com as propostas de commits.
- Para cada commit proposto, inclua:
  - **Mensagem do Commit**: A mensagem sugerida seguindo o Conventional Commits (ex: `feat(build): implement ghost structures`).
  - **Arquivos/Linhas**: Quais arquivos completos ou trechos específicos (hunks) farão parte deste commit.
  - **Descrição**: Um resumo breve do que este commit resolve ou adiciona.
- Lembre-se de configurar os metadados do artefato com `RequestFeedback=True` e `UserFacing=True`.

### 4. Wait for Approval
- **PARE** a execução. Peça para o usuário revisar o plano e aguarde a autorização explícita antes de fazer qualquer modificação no repositório.

### 5. Execute Commits
- Após a aprovação do usuário, execute os commits propostos.
- Para cada grupo aprovado:
  - Utilize `git reset` se houver arquivos na área de stage que precisem ser separados.
  - Utilize `git add <arquivos>` para adicionar os arquivos completos.
  - Se for necessário commitar apenas partes de um arquivo (partial staging), utilize comandos granulares ou crie patches (`git apply --cached`) caso as mudanças precisem ser separadas.
  - Utilize `git commit -m "<Mensagem do Commit>"` para registrar a funcionalidade.
- Verifique com `git status` e `git diff --cached` se o que está no stage corresponde exatamente ao escopo daquele commit antes de efetivá-lo.

## Review Checklist
- [ ] As alterações foram agrupadas por *propósito funcional* em vez de *arquivo*?
- [ ] Os tipos de commit (feat, fix, etc.) estão corretos?
- [ ] O plano foi apresentado e **explicitamente aprovado** pelo usuário antes de executar `git commit`?
- [ ] Os commits foram isolados corretamente na hora de adicionar ao stage (`git add`)?
