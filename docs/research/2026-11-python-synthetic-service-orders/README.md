# Análise de registros de manutenção com Python — demonstração 100% sintética
**OPSPECTA | Nota técnica reproduzível | 09/11/2026**

> Este é um experimento de simulação. Não contém dados de clientes, hospitais, pacientes, equipamentos ou fabricantes reais. Não é publicação revisada por pares nem validação comercial/clinica da OPSPECTA.

## Objetivo e método
Demonstrar um procedimento transparente para (a) identificar campos incompletos, (b) medir o intervalo registrado entre abertura e fechamento de ordens de serviço e (c) sinalizar *candidatos* a reincidência para revisão humana. O script anexo `analise_logs_sinteticos.py` usa Python 3.10+ e apenas a biblioteca padrão. Gera 100 ordens de serviço fictícias de 20 ativos artificiais com semente determinística `20261109`. Nenhum contato com equipamentos ou modelos externos.

A regra ilustrativa de reincidência considera **pares consecutivos por ativo** cuja categoria de ocorrência é igual e cujo intervalo entre as respectivas aberturas é de até 30 dias. Isso **não confirma uma mesma causa-raiz**, nem que uma peça foi trocada indevidamente.

## Resultados da simulação
| Métrica | Valor exclusivamente sintético |
|---|---:|
| Ordens de serviço | 100 |
| Campo `action` propositalmente vazio | 8 (8,0%) |
| Duração média abertura–fechamento | 27,7 horas |
| Pares candidatos a reincidência | 16 |
| Categorias | communication 18, configuration 21, power 15, sensor 21, software 25 |

Os números foram obtidos pela execução do script e **não são indicadores de campo, clientes ou hospitais**. O intervalo abertura–fechamento não corresponde necessariamente ao tempo de reparo (MTTR): inclui períodos que não são separados na base sintética.

## Reproduzir
Salve o arquivo `analise_logs_sinteticos.py` ao lado desta nota e execute:

```bash
python analise_logs_sinteticos.py
```

O programa cria `os_sinteticas.csv` e imprime métricas. Colunas: `order_id`, `asset_id`, `opened_at`, `closed_at`, `category`, `action`. Os dados são gerados, não extraídos.

## Limites e próxima validação
Dados reais demandariam autorização, governança de acesso, minimização de informações, segregação entre organizações, alinhamento sobre conceitos de SLA e análise de confidencialidade/transferências internacionais. Registros duplicados, mudanças de identificação do ativo e descrições genéricas podem produzir falsos candidatos a reincidência. Conclusões técnicas requerem revisão por profissional qualificado; nenhuma recomendação de intervenção física ou clínica é gerada.

Próximo experimento: comparar a regra com revisão cega de técnicos responsáveis e medir precisão, falsos positivos e falsos negativos, sempre em conjunto licitamente disponibilizado e autorizado. O resultado atual **não permite alegar economia, menos falhas ou superioridade frente a plataformas de fabricantes**.

## Referências de contexto
- WHO. *Medical equipment maintenance programme overview* (2011). https://iris.who.int/handle/10665/44587
- WHO. *Introduction to medical equipment inventory management* (2011). https://iris.who.int/handle/10665/44588
- NIST. *AI Risk Management Framework (AI RMF 1.0)* (2023). https://doi.org/10.6028/NIST.AI.100-1

**Natureza editorial:** nota técnica aberta em repositório de código, não artigo de periódico ou publicação revisada por pares.
