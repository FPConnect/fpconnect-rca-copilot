# OPSPECTA — separação e governança da base de conhecimento técnico

**Data:** 04/11/2026  
**Escopo:** módulo `/knowledge`, artigos `kb_articles`, workspaces, permissões e recuperação assistiva. **Não** constitui segregação multitenant de toda a aplicação (tickets, máquinas, contratos e anexos requerem avaliação própria).

## 1. Objetivo

Separar informações técnicas por titular e organização autorizada, sem presumir que registros privados podem ser aproveitados por outros clientes. O resultado de busca é referência para revisão humana, não diagnóstico confirmado nem instrução autônoma de manutenção.

## 2. Arquitetura e modos de acesso

**Private:** artigo visível somente ao proprietário ativo autenticado. O título, corpo, tags e metadados não aparecem na listagem de terceiros. Administradores só recebem artigos enviados especificamente à fila de revisão, por autorização voluntária do autor.

**Workspace:** organização lógica com `knowledge_workspaces` e associação explícita em `knowledge_memberships`. A administração designa pessoas; não há associação automática por domínio de e-mail. Autores membros veem seus rascunhos enquanto membros; outros membros somente recebem artigos aprovados. A remoção de membro revoga sua leitura de todos os registros workspace, mesmo dos que ele criou.

**Global:** artigos aprovados por revisor humano independente podem ser pesquisados por usuários autenticados de outras organizações. Autor enxerga rascunhos próprios antes de revisão; os demais não.

**Legacy:** artigos anteriores à migração recebem `review_status=legacy_quarantine`, `visibility=private` e proprietário nulo. Não são pesquisáveis ou compartilháveis. A triagem exige administrador nível >=4, designação explícita de proprietário e, quando necessário, workspace; esta ação **não aprova nem publica**.

### Responsabilidades

- Usuário nível >=2: criar artigo, pesquisar permissões vigentes, revisar conteúdo próprio, submeter para análise.
- Administrador nível >=4: criar espaços, conceder/revogar membros, inspecionar fila de revisão, classificar legado.
- Revisão global/privada: independente do autor e por administrador nível >=4.
- Revisão de workspace: independente do autor, por administrador nível >=4 **que também seja gerente daquele workspace**.
- Aprovação exige declaração humana `sharing_authorized=true`. Este ato não dispensa checagem real de consentimento, confidencialidade, adequação técnica e direitos de uso.

## 3. Organização e filtros disponíveis

**Categorias:** operações, equipamentos, conectividade, software, qualidade, documentação, outros.

**Metadados:** família do equipamento, fabricante, modelo, código de falha, referência interna autorizada, etiquetas (até 12), autor, workspace, visibilidade, estado de revisão, versão, data, revisor.

**Busca:** texto/título e etiquetas, categoria, organização, status, visibilidade, fabricante, família, código de falha e etiqueta exata. Paginação limitada a 50 artigos por requisição. **O filtro de acesso é aplicado antes dos filtros de conteúdo e ordenação.**

Ciclo de vida: `draft -> in_review -> approved` ou `rejected -> in_review`; alterações em artigo aprovado cancelam a aprovação anterior e exigem nova revisão. Arquivamento impede que um artigo seja utilizado como referência automática.

## 4. Recuperação para análise de chamados

`POST /analyze` e `POST /tickets/{id}/analyze` passam a identidade do usuário autenticado para a busca de artigos. O serviço realiza recuperação lexical somente de artigos **aprovados** e visíveis (private do próprio, workspace de membros atuais, ou global). Sem associação ou migração, a busca falha fechada e não retorna informação do cliente.

A busca de embeddings/vetor não foi reativada: os vetores legados não tinham proveniência de compartilhamento verificável. Foi preservada a coluna de vetor, mas novos documentos não geram embeddings automaticamente. O valor `confidence` de correspondências lexicais é 0.0 e não deve ser exibido como probabilidade de causa.

**Separação de conteúdo do procedimento:** a análise de chamado retorna referência ao artigo, não instruções físicas copiadas da base. Qualquer ação técnica permanece sob procedimentos e profissionais habilitados.

## 5. Migração e recuperação

`008_knowledge_governance.py` adiciona tabelas, colunas e índices sem excluir texto, tags ou vetores anteriores. O deploy deve aplicar `alembic upgrade head` **antes de servir a nova API**, com backup recuperável e teste de restauração em processo operacional próprio. O downgrade é intencionalmente bloqueado porque poderia descartar campos de autorização.

Inventário de legado: `GET /knowledge/legacy` retorna apenas identificador, título e data a administradores; o conteúdo é inacessível até classificação. A conversão para artigo normal depende de `POST /knowledge/legacy/{id}/classify` e revisão subsequente.

Atenção: títulos históricos também podem conter informações sensíveis. Apenas equipes autorizadas devem acessar este inventário.

## 6. Testes e métricas de controle

O arquivo `apps/api/tests/test_knowledge_workspaces.py` contém cenários sintéticos de:
- vazamento entre usuários e workspaces;
- associação explícita e remoção imediata de membro;
- impossibilidade de autopublicação;
- consulta de artigos antes/depois da aprovação;
- filtragem por categoria, código de falha e etiqueta exata;
- preservação do legado em quarentena;
- metadados de auditoria e invalidação da revisão após edição;
- busca com identidade do requerente.

**Monitorar em operação:** tentativas negadas, número de artigos em quarentena, fila pendente, compartilhamento global aprovado, falsos positivos de busca e eventuais incidentes. Não registrar corpos de artigos ou conteúdo de chamados em logs de aplicação.

## 7. Limites e pendências conscientes

- Ainda não há validação independente da segregação de todo o sistema SaaS; o isolamento se restringe ao acervo KB.
- Uma fila de revisão humana é necessária para classificar o legado. Não há base comprovada para classificar tudo automaticamente.
- A UI não envia ou importa dados sensíveis por padrão. Não misturar dados de clientes para treinar modelos sem autorização específica.
- Sem busca semântica até que haja processo de indexação com controle de workspace, finalidade aprovada e políticas de retenção.
- O workflow precisa aplicar a migração sem pular testes, validar produção e manter capacidade de restauração.
