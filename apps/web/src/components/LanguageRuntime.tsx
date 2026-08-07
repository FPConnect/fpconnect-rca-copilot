"use client";

import { useEffect } from "react";

const SYSTEM_STORAGE_KEY = "fpconnect_system_preferences";
const LANGUAGE_CHANGE_EVENT = "fpconnect:language-change";

type Language = "pt-BR" | "en-US";

const PT_TO_EN: Record<string, string> = {
  "FPConnect": "FPConnect",
  "Technologies": "Technologies",
  "Home": "Home",
  "Máquinas": "Machines",
  "Health Checks": "Health Checks",
  "Alertas": "Alerts",
  "Tickets": "Tickets",
  "Métricas": "Metrics",
  "Manutenção": "Maintenance",
  "Controle de Acesso": "Access Control",
  "Histórico": "History",
  "Notificações": "Notifications",
  "Configurações": "Settings",
  "Sair": "Sign out",
  "Healthcare Equipment Monitor": "Healthcare Equipment Monitor",
  "Dashboard Operacional": "Operational Dashboard",
  "Acompanhe disponibilidade, risco e performance dos equipamentos em um painel unificado para resposta rápida.": "Track availability, risk, and equipment performance in one unified panel for faster response.",
  "Tickets Abertos": "Open Tickets",
  "Em Progresso": "In Progress",
  "Resolvidos Hoje": "Resolved Today",
  "Críticos": "Critical",
  "MTTR (Reparo)": "MTTR (Repair)",
  "MTBF (Estabilidade)": "MTBF (Stability)",
  "Disponibilidade": "Availability",
  "horas": "hours",
  "dias": "days",
  "vs mês anterior": "vs previous month",
  "Primeiros Passos": "First Steps",
  "Configure o FPConnect em poucos minutos para começar a monitorar os equipamentos da sua operação.": "Configure FPConnect in a few minutes to start monitoring your operation's equipment.",
  "Cadastre suas máquinas": "Register your machines",
  "Adicione os equipamentos hospitalares que deseja monitorar.": "Add the hospital equipment you want to monitor.",
  "Configure verificações de saúde": "Configure health checks",
  "Defina verificações periódicas de disponibilidade para cada equipamento.": "Define periodic availability checks for each piece of equipment.",
  "Ative alertas": "Enable alerts",
  "Receba notificações em tempo real quando um equipamento apresentar falha.": "Receive real-time notifications when equipment fails.",
  "Gerencie tickets": "Manage tickets",
  "Abra e acompanhe chamados de manutenção corretiva e preventiva.": "Open and track corrective and preventive maintenance requests.",
  "Acompanhe métricas": "Track metrics",
  "Visualize indicadores de disponibilidade e desempenho do seu parque.": "View availability and performance indicators for your fleet.",
  "Personalize as configurações": "Customize settings",
  "Ajuste idioma, fuso horário e preferências de notificação.": "Adjust language, time zone, and notification preferences.",
  "Entrar": "Sign in",
  "Acesse a plataforma FPConnect RCA Copilot.": "Access the FPConnect RCA Copilot platform.",
  "Email": "Email",
  "Senha": "Password",
  "Credenciais inválidas.": "Invalid credentials.",
  "Entrando...": "Signing in...",
  "Perfil do Usuário": "User Profile",
  "Nome": "Name",
  "Seu nome": "Your name",
  "Email inválido": "Invalid email",
  "Celular para SMS": "Mobile phone for SMS",
  "Celular inválido": "Invalid mobile phone",
  "Celular obrigatório": "Mobile phone required",
  "Informe um número de celular válido para notificações por SMS.": "Enter a valid mobile phone number for SMS notifications.",
  "Cadastre um celular válido no perfil antes de ativar SMS.": "Register a valid mobile phone in the profile before enabling SMS.",
  "Cadastre um celular no perfil para ativar SMS": "Register a mobile phone in the profile to enable SMS",
  "Usado como destino das notificações por SMS quando esse canal estiver ativo.": "Used as the destination for SMS notifications when this channel is active.",
  "SMS ativo": "SMS active",
  "Campos obrigatórios": "Required fields",
  "Nome e email são obrigatórios.": "Name and email are required.",
  "Perfil atualizado": "Profile updated",
  "Suas informações foram salvas.": "Your information has been saved.",
  "Preferências do Sistema": "System Preferences",
  "Tema": "Theme",
  "Claro": "Light",
  "Escuro": "Dark",
  "Sistema": "System",
  "Idioma": "Language",
  "Português (BR)": "Portuguese (BR)",
  "English (US)": "English (US)",
  "Fuso Horário": "Time Zone",
  "Taxa de Atualização (s)": "Refresh Rate (s)",
  "Salvar": "Save",
  "Salvando...": "Saving...",
  "Cancelar": "Cancel",
  "Salvo com sucesso!": "Saved successfully!",
  "Erro ao salvar. Tente novamente.": "Error saving. Try again.",
  "Configurações salvas": "Settings saved",
  "Preferências do sistema atualizadas.": "System preferences updated.",
  "Preferências de Notificação": "Notification Preferences",
  "Receba alertas por email": "Receive alerts by email",
  "Receba alertas por SMS": "Receive alerts by SMS",
  "In-app": "In-app",
  "Notificações dentro do sistema": "In-app system notifications",
  "Push": "Push",
  "Notificações push do navegador": "Browser push notifications",
  "Preferências de notificação salvas": "Notification preferences saved",
  "Segurança": "Security",
  "Alterar Senha": "Change Password",
  "Senha Atual": "Current Password",
  "Nova Senha": "New Password",
  "Confirmar Nova Senha": "Confirm New Password",
  "Mínimo 8 caracteres": "Minimum 8 characters",
  "Repita a nova senha": "Repeat the new password",
  "Mostrar senhas": "Show passwords",
  "Ocultar senhas": "Hide passwords",
  "Senha alterada": "Password changed",
  "Sua senha foi atualizada com sucesso.": "Your password has been updated successfully.",
  "Dados e Privacidade": "Data and Privacy",
  "Exportar Dados": "Export Data",
  "Baixe todos os seus dados em formato JSON": "Download all your data in JSON format",
  "Exportar": "Export",
  "Exportação concluída": "Export completed",
  "O arquivo JSON foi gerado.": "The JSON file was generated.",
  "Redefinir Preferências": "Reset Preferences",
  "Restaura todas as configurações para o padrão": "Restore all settings to default",
  "Redefinir": "Reset",
  "Preferências redefinidas": "Preferences reset",
  "Todas as configurações foram restauradas.": "All settings have been restored.",
  "Pesquisar máquinas...": "Search machines...",
  "Pesquisar tickets...": "Search tickets...",
  "Pesquisar alertas...": "Search alerts...",
  "Pesquisar histórico...": "Search history...",
  "Tipo": "Type",
  "Status": "Status",
  "Prioridade": "Priority",
  "Severidade": "Severity",
  "Todos": "All",
  "Limpar filtros": "Clear filters",
  "Online": "Online",
  "Offline": "Offline",
  "Warning": "Warning",
  "Monitoramento": "Monitoring",
  "Suporte de Vida": "Life Support",
  "Infusão": "Infusion",
  "Crítico": "Critical",
  "Alto": "High",
  "Médio": "Medium",
  "Baixo": "Low",
  "Aberto": "Open",
  "Em Andamento": "In Progress",
  "Resolvido": "Resolved",
  "Pendente": "Pending",
  "Reconhecido": "Acknowledged",
  "Reconhecer": "Acknowledge",
  "Nenhum alerta encontrado.": "No alerts found.",
  "Nenhuma máquina encontrada.": "No machines found.",
  "Nenhum ticket encontrado.": "No tickets found.",
  "Nenhum evento encontrado.": "No events found.",
  "Nenhum resultado encontrado.": "No results found.",
  "ID": "ID",
  "Máquina": "Machine",
  "Localização": "Location",
  "Último Check": "Last Check",
  "Data": "Date",
  "Técnico": "Technician",
  "Agendar Manutenção": "Schedule Maintenance",
  "Agendar": "Schedule",
  "Preventiva": "Preventive",
  "Corretiva": "Corrective",
  "Calibração": "Calibration",
  "Histórico de Auditoria": "Audit History",
  "Ação": "Action",
  "Usuário": "User",
  "Recurso": "Resource",
  "Data/Hora": "Date/Time",
  "Métricas de Performance": "Performance Metrics",
  "Uptime Médio": "Average Uptime",
  "MTBF (horas)": "MTBF (hours)",
  "MTTR (minutos)": "MTTR (minutes)",
  "Alertas (7d)": "Alerts (7d)",
  "Uptime por Equipamento": "Uptime by Equipment",
  "incidente(s)": "incident(s)",
  "Create Ticket": "Create Ticket",
  "Ticket title": "Ticket title",
  "Low": "Low",
  "Medium": "Medium",
  "High": "High",
  "Critical": "Critical",
  "Create": "Create",
  "Voltar": "Previous",
  "Avançar": "Next",
  "Redirecionando para login...": "Redirecting to login...",
  "Carregando sessão...": "Loading session...",
  "Plataforma de monitoramento para operações hospitalares": "Monitoring platform for hospital operations",
  "Visibilidade total para": "Total visibility for",
  "Engenharia Clínica e TI Biomédica": "Clinical Engineering and Biomedical IT",
  "O FPConnect centraliza monitoramento, alertas, tickets e histórico operacional para sua equipe tomar decisões rápidas e reduzir indisponibilidade de equipamentos de missão crítica.": "FPConnect centralizes monitoring, alerts, tickets, and operational history so your team can make fast decisions and reduce downtime for mission-critical equipment.",
  "Acessar plataforma": "Access platform",
  "Ver painel operacional": "View operational dashboard",
  "Indicadores operacionais": "Operational indicators",
  "Equipamentos monitoráveis": "Monitorable equipment",
  "Redução média de MTTR": "Average MTTR reduction",
  "SLA de disponibilidade": "Availability SLA",
  "Observabilidade em tempo real": "Real-time observability",
  "Monitore disponibilidade, alertas e comportamento de equipamentos críticos em um único painel.": "Monitor availability, alerts, and critical equipment behavior in a single dashboard.",
  "Resposta rápida a incidentes": "Fast incident response",
  "Abra e acompanhe tickets com contexto técnico para acelerar análise RCA e reduzir MTTR.": "Open and track tickets with technical context to accelerate RCA analysis and reduce MTTR.",
  "Confiabilidade operacional": "Operational reliability",
  "Padronize verificações e priorize riscos para manter continuidade clínica e segurança do paciente.": "Standardize checks and prioritize risks to maintain clinical continuity and patient safety.",
  "Degustação gratuita": "Free trial",
  "Plano Basic para experimentar sem custo": "Basic plan to try at no cost",
  "Acesse o modo gratuito com limite máximo para conhecer a experiência do FPConnect sem compromisso. Ideal para validação inicial com sua equipe.": "Access the free mode with defined limits to experience FPConnect with no commitment. Ideal for initial validation with your team.",
  "Testar plano Basic": "Try Basic plan",
  "Menu": "Menu",
  "Planos": "Plans",
  "Abra para visualizar os planos pagos em formato de carrossel.": "Open to view the paid plans in carousel format.",
  "Abrir / Fechar": "Open / Close",
  "Operação clínica completa com diagnóstico inteligente e colaboração de equipe.": "Complete clinical operation with intelligent diagnostics and team collaboration.",
  "RCA avançado": "Advanced RCA",
  "Playbooks operacionais": "Operational playbooks",
  "Relatórios executivos": "Executive reports",
  "Suporte prioritário": "Priority support",
  "Para operações críticas com alta disponibilidade e governança multiunidade.": "For critical operations with high availability and multi-unit governance.",
  "Tudo do Premium": "Everything in Premium",
  "Contratos/SLA avançados": "Advanced contracts/SLA",
  "Prioridade máxima de processamento": "Maximum processing priority",
  "Acompanhamento estratégico": "Strategic guidance",
  "Consultoria": "Consulting",
  "Plano consultivo para transformação operacional com apoio especialista dedicado.": "Consulting plan for operational transformation with dedicated expert support.",
  "Tudo do VIP": "Everything in VIP",
  "Squad consultivo": "Consulting squad",
  "Roadmap de eficiência": "Efficiency roadmap",
  "Implantação assistida": "Assisted implementation",
  "Quero este plano": "I want this plan",
  "Com o FPConnect, reduzimos o tempo entre o alerta e a tomada de decisão. O time de engenharia clínica ganhou previsibilidade.": "With FPConnect, we reduced the time between alert and decision-making. The clinical engineering team gained predictability.",
  "Coordenadora de Engenharia Clínica": "Clinical Engineering Coordinator",
  "A visão de incidentes e causa raiz trouxe clareza para priorização. Hoje atuamos de forma muito mais proativa.": "The incident and root-cause view brought clarity to prioritization. Today we act much more proactively.",
  "Gestor de Operações Hospitalares": "Hospital Operations Manager",
  "Navegação institucional": "Institutional navigation",
  "Missão": "Mission",
  "Visão": "Vision",
  "Valores": "Values",
  "Quem somos": "Who we are",
  "Ajuda / FAQs": "Help / FAQs",
  "Conectar engenharia clínica, TI biomédica e operação hospitalar em uma plataforma única para reduzir indisponibilidade, acelerar resposta a incidentes e proteger a segurança do paciente.": "Connect clinical engineering, biomedical IT, and hospital operations in a single platform to reduce downtime, accelerate incident response, and protect patient safety.",
  "Ser a plataforma de referência para operações hospitalares orientadas por dados, tornando cada decisão de disponibilidade, manutenção e risco mais rápida, rastreável e confiável.": "Become the reference platform for data-driven hospital operations, making every availability, maintenance, and risk decision faster, traceable, and reliable.",
  "Cultura operacional": "Operational culture",
  "Segurança do paciente": "Patient safety",
  "Toda priorização parte do impacto clínico e da continuidade assistencial.": "Every prioritization starts with clinical impact and continuity of care.",
  "Alertas, tickets e métricas precisam sustentar decisões consistentes no dia a dia.": "Alerts, tickets, and metrics must support consistent day-to-day decisions.",
  "Clareza para decisão": "Decision clarity",
  "Dados técnicos devem virar contexto simples para gestores, equipes e fornecedores.": "Technical data should become clear context for managers, teams, and suppliers.",
  "Rastreabilidade": "Traceability",
  "Cada ocorrência deve manter histórico, responsável, evidência e evolução visíveis.": "Every occurrence should keep visible history, ownership, evidence, and progress.",
  "Institucional": "Institutional",
  "Somos a FPConnect Technologies, uma empresa focada em tecnologia para engenharia clínica, TI biomédica e operações hospitalares.": "We are FPConnect Technologies, a company focused on technology for clinical engineering, biomedical IT, and hospital operations.",
  "Criamos uma plataforma para centralizar monitoramento, chamados, histórico e métricas de disponibilidade em ambientes de missão crítica.": "We built a platform to centralize monitoring, tickets, history, and availability metrics in mission-critical environments.",
  "Nosso compromisso é entregar uma operação mais previsível, rastreável e preparada para tomada de decisão.": "Our commitment is to deliver a more predictable, traceable operation prepared for decision-making.",
  "Suporte": "Support",
  "Buscar nas FAQs...": "Search FAQs...",
  "Como cadastrar um novo equipamento?": "How do I register new equipment?",
  "Acesse o menu Máquinas e clique em 'Novo Equipamento'.": "Open the Machines menu and click 'New Equipment'.",
  "Como visualizar alertas?": "How do I view alerts?",
  "Clique no ícone de sino no cabeçalho para ver todos os alertas.": "Click the bell icon in the header to view all alerts.",
  "Como gerar relatórios?": "How do I generate reports?",
  "Acesse o menu Métricas e selecione o período desejado.": "Open the Metrics menu and select the desired period.",
  "Como abrir um chamado?": "How do I open a ticket?",
  "Vá em Tickets e clique em 'Novo Ticket'.": "Go to Tickets and click 'New Ticket'.",
  "Como configurar notificações?": "How do I configure notifications?",
  "Acesse Configurações > Notificações para personalizar.": "Open Settings > Notifications to customize.",
  "Nenhuma pergunta encontrada.": "No question found.",
  "FPConnect™ - Marca registrada. © 2026 Todos os direitos reservados.": "FPConnect™ - Registered trademark. © 2026 All rights reserved.",
};

const EN_TO_PT = Object.fromEntries(
  Object.entries(PT_TO_EN).map(([pt, en]) => [en, pt]),
);

const originalText = new WeakMap<Text, string>();
const originalAttributes = new WeakMap<Element, Map<string, string>>();

function readLanguage(): Language {
  try {
    const raw = localStorage.getItem(SYSTEM_STORAGE_KEY);
    const language = raw ? JSON.parse(raw).language : "pt-BR";
    return language === "en-US" ? "en-US" : "pt-BR";
  } catch {
    return "pt-BR";
  }
}

function translateValue(value: string, language: Language): string {
  const trimmed = value.trim();
  if (!trimmed) return value;

  const dictionary = language === "en-US" ? PT_TO_EN : EN_TO_PT;
  const normalized = trimmed.replace(/\s+/g, " ");
  const translated = dictionary[trimmed] ?? dictionary[normalized];
  if (translated) return value.replace(trimmed, translated);

  if (language === "en-US") {
    return value
      .replace(/^Página (\d+) de (\d+)$/, "Page $1 of $2")
      .replace(/^(.+) vs semana anterior$/, "$1 vs previous week");
  }

  return value
    .replace(/^Page (\d+) of (\d+)$/, "Página $1 de $2")
    .replace(/^(.+) vs previous week$/, "$1 vs semana anterior");
}

function translateTextNode(node: Text, language: Language) {
  const parent = node.parentElement;
  if (!parent || ["SCRIPT", "STYLE", "TEXTAREA"].includes(parent.tagName)) return;
  if (parent.closest("[data-no-translate]")) return;
  if (!originalText.has(node)) {
    originalText.set(node, node.nodeValue ?? "");
  }
  const base = originalText.get(node) ?? "";
  const next = translateValue(base, language);
  if (node.nodeValue !== next) node.nodeValue = next;
}

function translateElementAttributes(element: Element, language: Language) {
  if (element.closest("[data-no-translate]")) return;

  const attributes = ["placeholder", "aria-label", "title"];
  let stored = originalAttributes.get(element);
  if (!stored) {
    stored = new Map();
    originalAttributes.set(element, stored);
  }

  for (const attr of attributes) {
    const current = element.getAttribute(attr);
    if (!current) continue;
    if (!stored.has(attr)) stored.set(attr, current);
    const next = translateValue(stored.get(attr) ?? current, language);
    if (current !== next) element.setAttribute(attr, next);
  }
}

function applyLanguage(language: Language) {
  document.documentElement.lang = language;

  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node = walker.nextNode();
  while (node) {
    translateTextNode(node as Text, language);
    node = walker.nextNode();
  }

  document.body.querySelectorAll("*").forEach((element) => {
    translateElementAttributes(element, language);
  });
}

export function notifyLanguageChanged() {
  window.dispatchEvent(new Event(LANGUAGE_CHANGE_EVENT));
}

export default function LanguageRuntime() {
  useEffect(() => {
    const run = () => applyLanguage(readLanguage());
    run();

    const observer = new MutationObserver(() => {
      window.requestAnimationFrame(run);
    });
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: true,
      attributeFilter: ["placeholder", "aria-label", "title"],
    });

    window.addEventListener(LANGUAGE_CHANGE_EVENT, run);
    window.addEventListener("storage", run);

    return () => {
      observer.disconnect();
      window.removeEventListener(LANGUAGE_CHANGE_EVENT, run);
      window.removeEventListener("storage", run);
    };
  }, []);

  return null;
}
