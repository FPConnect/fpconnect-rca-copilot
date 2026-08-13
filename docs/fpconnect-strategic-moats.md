# FPConnect - Plano de abismos de diferenciacao

Data: 2026-08-13

## Principio de implementacao

Nada do que ja existe deve ser refeito para validar os diferenciais. A
estrategia tecnica e adicionar modulos independentes, com dados e simulacoes
isoladas, ate que exista prova comercial suficiente para integrar ao fluxo
principal.

## O que o mercado ja entrega

Sistemas de CMMS/HTM e facilities hospitalares competem em:

- ordens de servico e manutencao preventiva;
- inventario de ativos;
- compliance e auditoria;
- multi-site;
- mobile/offline;
- integracoes com BMS, IoT, ERP e EHR;
- manutencao preditiva.

Isso e necessario, mas nao cria distancia suficiente. A FPConnect precisa
vender um nivel acima: decisao clinica, risco executivo e receita protegida.

## Fontes pesquisadas

- FDA - Cybersecurity in Medical Devices:
  https://www.fda.gov/medical-devices/digital-health-center-excellence/cybersecurity
- FDA - Medical Device Recalls and Early Alerts:
  https://www.fda.gov/medical-devices/medical-device-safety/medical-device-recalls-and-early-alerts
- FDA - GUDID:
  https://www.fda.gov/medical-devices/unique-device-identification-system-udi-system/global-unique-device-identification-database-gudid
- AccessGUDID:
  https://accessgudid.nlm.nih.gov/
- ECRI - Top 10 Health Technology Hazards for 2026:
  https://www.draeger.com/Content/Documents/Content/ECRI-Top-10-Health-Technology-Hazards-for-2026-Executive-Brief.pdf
- NIST - AI Risk Management Framework:
  https://www.nist.gov/itl/ai-risk-management-framework
- GE HealthCare Research - Digital Twin:
  https://research.gehealthcare.com/across-the-enterprise/how-a-purpose-built-digital-twin-is-changing-hospital-operations-jb35456xx/
- CISA - Known Exploited Vulnerabilities:
  https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- CISA - 2026 Minimum Elements for SBOM:
  https://www.cisa.gov/resources-tools/resources/2026-minimum-elements-software-bill-materials-sbom
- Health-ISAC - cyberattacks in healthcare:
  https://health-isac.org/cyberattacks-on-healthcare-sector-jumped-14-in-first-half-of-2026/
- Facilio - healthcare CMMS comparison:
  https://facilio.com/blog/healthcare-maintenance-management-software/
- EQ2 HEMS CMMS:
  https://www.eq2llc.com/eq2-hems-cmms

## Abismo 1 - Clinical Capacity Twin

### Tese

O FPConnect deixa de mostrar "equipamento indisponivel" e passa a mostrar
"capacidade assistencial em risco": leitos, exames, cirurgias, receita e fila
impactados por ativo critico.

### Por que isso diferencia

CMMS tradicional para na manutencao. O comprador executivo compra capacidade,
continuidade e previsibilidade. Um digital twin operacional permite responder:

- qual unidade quebra primeiro se este equipamento parar?
- qual contingencia protege mais receita e paciente?
- onde vale contratar redundancia, backup ou troca?
- qual investimento tem payback mais rapido?

### MVP de 90 dias

1. Comecar com UTI, centro cirurgico e diagnostico por imagem.
2. Mapear ativos criticos, uso, localizacao, criticidade e tickets.
3. Criar simulador simples de downtime e capacidade.
4. Gerar relatorio executivo por unidade.
5. Validar com 3 hospitais: "isso muda decisao de investimento?"

## Abismo 2 - Device Trust Graph

### Tese

Cada ativo vira um grafo de confianca: UDI/GUDID, recall, early alert, SBOM,
CVE/KEV, firmware, contrato, fornecedor e evidencia interna.

### Por que isso diferencia

Hospitais sofrem com fontes dispersas. Engenharia, TI, qualidade e compras
olham para o mesmo equipamento com perguntas diferentes. O Trust Graph cria
uma resposta unica:

- qual ativo esta vulneravel?
- qual e o impacto clinico?
- existe recall ou alerta?
- o fornecedor deve agir?
- qual evidencia eu anexo na auditoria?

### MVP de 90 dias

1. Selecionar ventiladores, bombas de infusao e equipamentos de imagem.
2. Importar inventario local e normalizar fabricante/modelo/UDI.
3. Cruzar demo com FDA recalls, AccessGUDID, CISA KEV e SBOM simulado.
4. Gerar pacote de evidencia e carta para OEM.
5. Medir percentual de ativos criticos com acao defensavel.

## Abismo 3 - Executive Revenue Command

### Tese

O produto precisa provar valor em linguagem de diretoria e alimentar venda:
ROI, risco protegido, proposta sugerida, expansao contratual e mensagem por
stakeholder.

### Por que isso diferencia

A maioria das ferramentas tecnicas morre em piloto porque nao vira business
case. O Revenue Command transforma operacao em argumento:

- para CFO: perda evitada e payback;
- para COO: continuidade e capacidade;
- para engenharia: prioridade e evidencias;
- para TI/CISO: risco cyber por ativo;
- para vendas FPConnect: proxima acao e pacote recomendado.

### MVP de 90 dias

1. Criar business case automatico por hospital-alvo.
2. Gerar narrativa de valor por cargo.
3. Conectar sinais de uso a gatilhos de upgrade.
4. Criar templates de proposta Premium, VIP e Consultoria.
5. Medir respostas, reunioes executivas e expansao.

## Regras de seguranca do produto

- Nao substituir criterio clinico ou regulatorio por IA.
- Manter fonte e evidencia em toda recomendacao.
- Separar recomendacao tecnica de decisao assistencial.
- Permitir aprovacao humana antes de contato com fornecedor ou cliente.
- Registrar trilha de auditoria para cada decisao.

## Implementacao inicial adicionada

- Nova pagina: `/strategic-moats`
- Novo endpoint: `/api/strategic-moats`
- Novo modulo de dados/simulacao: `apps/web/src/lib/strategic-moats.ts`

Nenhuma pagina existente foi alterada.
