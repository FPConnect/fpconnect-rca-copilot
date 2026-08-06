"use client";

import { useEffect } from "react";

const SYSTEM_STORAGE_KEY = "fpconnect_system_preferences";
const LANGUAGE_CHANGE_EVENT = "fpconnect:language-change";
const LANGUAGE_BASELINE_KEY = "fpconnect_language_baseline_v2";

type Language = "pt-BR" | "en-US";

const PT_TO_EN: Record<string, string> = {
  "FPConnect": "FPConnect",
  "Tecnologias": "Technologies",
  "Início": "Home",
  "Radar de Risco": "Risk Radar",
  "RCA com Evidências": "RCA Evidence",
  "Motor de Valor": "Value Engine",
  "Máquinas": "Machines",
  "Verificações": "Health Checks",
  "Alertas": "Alerts",
  "Chamados": "Tickets",
  "Métricas": "Metrics",
  "Manutenção": "Maintenance",
  "Controle de Acesso": "Access Control",
  "Histórico": "History",
  "Notificações": "Notifications",
  "Configurações": "Settings",
  "Sair": "Sign out",
  "Monitor de Equipamentos Clínicos": "Healthcare Equipment Monitor",
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
  "Ative o Radar de Risco Clínico": "Enable Clinical Risk Radar",
  "Cruze UDI, firmware, recall, cibersegurança e risco regulatório por equipamento.": "Cross-check UDI, firmware, recall, cybersecurity, and regulatory risk by equipment.",
  "Use RCA com evidência": "Use evidence-backed RCA",
  "Gere causa provável com manuais, histórico, contenção e pacote para fornecedor.": "Generate probable cause with manuals, history, containment, and supplier package.",
  "Mostre ROI e renovação": "Show ROI and renewal",
  "Converta indisponibilidade evitada em valor financeiro e expansão contratual.": "Convert avoided downtime into financial value and contract expansion.",
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
  "Pesquisar chamados...": "Search tickets...",
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
  "Nenhum chamado encontrado.": "No tickets found.",
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
  "Criar chamado": "Create Ticket",
  "Título do chamado": "Ticket title",
  "Low": "Low",
  "Medium": "Medium",
  "High": "High",
  "Critical": "Critical",
  "Create": "Create",
  "Voltar": "Previous",
  "Avançar": "Next",
  "Redirecionando para login...": "Redirecting to login...",
  "Carregando sessão...": "Loading session...",
};

const EN_TO_PT = Object.fromEntries(
  Object.entries(PT_TO_EN).map(([pt, en]) => [en, pt]),
);

const originalText = new WeakMap<Text, string>();
const originalAttributes = new WeakMap<Element, Map<string, string>>();

function normalizeLegacyLanguagePreference() {
  const baseline = localStorage.getItem(LANGUAGE_BASELINE_KEY);
  if (baseline === "portuguese-copy-2026-08") return;

  const raw = localStorage.getItem(SYSTEM_STORAGE_KEY);
  if (raw) {
    try {
      const preferences = JSON.parse(raw) as { language?: Language };
      if (preferences.language === "en-US") {
        localStorage.setItem(
          SYSTEM_STORAGE_KEY,
          JSON.stringify({ ...preferences, language: "pt-BR" }),
        );
      }
    } catch {
      localStorage.removeItem(SYSTEM_STORAGE_KEY);
    }
  }

  localStorage.setItem(LANGUAGE_BASELINE_KEY, "portuguese-copy-2026-08");
}

function readLanguage(): Language {
  try {
    normalizeLegacyLanguagePreference();
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
  const translated = dictionary[trimmed];
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
  if (!originalText.has(node)) {
    originalText.set(node, node.nodeValue ?? "");
  }
  const base = originalText.get(node) ?? "";
  const next = translateValue(base, language);
  if (node.nodeValue !== next) node.nodeValue = next;
}

function translateElementAttributes(element: Element, language: Language) {
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
