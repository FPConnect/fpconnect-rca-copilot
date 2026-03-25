from __future__ import annotations


CURATED_FINANCE_KNOWLEDGE: list[tuple[str, str]] = [
    (
        "o que sao debentures",
        "Debentures sao titulos de divida emitidos por empresas para captar recursos. Em geral pagam CDI, IPCA ou taxa prefixada, mas carregam risco de credito do emissor e nem sempre contam com cobertura do FGC. O ponto central e avaliar emissor, prazo, garantia, subordinacao e liquidez antes de investir.",
    ),
    (
        "o que e duration",
        "Duration e uma medida de sensibilidade do preco de um titulo de renda fixa a mudancas na taxa de juros. Quanto maior a duration, maior tende a ser o impacto de oscilacoes de juros sobre o preco do papel. Ela ajuda a entender risco de marcacao a mercado, especialmente em titulos mais longos.",
    ),
    (
        "o que e curva de juros",
        "Curva de juros e a estrutura das taxas para diferentes prazos da economia. Ela mostra como o mercado precifica dinheiro no tempo e costuma afetar renda fixa, bolsa, cambio e credito. Mudancas na inclinacao da curva podem sinalizar expectativa de inflacao, atividade e politica monetaria.",
    ),
    (
        "o que sao opcoes",
        "Opcoes sao contratos que dao o direito, mas nao a obrigacao, de comprar ou vender um ativo por um preco predeterminado ate uma data. Elas servem para hedge, renda ou alavancagem, mas embutem risco elevado se usadas sem estrutura e sem entender delta, vencimento, volatilidade e perda maxima possivel.",
    ),
    (
        "o que sao contratos futuros",
        "Contratos futuros sao derivativos padronizados negociados em bolsa para travar ou especular sobre preco futuro de um ativo, indice, moeda ou taxa. Como operam com ajuste diario e margem, podem ampliar ganho e perda muito rapido. Sao instrumentos mais adequados para hedge profissional ou operacao com gestao de risco bem disciplinada.",
    ),
    (
        "como analisar balanco de empresa",
        "Para analisar balanco, comece por receita, margem, lucro, geracao de caixa, divida liquida, retorno sobre capital e consistencia historica. Depois olhe notas explicativas, qualidade do lucro, ciclo do negocio e se o crescimento veio com eficiencia ou so com mais alavancagem. O numero isolado raramente basta; o valor vem da combinacao entre qualidade operacional e preco pago.",
    ),
    (
        "o que e fluxo de caixa descontado",
        "Fluxo de caixa descontado e um metodo de valuation que estima o valor presente do caixa futuro de um negocio usando uma taxa de desconto. Ele depende muito das premissas de crescimento, margem, investimento e custo de capital, por isso pequenas mudancas nessas hipoteses alteram bastante o resultado final.",
    ),
    (
        "o que e roe e roic",
        "ROE mede retorno sobre patrimonio liquido; ROIC mede retorno sobre o capital investido no negocio. Os dois ajudam a avaliar eficiencia, mas fazem mais sentido quando comparados com historico da empresa, pares do setor e custo de capital. Retorno alto sustentavel costuma ser sinal melhor que crescimento sem qualidade.",
    ),
    (
        "como funciona marcação a mercado",
        "Marcacao a mercado e a atualizacao do preco de um ativo pela taxa ou preco vigente do momento, mesmo antes do vencimento. Em renda fixa, isso explica por que titulos podem cair de valor no curto prazo quando juros sobem, mesmo pagando exatamente o combinado no vencimento se voce carregar ate la.",
    ),
    (
        "como funciona imposto em fii",
        "FIIs exigem atencao dupla: rendimentos e ganho de capital podem seguir regras diferentes. Como tributacao muda e depende do tipo de renda, da operacao e da legislacao vigente, o caminho seguro e validar a regra atual antes de declarar. O agente pode explicar a estrutura geral, mas a apuracao final precisa ser conferida no periodo correto.",
    ),
]


FINANCE_STUDY_TRACKS: dict[str, tuple[str, list[str]]] = {
    "iniciante": (
        "Trilha iniciante de mercado financeiro",
        [
            "1. Entenda reserva de emergencia, liquidez e risco antes de pensar em bolsa.",
            "2. Separe renda fixa de renda variavel e saiba onde cada uma faz sentido.",
            "3. Aprenda o basico de Tesouro Selic, CDB, ETF, acao e FII.",
            "4. Monte uma carteira simples, diversificada e pequena no inicio.",
            "5. Estude custos, imposto e disciplina de aportes antes de tentar acelerar retorno.",
            "6. Quando quiser partir para pratica, use mercado: analisar <ticker> e mercado: plano <ticker> para simular cenarios sem operar ao vivo.",
        ],
    ),
    "fundamentalista": (
        "Trilha de analise fundamentalista",
        [
            "1. Comece por demonstracoes financeiras: receita, margem, lucro e fluxo de caixa.",
            "2. Depois avalie divida, retorno sobre capital, governanca e vantagem competitiva.",
            "3. Estude multiplos como P/L, EV/EBITDA, P/VP, ROE e ROIC no contexto do setor.",
            "4. Aprenda valuation por comparaveis e fluxo de caixa descontado sem tratar estimativa como certeza.",
            "5. Feche a analise comparando qualidade do negocio com o preco de mercado e sua margem de seguranca.",
            "6. Para praticar no agente, combine perguntas conceituais com mercado: analisar <ticker> para confrontar fundamento e momento tecnico.",
        ],
    ),
    "trader": (
        "Trilha de operacao e gestao de risco",
        [
            "1. Diferencie day trade, swing trade e position pelo prazo e pela exigencia operacional.",
            "2. Estude tendencia, suporte, resistencia, medias moveis, RSI, ATR e volume.",
            "3. Defina risco por operacao antes de pensar em alvo de ganho.",
            "4. Entenda stop loss, tamanho de posicao, slippage e o efeito da liquidez.",
            "5. Registre setups, erro de execucao e disciplina emocional; sem isso nao existe processo repetivel.",
            "6. Use primeiro o paper trading do agente com mercado: plano, mercado: comprar e mercado: atualizar para testar consistencia sem execucao real.",
        ],
    ),
    "macroeconomia": (
        "Trilha de macroeconomia e juros",
        [
            "1. Comece por Selic, CDI e IPCA para entender juros nominais, juros reais e inflacao.",
            "2. Estude curva de juros, expectativa de crescimento, cambio e risco fiscal como vetores que deslocam precos de ativos.",
            "3. Entenda como alta de juros afeta renda fixa, bolsa, credito, consumo e valuation.",
            "4. Aprenda marcacao a mercado, duration e o impacto do prazo em titulos de renda fixa.",
            "5. Observe como politica monetaria no Brasil e nos EUA costuma contaminar fluxo global e ativos locais.",
            "6. Use o agente para consolidar conceitos perguntando por Selic, CDI, IPCA, duration, curva de juros e marcacao a mercado antes de partir para analises de ativos.",
        ],
    ),
}


def finance_knowledge_entries() -> list[dict[str, str]]:
    return [{"question": question, "answer": answer} for question, answer in CURATED_FINANCE_KNOWLEDGE]


def finance_study_track_entries() -> list[dict[str, object]]:
    return [
        {"id": track_id, "title": title, "steps": steps}
        for track_id, (title, steps) in FINANCE_STUDY_TRACKS.items()
    ]
