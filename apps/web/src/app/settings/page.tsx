"use client";

import { useState } from "react";
import { Save, X, Eye, EyeOff, CheckCircle, AlertCircle } from "lucide-react";
import { useNotifications } from "@/contexts/NotificationContext";

interface ProfileForm {
  name: string;
  email: string;
}

interface PasswordForm {
  current: string;
  newPassword: string;
  confirm: string;
}

interface NotificationPrefs {
  email: boolean;
  sms: boolean;
  inApp: boolean;
  push: boolean;
}

interface SystemPrefs {
  theme: "light" | "dark" | "system";
  language: "pt-BR" | "en-US";
  timezone: string;
  refreshRate: number;
}

const TIMEZONES = [
  "America/Sao_Paulo",
  "America/New_York",
  "America/Los_Angeles",
  "Europe/London",
  "Europe/Lisbon",
  "UTC",
];

const INITIAL_PROFILE: ProfileForm = { name: "Admin", email: "admin@hospital.com" };
const INITIAL_SYSTEM: SystemPrefs = {
  theme: "light",
  language: "pt-BR",
  timezone: "America/Sao_Paulo",
  refreshRate: 30,
};
const INITIAL_NOTIF: NotificationPrefs = {
  email: true,
  sms: false,
  inApp: true,
  push: false,
};

type SaveStatus = "idle" | "saving" | "success" | "error";

function useSaveStatus() {
  const [status, setStatus] = useState<SaveStatus>("idle");

  const save = async (fn: () => Promise<void> | void) => {
    setStatus("saving");
    try {
      await fn();
      setStatus("success");
      setTimeout(() => setStatus("idle"), 3000);
    } catch {
      setStatus("error");
      setTimeout(() => setStatus("idle"), 3000);
    }
  };

  return { status, save };
}

function StatusBanner({ status }: { status: SaveStatus }) {
  if (status === "idle" || status === "saving") return null;
  if (status === "success")
    return (
      <div className="flex items-center gap-2 text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg px-4 py-2">
        <CheckCircle size={16} />
        Salvo com sucesso!
      </div>
    );
  return (
    <div className="flex items-center gap-2 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg px-4 py-2">
      <AlertCircle size={16} />
      Erro ao salvar. Tente novamente.
    </div>
  );
}

function SectionCard({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="bg-white rounded-xl shadow p-6 mb-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4 pb-3 border-b border-gray-100">
        {title}
      </h2>
      {children}
    </div>
  );
}

function Toggle({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description?: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between py-3 gap-4 overflow-hidden">
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-gray-700">{label}</p>
        {description && (
          <p className="text-xs text-gray-400 mt-0.5">{description}</p>
        )}
      </div>
      <button
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={`relative flex-shrink-0 w-11 h-6 rounded-full overflow-hidden transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
          checked ? "bg-blue-600" : "bg-gray-200"
        }`}
      >
        <span
          className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${
            checked ? "translate-x-5" : "translate-x-0"
          }`}
        />
      </button>
    </div>
  );
}

export default function SettingsPage() {
  const { addNotification } = useNotifications();

  /* Profile */
  const [profile, setProfile] = useState<ProfileForm>(INITIAL_PROFILE);
  const [profileDraft, setProfileDraft] = useState<ProfileForm>(INITIAL_PROFILE);
  const profileSave = useSaveStatus();

  const handleProfileSave = () => {
    if (!profileDraft.name.trim() || !profileDraft.email.trim()) {
      addNotification("error", "Campos obrigatórios", "Nome e email são obrigatórios.");
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(profileDraft.email)) {
      addNotification("error", "Email inválido", "Por favor, insira um email válido.");
      return;
    }
    profileSave.save(() => {
      setProfile(profileDraft);
      addNotification("success", "Perfil atualizado", "Suas informações foram salvas.");
    });
  };

  /* System */
  const [system, setSystem] = useState<SystemPrefs>(INITIAL_SYSTEM);
  const [systemDraft, setSystemDraft] = useState<SystemPrefs>(INITIAL_SYSTEM);
  const systemSave = useSaveStatus();

  const handleSystemSave = () => {
    systemSave.save(() => {
      setSystem(systemDraft);
      addNotification("success", "Configurações salvas", "Preferências do sistema atualizadas.");
    });
  };

  /* Notifications */
  const [notifPrefs, setNotifPrefs] = useState<NotificationPrefs>(INITIAL_NOTIF);
  const [notifDraft, setNotifDraft] = useState<NotificationPrefs>(INITIAL_NOTIF);
  const notifSave = useSaveStatus();

  const handleNotifSave = () => {
    notifSave.save(() => {
      setNotifPrefs(notifDraft);
      addNotification("success", "Preferências de notificação salvas");
    });
  };

  /* Password */
  const [passwordForm, setPasswordForm] = useState<PasswordForm>({
    current: "",
    newPassword: "",
    confirm: "",
  });
  const [showPasswords, setShowPasswords] = useState(false);
  const passwordSave = useSaveStatus();

  const handlePasswordSave = () => {
    if (!passwordForm.current || !passwordForm.newPassword || !passwordForm.confirm) {
      addNotification("error", "Campos obrigatórios", "Preencha todos os campos de senha.");
      return;
    }
    if (passwordForm.newPassword.length < 8) {
      addNotification("error", "Senha muito curta", "A nova senha deve ter pelo menos 8 caracteres.");
      return;
    }
    if (passwordForm.newPassword !== passwordForm.confirm) {
      addNotification("error", "Senhas não coincidem", "A confirmação da senha não corresponde.");
      return;
    }
    passwordSave.save(() => {
      setPasswordForm({ current: "", newPassword: "", confirm: "" });
      addNotification("success", "Senha alterada", "Sua senha foi atualizada com sucesso.");
    });
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Configurações</h1>

      {/* Profile */}
      <SectionCard title="Perfil do Usuário">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nome <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={profileDraft.name}
              onChange={(e) =>
                setProfileDraft((p) => ({ ...p, name: e.target.value }))
              }
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Seu nome"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email <span className="text-red-500">*</span>
            </label>
            <input
              type="email"
              value={profileDraft.email}
              onChange={(e) =>
                setProfileDraft((p) => ({ ...p, email: e.target.value }))
              }
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="seu@email.com"
            />
          </div>
          <div className="flex items-center justify-between pt-2">
            <StatusBanner status={profileSave.status} />
            <div className="flex gap-2 ml-auto">
              <button
                onClick={() => setProfileDraft(profile)}
                className="flex items-center gap-1.5 px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
              >
                <X size={14} />
                Cancelar
              </button>
              <button
                onClick={handleProfileSave}
                disabled={profileSave.status === "saving"}
                className="flex items-center gap-1.5 px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                <Save size={14} />
                {profileSave.status === "saving" ? "Salvando..." : "Salvar"}
              </button>
            </div>
          </div>
        </div>
      </SectionCard>

      {/* System Preferences */}
      <SectionCard title="Preferências do Sistema">
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tema
              </label>
              <select
                value={systemDraft.theme}
                onChange={(e) =>
                  setSystemDraft((p) => ({
                    ...p,
                    theme: e.target.value as SystemPrefs["theme"],
                  }))
                }
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="light">Claro</option>
                <option value="dark">Escuro</option>
                <option value="system">Sistema</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Idioma
              </label>
              <select
                value={systemDraft.language}
                onChange={(e) =>
                  setSystemDraft((p) => ({
                    ...p,
                    language: e.target.value as SystemPrefs["language"],
                  }))
                }
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="pt-BR">Português (BR)</option>
                <option value="en-US">English (US)</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Fuso Horário
              </label>
              <select
                value={systemDraft.timezone}
                onChange={(e) =>
                  setSystemDraft((p) => ({ ...p, timezone: e.target.value }))
                }
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {TIMEZONES.map((tz) => (
                  <option key={tz} value={tz}>
                    {tz}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Taxa de Atualização (s)
              </label>
              <select
                value={systemDraft.refreshRate}
                onChange={(e) =>
                  setSystemDraft((p) => ({
                    ...p,
                    refreshRate: Number(e.target.value),
                  }))
                }
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {[10, 15, 30, 60, 120].map((v) => (
                  <option key={v} value={v}>
                    {v}s
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex items-center justify-between pt-2">
            <StatusBanner status={systemSave.status} />
            <div className="flex gap-2 ml-auto">
              <button
                onClick={() => setSystemDraft(system)}
                className="flex items-center gap-1.5 px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
              >
                <X size={14} />
                Cancelar
              </button>
              <button
                onClick={handleSystemSave}
                disabled={systemSave.status === "saving"}
                className="flex items-center gap-1.5 px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
              >
                <Save size={14} />
                {systemSave.status === "saving" ? "Salvando..." : "Salvar"}
              </button>
            </div>
          </div>
        </div>
      </SectionCard>

      {/* Notification Preferences */}
      <SectionCard title="Preferências de Notificação">
        <div className="divide-y divide-gray-100">
          <Toggle
            label="Email"
            description="Receba alertas por email"
            checked={notifDraft.email}
            onChange={(v) => setNotifDraft((p) => ({ ...p, email: v }))}
          />
          <Toggle
            label="SMS"
            description="Receba alertas por SMS"
            checked={notifDraft.sms}
            onChange={(v) => setNotifDraft((p) => ({ ...p, sms: v }))}
          />
          <Toggle
            label="In-app"
            description="Notificações dentro do sistema"
            checked={notifDraft.inApp}
            onChange={(v) => setNotifDraft((p) => ({ ...p, inApp: v }))}
          />
          <Toggle
            label="Push"
            description="Notificações push do navegador"
            checked={notifDraft.push}
            onChange={(v) => setNotifDraft((p) => ({ ...p, push: v }))}
          />
        </div>
        <div className="flex items-center justify-between pt-4 border-t border-gray-100 mt-4">
          <StatusBanner status={notifSave.status} />
          <div className="flex gap-2 ml-auto">
            <button
              onClick={() => setNotifDraft(notifPrefs)}
              className="flex items-center gap-1.5 px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
            >
              <X size={14} />
              Cancelar
            </button>
            <button
              onClick={handleNotifSave}
              disabled={notifSave.status === "saving"}
              className="flex items-center gap-1.5 px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              <Save size={14} />
              {notifSave.status === "saving" ? "Salvando..." : "Salvar"}
            </button>
          </div>
        </div>
      </SectionCard>

      {/* Security */}
      <SectionCard title="Segurança">
        <h3 className="text-sm font-semibold text-gray-600 mb-3">
          Alterar Senha
        </h3>
        <div className="space-y-3">
          <div className="relative">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Senha Atual
            </label>
            <input
              type={showPasswords ? "text" : "password"}
              value={passwordForm.current}
              onChange={(e) =>
                setPasswordForm((p) => ({ ...p, current: e.target.value }))
              }
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10"
              placeholder="••••••••"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nova Senha
            </label>
            <input
              type={showPasswords ? "text" : "password"}
              value={passwordForm.newPassword}
              onChange={(e) =>
                setPasswordForm((p) => ({ ...p, newPassword: e.target.value }))
              }
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Mínimo 8 caracteres"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Confirmar Nova Senha
            </label>
            <input
              type={showPasswords ? "text" : "password"}
              value={passwordForm.confirm}
              onChange={(e) =>
                setPasswordForm((p) => ({ ...p, confirm: e.target.value }))
              }
              className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Repita a nova senha"
            />
          </div>
          <button
            type="button"
            onClick={() => setShowPasswords((v) => !v)}
            className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-700"
          >
            {showPasswords ? <EyeOff size={14} /> : <Eye size={14} />}
            {showPasswords ? "Ocultar senhas" : "Mostrar senhas"}
          </button>
        </div>
        <div className="flex items-center justify-between pt-4 border-t border-gray-100 mt-4">
          <StatusBanner status={passwordSave.status} />
          <div className="flex gap-2 ml-auto">
            <button
              onClick={() =>
                setPasswordForm({ current: "", newPassword: "", confirm: "" })
              }
              className="flex items-center gap-1.5 px-4 py-2 text-sm border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
            >
              <X size={14} />
              Cancelar
            </button>
            <button
              onClick={handlePasswordSave}
              disabled={passwordSave.status === "saving"}
              className="flex items-center gap-1.5 px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              <Save size={14} />
              {passwordSave.status === "saving" ? "Salvando..." : "Alterar Senha"}
            </button>
          </div>
        </div>
      </SectionCard>

      {/* Data Management */}
      <SectionCard title="Dados e Privacidade">
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p className="text-sm font-medium text-gray-700">
                Exportar Dados
              </p>
              <p className="text-xs text-gray-400 mt-0.5">
                Baixe todos os seus dados em formato JSON
              </p>
            </div>
            <button
              onClick={() =>
                addNotification("info", "Exportação iniciada", "Seus dados serão enviados por email.")
              }
              className="text-sm px-4 py-2 border border-gray-200 rounded-lg text-gray-600 hover:bg-white transition-colors"
            >
              Exportar
            </button>
          </div>
          <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
            <div>
              <p className="text-sm font-medium text-red-700">
                Redefinir Preferências
              </p>
              <p className="text-xs text-red-400 mt-0.5">
                Restaura todas as configurações para o padrão
              </p>
            </div>
            <button
              onClick={() => {
                setSystemDraft(INITIAL_SYSTEM);
                setSystem(INITIAL_SYSTEM);
                setNotifDraft(INITIAL_NOTIF);
                setNotifPrefs(INITIAL_NOTIF);
                addNotification("warning", "Preferências redefinidas", "Todas as configurações foram restauradas.");
              }}
              className="text-sm px-4 py-2 border border-red-200 rounded-lg text-red-600 hover:bg-red-100 transition-colors"
            >
              Redefinir
            </button>
          </div>
        </div>
      </SectionCard>
    </div>
  );
}
