"use client";

import Link from "next/link";
import { ExternalLink, Shield, Wifi, BarChart2, Server, Cpu, FileText, BookOpen, HelpCircle } from "lucide-react";

/* -------------------------------------------------------------------
 * DHS — Nihon Kohden Digital Health Solutions (NKDHS)
 * https://www.digitalhealthsolutions.com
 *
 * Products:
 *   HealthConnect  — EMR/HL7 integration (Enterprise Gateway, NKAnywhere, Ventilator Gateway)
 *   VirtualCare    — Remote ICU monitoring (NetKonnect, NGNK, Prefense, ViTrac)
 *   DataInsight    — Clinical analytics & data acquisition (CoMET)
 * ------------------------------------------------------------------ */

const PRODUCTS = [
  {
    category: "HealthConnect",
    description:
      "Seamlessly integrate hospital systems with the EMR and Nihon Kohden devices. Empower clinicians with remote oversight and control through seven key gateway extensions.",
    icon: Server,
    color: "blue",
    url: "https://www.digitalhealthsolutions.com/product-main-pages/healthconnect",
    items: [
      {
        name: "Enterprise Gateway (HL7 Gateway)",
        description: "Securely connects the patient monitoring network to the hospital network and EMR via HL7 messaging.",
        url: "https://www.digitalhealthsolutions.com/site-products-1/enterprise-gateway",
        tags: ["HL7", "EMR", "Integration"],
      },
      {
        name: "NKAnywhere",
        description: "Remotely update firmware files and settings for Nihon Kohden devices without physical access.",
        url: "https://www.digitalhealthsolutions.com/site-products/nkanywhere",
        tags: ["Firmware", "Remote Management"],
      },
      {
        name: "Ventilator Gateway",
        description: "Secures ventilator patient data from Nihon Kohden ventilators directly into the EMR.",
        url: "https://www.digitalhealthsolutions.com/site-products/ventilator-gateway",
        tags: ["Ventilator", "EMR", "ICU"],
      },
    ],
  },
  {
    category: "VirtualCare",
    description:
      "Access patient bedside monitors from multiple locations for remote live management. Monitor vital signs, waveforms, and patient information with centralized and mobile solutions.",
    icon: Wifi,
    color: "green",
    url: "https://www.digitalhealthsolutions.com/product-main-pages/virtualcare",
    items: [
      {
        name: "NetKonnect / NGNK Remote ICU",
        description: "Next-generation remote ICU platform enabling multi-site centralized patient monitoring for clinicians.",
        url: "https://www.digitalhealthsolutions.com/site-products-2/netkonnect",
        tags: ["Remote ICU", "Monitoring", "Centralized"],
      },
      {
        name: "Prefense — Centralized Telemetry",
        description: "Provides clinicians with remote access to telemetry device data from a central station.",
        url: "https://www.digitalhealthsolutions.com/site-products/prefense",
        tags: ["Telemetry", "ECG", "Cardiac Monitoring"],
      },
      {
        name: "ViTrac",
        description: "View near real-time patient data remotely through mobile devices, enabling care from anywhere.",
        url: "https://www.digitalhealthsolutions.com/site-products/vitrac",
        tags: ["Mobile", "Real-time", "Vital Signs"],
      },
    ],
  },
  {
    category: "DataInsight",
    description:
      "Engineer multi-source data acquisition for cutting-edge data-driven applications. Leverage AI/ML to help clinicians create live data applications and enable real-time data transmission.",
    icon: BarChart2,
    color: "purple",
    url: "https://www.digitalhealthsolutions.com/product-main-pages/datainsight",
    items: [
      {
        name: "CoMET®",
        description:
          "Advanced clinical data platform for data acquisition and analytics from multiple Nihon Kohden sources. ANVISA certified for the Brazilian market.",
        url: "https://www.digitalhealthsolutions.com/news",
        tags: ["Analytics", "AI/ML", "ANVISA", "Brazil"],
      },
      {
        name: "Live Data Applications",
        description: "Real-time user applications built on the DataInsight platform for clinicians to foresee and prevent problems.",
        url: "https://www.digitalhealthsolutions.com/product-main-pages/datainsight",
        tags: ["Real-time", "Predictive", "AI"],
      },
    ],
  },
];

const PLAYBOOKS = [
  {
    title: "Alerta crítico de ventilador em UTI",
    context: "UTI adulto / neonatal",
    description:
      "Exemplo de fluxo DHS completo, combinando monitorização de leito, alerta remoto, abertura de ticket e escalonamento automático.",
    steps: [
      "Alarmes de ventilador e monitor de beira-leito sobem para o FPConnect via integração de rede.",
      "A inteligência de Radar prioriza eventos críticos (apneia, desconexão, falha de energia).",
      "Um ticket crítico é aberto automaticamente com SLA definido e nível de escalonamento inicial.",
      "O fluxo de SLA (n8n) notifica plantonista, coordenação e engenharia clínica conforme o tempo de resposta.",
    ],
    links: [
      { label: "Abrir lista de tickets", href: "/tickets" },
      { label: "Ver Radar Intel", href: "/radar" },
    ],
  },
  {
    title: "Integração EMR/HL7 com monitorização contínua",
    context: "Unidade de internação / centro cirúrgico",
    description:
      "Cenário em que o FPConnect usa a camada de integração para manter dados de sinais vitais e eventos alinhados ao prontuário eletrônico.",
    steps: [
      "Os monitores enviam dados para a rede e para o FPConnect em tempo quase real.",
      "Eventos relevantes (quedas de pressão, bradicardias) são correlacionados com o contexto clínico do paciente.",
      "Logs e tickets são associados ao paciente e ao leito, facilitando revisão posterior (RCA).",
    ],
    links: [
      { label: "Ver máquinas e leitos", href: "/machines" },
      { label: "Histórico e RCA", href: "/history" },
    ],
  },
  {
    title: "Uso avançado de dados para melhoria contínua",
    context: "Gestão de risco e qualidade",
    description:
      "Como dados agregados de alarmes, tickets e incidentes alimentam dashboards e análises para reduzir eventos evitáveis.",
    steps: [
      "Alarmes e tickets são categorizados (dispositivo, unidade, motivo clínico, causa raiz provável).",
      "Dashboards destacam padrões de risco (por exemplo, alarmes recorrentes em um mesmo equipamento).",
      "Planos de ação são acompanhados via tickets, com campos de causa raiz e contramedidas.",
    ],
    links: [
      { label: "Painel principal", href: "/" },
      { label: "Métricas e dashboards", href: "/metrics" },
    ],
  },
];

const LEARNING_RESOURCES = [
  {
    title: "NKDHS Official Website",
    description: "Ponto de partida para visão geral dos produtos e notícias da Nihon Kohden Digital Health Solutions.",
    url: "https://www.digitalhealthsolutions.com",
    icon: BookOpen,
  },
  {
    title: "NKDHS Company News",
    description: "Comunicações oficiais sobre lançamentos, certificações e atualizações de portfólio.",
    url: "https://www.digitalhealthsolutions.com/news",
    icon: FileText,
  },
  {
    title: "FDA Digital Health Guidance",
    description: "Visão geral de diretrizes da FDA para software médico, interoperabilidade e cibersegurança.",
    url: "https://www.fda.gov/medical-devices/digital-health-center-excellence",
    icon: Shield,
  },
  {
    title: "PubMed — Digital Health & ICU",
    description: "Coleção dinâmica de artigos científicos sobre monitorização remota, EMR integration e UTI digital.",
    url: "https://pubmed.ncbi.nlm.nih.gov/?term=digital+health+ICU+monitoring&sort=date",
    icon: BookOpen,
  },
];

const COLOR_MAP: Record<string, { bg: string; border: string; text: string; badge: string }> = {
  blue: {
    bg: "bg-blue-50",
    border: "border-blue-200",
    text: "text-blue-700",
    badge: "bg-blue-100 text-blue-700",
  },
  green: {
    bg: "bg-green-50",
    border: "border-green-200",
    text: "text-green-700",
    badge: "bg-green-100 text-green-700",
  },
  purple: {
    bg: "bg-purple-50",
    border: "border-purple-200",
    text: "text-purple-700",
    badge: "bg-purple-100 text-purple-700",
  },
};

export default function DHSResourcesPage() {
  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-blue-100 rounded-xl">
            <Cpu size={28} className="text-blue-600" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              DHS — Digital Health Solutions
            </h1>
            <p className="text-gray-500 mt-1 text-sm">
              Nihon Kohden Digital Health Solutions (NKDHS) — recursos, produtos e exemplos práticos de como o FPConnect
              pode usar esse ecossistema em fluxos diários de operação, escalonamento de SLA e inteligência clínica.
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              <a
                href="https://www.digitalhealthsolutions.com"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 text-white text-xs font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                <ExternalLink size={12} />
                Site Oficial NKDHS
              </a>
              <a
                href="mailto:info@nklab.com"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 text-gray-700 text-xs font-medium rounded-lg hover:bg-gray-200 transition-colors"
              >
                <HelpCircle size={12} />
                info@nklab.com
              </a>
            </div>
          </div>
        </div>

        {/* About */}
        <div className="mt-5 p-4 bg-gray-50 rounded-lg border border-gray-100 text-sm text-gray-600 leading-relaxed space-y-2">
          <p>
            <strong className="text-gray-800">Sobre a NKDHS:</strong> a Nihon Kohden Digital Health Solutions apoia
            hospitais e equipes clínicas com um conjunto integrado de soluções para conectividade, monitorização remota
            e uso inteligente de dados. Os pilares típicos são <strong>HealthConnect</strong> (integração EMR/HL7),{" "}
            <strong>VirtualCare</strong> (monitorização e acesso remoto) e <strong>DataInsight</strong> (análise clínica de
            informação).
          </p>
          <p>
            Nesta tela o foco é mostrar <strong>como o FPConnect pode se apoiar nesse ecossistema</strong> para criar fluxos
            padronizados: alarmes que geram tickets, inteligência de risco no Radar, playbooks operacionais e métricas que
            ajudam na melhoria contínua de segurança e qualidade.
          </p>
        </div>
      </div>

      {/* Products */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Produtos NKDHS</h2>
        <div className="space-y-6">
          {PRODUCTS.map((product) => {
            const colors = COLOR_MAP[product.color];
            const Icon = product.icon;
            return (
              <div key={product.category} className={`rounded-xl border ${colors.border} ${colors.bg} p-5`}>
                <div className="flex items-center justify-between gap-3 mb-2">
                  <div className="flex items-center gap-2">
                    <Icon size={18} className={colors.text} />
                    <h3 className={`font-bold text-base ${colors.text}`}>{product.category}</h3>
                  </div>
                  <a
                    href={product.url}
                    target="_blank"
                    rel="noreferrer"
                    className={`text-xs font-medium ${colors.text} hover:underline flex items-center gap-1`}
                  >
                    <ExternalLink size={11} />
                    Ver produto
                  </a>
                </div>
                <p className="text-sm text-gray-600 mb-4">{product.description}</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {product.items.map((item) => (
                    <div key={item.name} className="bg-white rounded-lg border border-gray-200 p-4">
                      <div className="flex items-start justify-between gap-2">
                        <p className="text-sm font-semibold text-gray-800">{item.name}</p>
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-blue-500 hover:text-blue-700 flex-shrink-0"
                        >
                          <ExternalLink size={13} />
                        </a>
                      </div>
                      <p className="text-xs text-gray-500 mt-1 leading-relaxed">{item.description}</p>
                      <div className="mt-2 flex flex-wrap gap-1">
                        {item.tags.map((tag) => (
                          <span key={tag} className={`text-xs px-2 py-0.5 rounded-full font-medium ${colors.badge}`}>
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Playbooks práticos dentro do FPConnect */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-2">Playbooks DHS no FPConnect</h2>
        <p className="text-xs text-gray-500 mb-4 max-w-3xl">
          Exemplos de fluxos que combinam monitorização, tickets, escalonamento de SLA e análise de dados. Servem como
          guia rápido para demonstrar o valor conjunto de FPConnect + NKDHS em diferentes contextos clínicos.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {PLAYBOOKS.map((pb) => (
            <div key={pb.title} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex flex-col gap-2">
              <div>
                <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-1">{pb.context}</p>
                <h3 className="text-sm font-semibold text-gray-900">{pb.title}</h3>
              </div>
              <p className="text-xs text-gray-500 leading-relaxed">{pb.description}</p>
              <ul className="mt-1 space-y-1">
                {pb.steps.map((step) => (
                  <li key={step} className="text-xs text-gray-600 flex gap-1">
                    <span className="mt-[3px] h-1.5 w-1.5 rounded-full bg-blue-400 flex-shrink-0" />
                    <span>{step}</span>
                  </li>
                ))}
              </ul>
              <div className="mt-2 flex flex-wrap gap-2">
                {pb.links.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full border border-blue-200 text-[11px] font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 hover:border-blue-300 transition-colors"
                  >
                    <Cpu size={11} className="text-blue-500" />
                    {link.label}
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Learning Resources */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-1">Recursos de aprendizado &amp; referências externas</h2>
        <p className="text-xs text-gray-500 mb-4 max-w-3xl">
          Use estes links como complemento. As principais fontes operacionais (notícias, pesquisas e incidentes) já
          aparecem integradas no Radar Intel, dashboards e histórico de tickets dentro do próprio FPConnect.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {LEARNING_RESOURCES.map((res) => {
            const Icon = res.icon;
            return (
              <a
                key={res.title}
                href={res.url}
                target={res.url.startsWith("mailto") ? undefined : "_blank"}
                rel={res.url.startsWith("mailto") ? undefined : "noreferrer"}
                className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 hover:shadow-md hover:border-blue-200 transition-all group flex gap-3"
              >
                <div className="p-2 bg-blue-50 rounded-lg flex-shrink-0 h-fit group-hover:bg-blue-100 transition-colors">
                  <Icon size={16} className="text-blue-600" />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-gray-800 group-hover:text-blue-700 transition-colors">
                    {res.title}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">{res.description}</p>
                </div>
              </a>
            );
          })}
        </div>
      </div>

      {/* Intel / Radar note */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-5 flex gap-3">
        <div className="flex-shrink-0">
          <Cpu size={20} className="text-blue-500 mt-0.5" />
        </div>
        <div>
          <p className="text-sm font-semibold text-blue-800">Radar Intel integrado</p>
          <p className="text-sm text-blue-700 mt-1">
            Os feeds de notícias e pesquisas da NKDHS (MedCity News, Fierce Healthcare, PubMed — Remote
            Monitoring, EMR Integration e ICU Digital Health) estão configurados no <strong>Radar (Intel)</strong>.
            Acesse a aba <strong>Radar</strong> para visualizar as últimas notícias e publicações científicas relacionadas
            a DHS e Digital Health Solutions em tempo real.
          </p>
        </div>
      </div>
    </div>
  );
}
