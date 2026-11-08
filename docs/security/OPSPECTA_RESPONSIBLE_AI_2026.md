# OPSPECTA — governança de IA responsável e controles técnicos
**Versão:** 0.2 (08/11/2026)
**Escopo:** software de apoio à investigação de dados operacionais MedTech. **Não** equivale a diagnóstico clínico, dispositivo médico certificado, aconselhamento de manutenção, ou garantia de conformidade.
**Referencial de princípios:** Microsoft Responsible AI (Fairness, Reliability and Safety, Privacy and Security, Inclusiveness, Transparency, Accountability), usado como orientação sem afiliação com a Microsoft. NIST AI RMF (Govern, Map, Measure, Manage), implementação voluntária e progressiva.  
**Situação:** controles de software incorporados à `main` em 03/11/2026 (commit `78813da`); CI de API/frontend e workflow de deploy concluíram com sucesso. Isso não substitui verificação funcional em produção, aprovação dos responsáveis ou os checkpoints abaixo. Um checklist não é certificação.

## 1. Mapeamento verificável dos seis princípios

| Princípio | Controle técnico implementado na proposta | Evidência verificável | Lacuna / condição para expansão |
| --- | --- | --- | --- |
| **Fairness** | Índice exploratório de equipamento usa sinais de manutenção e não atributos demográficos; teste de invariância quando atributos pessoais irrelevantes são incluídos | `apps/api/app/services/predictive.py`; `apps/api/tests/test_enterprise_services.py` | Sem amostra real representativa nem análise de disparidades por hospital, família de equipamento ou acesso a serviços; realizar estudo de viés e qualidade antes de afirmar justiça do produto |
| **Reliability and Safety** | Resposta de hipótese não confirma causa raiz automaticamente; índices heurísticos não informam prazo até falha; entrada de escore validada | `apps/api/app/api/routes/analyze.py`; `apps/api/app/services/predictive.py`; testes de serviços | Validar por especialidade, casos-limite, testes de regressão, false positives/negatives e revisão de profissionais autorizados. Nenhum uso para decisão de segurança clínica sem avaliação |
| **Privacy and Security** | Autenticação e controle de acesso já existiam; uso externo de IA desativado por padrão; uso opcional exige permissão do ambiente e consentimento por chamada no serviço; rejeição de alguns identificadores comuns; logs de decisão não incluem texto da ocorrência | `apps/api/app/api/deps.py`; `apps/api/app/services/rca_advanced.py`; `apps/api/app/core/config.py`; `apps/api/tests/test_responsible_ai.py` | Detector de dados sensíveis é incompleto e **não substitui** consentimento/base legal, minimização ou análise de LGPD. Revisar retenção, fornecedores, segregação por cliente, criptografia, backups e incidentes |
| **Inclusiveness** | Interface identifica avisos em texto, links sem dependência exclusiva de cor; material público mobile; atualizações sem exigir login para material educativo | `apps/web/src/app/analyze/page.tsx`; `apps/web/src/app/ia-responsavel/page.tsx`; `apps/web/src/lib/publicRoutes.ts` | Auditoria WCAG 2.2 AA, leitores de tela, navegação por teclado e validação com usuários reais pendentes. Parte da documentação é apenas PT |
| **Transparency** | Resultados rotulados como hipóteses; valor de similaridade não é probabilidade calibrada; demonstrações fictícias explicitadas; página pública de compromissos e limitações | `apps/api/app/schemas/ticket.py`; `apps/web/src/app/ia-responsavel/page.tsx`; `apps/web/src/app/demonstracao/page.tsx` | Explicações de origem, dados e variações de modelo ainda precisam ser detalhadas por tipo de resultado |
| **Accountability** | Apenas usuário autorizado de nível ≥3 pode confirmar conclusão técnica com referências de evidência, e evento `TicketLog` registra responsável/tempo e tipo de decisão sem dados sensíveis; PATCH genérico não permite contornar revisão | `apps/api/app/api/routes/analyze.py`; `apps/api/app/api/routes/tickets.py`; `apps/api/tests/test_clinical_workflows.py` | Revisor é responsável por validar evidência, mas auditoria independente, governança de aprovação, processo de contestação, retenção e incidentes precisam de definição formal |

**Atenção:** uma pontuação heurística pode produzir diferentes níveis de prioridade para diferentes famílias de ativos devido à distribuição das variáveis. O teste de atributos demográficos irrelevantes não prova ausência de vieses sistêmicos. Não anunciar "modelo justo e certificado".

## 2. Fluxo mínimo de aprovação técnica

1. Usuário autenticado pede análise `POST /analyze`. Resposta é rascunho técnico `technical_hypothesis`, `review_status:pending`, `review_required:true`.
2. O resultado **não** altera `tickets.root_cause`, `tickets.recommendation` ou `tickets.analysis_completed`; grava evento de auditoria mínimo sem texto ou segredo.
3. Responsável técnico qualificado com acesso apropriado revê dados e procedimentos autorizados; confirma apenas quando dispõe de evidências e referências documentadas no sistema de registros da organização.
4. Confirmação explícita: `POST /analyze/{ticket_id}/confirm`, nível ≥3, payload com `confirmed:true`, causa, orientação revisada e referências curtas (sem dados pessoais ou segredos). O registro contém quem confirmou e quando; não prova por si só a validade da análise.
5. Tentativa de injetar resultado confirmado por `PATCH /tickets/{id}` é recusada.
6. Caso haja incerteza, a conclusão deve permanecer pendente, e a decisão operacional fica com a equipe responsável.

### Conteúdo e dados proibidos em entradas externas

- Dados identificáveis de pacientes, prontuários, número de documento, nomes completos, anexos de imagens médicas identificáveis.
- Senhas, API keys, tokens, logs confidenciais, segredos industriais sem autorização e dados técnicos restritos.
- Informação sobre comportamento individual de profissional para fins de avaliação de desempenho automatizada, salvo governança, base legal e avaliação específica.

`rca_advanced.generate_rca` faz verificação limitada de identificadores comuns, mas essa verificação **não identifica todos os dados pessoais**. Por isso, uso externo permanece desligado por padrão; qualquer alteração de `AI_EXTERNAL_PROCESSING_ENABLED` requer revisão contratual e técnica, aprovação do responsável de privacidade e avaliação de segurança. Não habilitar apenas para fazer demo.

## 3. Matriz de risco e responsáveis organizacionais

| Situação | Risco | Mitigação imediata | Condição de avanço |
| --- | --- | --- | --- |
| Sugestão com causalidade falsa | Reparos indevidos / conclusões falsas | Hipótese rotulada, confirmação humana, nenhuma ação física automática | Testes cegos com especialistas, casos negativos e monitoramento de erros |
| Predição de falha com prazo arbitrário | Falsa precisão ou manutenção desnecessária | `predicted_failure_days = null` e aviso heurístico | Modelo calibrado, validação externa e limite de finalidade |
| Dados de serviço enviados a LLM externo | Confidencialidade e LGPD | External off, doble opt-in e bloqueio de padrões sensíveis | DPA, política de retenção, avaliação de riscos e consentimentos/base legal adequados |
| Viés entre clientes/tipos de equipamento | Priorização injusta/ineficaz | Não usar atributos pessoais, revisão contextual | Amostras estratificadas e métricas acordadas |
| Acesso a dados de outro cliente | Quebra de confidencialidade | Auth/RBAC existentes | Provar isolamento multi-tenant da KB e anexos antes de oferecer SaaS multiempresa |
| Uso por pessoa não autorizada | Decisão sem competência técnica | Nível ≥3 para confirmação | Matriz de papéis documentada, treinamentos e revisão de acessos |
| Acessibilidade desigual | Exclusão de usuários | Linguagem clara, semântica HTML, layout responsivo | Teste WCAG e tecnologia assistiva |

**Papel de responsável:** a OPSPECTA deve designar titular técnico, responsável de privacidade e owner do produto na sua governança interna antes de uso com dados de clientes; nenhuma pessoa é nomeada automaticamente nesta proposta.

## 4. Checkpoints de validação antes de produção

- [ ] Testes de API incluindo `test_clinical_workflows.py`, `test_enterprise_services.py`, `test_responsible_ai.py`, sem falhas.
- [ ] Build e testes do Next.js, incluindo rotas públicas vs privadas, sem falhas.
- [ ] Sem APIs públicas de análise, sem `OPENAI_API_KEY` exposta e `AI_EXTERNAL_PROCESSING_ENABLED=false` por padrão.
- [ ] Testes manuais de interface com teclado e leitor de tela, com evidência de execução.
- [ ] Verificação de que nenhum resultado não revisado foi gravado como causa confirmada; testar `PATCH /tickets/{id}` e confirmação sem token.
- [ ] Revisão de tratamento de dados e isolamento entre empresas **antes de dados reais**.
- [ ] Procedimento de rollback, observabilidade e triagem de incidentes.
- [ ] Responsável pela decisão de uso com pacientes/equipamentos médicos assina a revisão do caso de uso. Não afirmar certificação sem processo regulatório aplicável.

## 5. Análises adicionais pendentes

- Inventário de todas as funções que usam modelos externos (inclusive embeddings locais) e respectivas versões, limitações e fontes.
- Revisão de dados da base de conhecimento `kb_articles`, cuja consulta de similaridade atual não inclui filtro por organização; esclarecer se artigos são exclusivamente compartilháveis ou exigir isolamento antes de clientes independentes.
- Revisão de relatórios rotulados “ANVISA compliance” construídos a partir de dados informados pelo usuário: não anunciar como conformidade certificada.
- Política de eliminação, exportação e correção de dados, inclusive logs e cache existentes.
- Validação com gestores de engenharia clínica e serviços MedTech antes de alegar eficiência ou redução de falhas.

## Fontes externas

- Microsoft, Responsible AI Principles and Approach: https://www.microsoft.com/en-us/ai/principles-and-approach
- NIST, AI RMF Playbook: https://airc.nist.gov/airmf-resources/playbook/
- Requisitos regulatórios brasileiros: verificar caso a caso com assessoria jurídica/regulatória e diretrizes da ANPD/Anvisa atualizadas. Não presumir certificação de IA da OPSPECTA.

**Última revisão:** 08/11/2026. Código integrado à `main`; testes locais de API/frontend, lint e build passaram. Verificação funcional em produção, auditoria de acessibilidade, revisão de privacidade/isolamento e aprovação formal para uso com dados reais permanecem pendentes.
