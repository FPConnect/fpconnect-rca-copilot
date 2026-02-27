import React, { useState } from "react";
import {
  View,
  Text,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Switch,
  StyleSheet,
  Alert,
  SafeAreaView,
} from "react-native";

interface NotificationPrefs {
  email: boolean;
  sms: boolean;
  inApp: boolean;
  push: boolean;
}

const INITIAL_NOTIF: NotificationPrefs = {
  email: true,
  sms: false,
  inApp: true,
  push: false,
};

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={styles.sectionCard}>
      <Text style={styles.sectionTitle}>{title}</Text>
      <View style={styles.sectionDivider} />
      {children}
    </View>
  );
}

function ToggleRow({
  label,
  description,
  value,
  onValueChange,
}: {
  label: string;
  description?: string;
  value: boolean;
  onValueChange: (v: boolean) => void;
}) {
  return (
    <View style={styles.toggleRow}>
      <View style={styles.toggleLabel}>
        <Text style={styles.toggleLabelText}>{label}</Text>
        {description ? (
          <Text style={styles.toggleDesc}>{description}</Text>
        ) : null}
      </View>
      <Switch
        value={value}
        onValueChange={onValueChange}
        trackColor={{ false: "#d1d5db", true: "#2563eb" }}
        thumbColor="#ffffff"
      />
    </View>
  );
}

export default function SettingsScreen() {
  const [name, setName] = useState("Admin");
  const [email, setEmail] = useState("admin@hospital.com");
  const [notifPrefs, setNotifPrefs] = useState<NotificationPrefs>(INITIAL_NOTIF);
  const [theme, setTheme] = useState<"light" | "dark" | "system">("light");

  const handleProfileSave = () => {
    if (!name.trim() || !email.trim()) {
      Alert.alert("Error", "Name and email are required.");
      return;
    }
    Alert.alert("Success", "Profile saved successfully.");
  };

  const handleReset = () => {
    Alert.alert("Reset Preferences", "Restore all settings to default?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Reset",
        style: "destructive",
        onPress: () => {
          setNotifPrefs(INITIAL_NOTIF);
          setTheme("light");
          Alert.alert("Done", "Preferences have been reset.");
        },
      },
    ]);
  };

  const THEMES: Array<"light" | "dark" | "system"> = ["light", "dark", "system"];

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        {/* Profile */}
        <SectionCard title="User Profile">
          <Text style={styles.fieldLabel}>Name</Text>
          <TextInput
            style={styles.input}
            value={name}
            onChangeText={setName}
            placeholder="Your name"
            placeholderTextColor="#9ca3af"
          />
          <Text style={styles.fieldLabel}>Email</Text>
          <TextInput
            style={styles.input}
            value={email}
            onChangeText={setEmail}
            placeholder="your@email.com"
            placeholderTextColor="#9ca3af"
            keyboardType="email-address"
            autoCapitalize="none"
          />
          <TouchableOpacity style={styles.saveBtn} onPress={handleProfileSave}>
            <Text style={styles.saveBtnText}>Save Profile</Text>
          </TouchableOpacity>
        </SectionCard>

        {/* Theme */}
        <SectionCard title="Appearance">
          <View style={styles.themeRow}>
            {THEMES.map((t) => (
              <TouchableOpacity
                key={t}
                style={[styles.themeBtn, theme === t && styles.themeBtnActive]}
                onPress={() => setTheme(t)}
              >
                <Text
                  style={[styles.themeBtnText, theme === t && styles.themeBtnTextActive]}
                >
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </SectionCard>

        {/* Notifications */}
        <SectionCard title="Notification Preferences">
          <ToggleRow
            label="Email"
            description="Receive alerts by email"
            value={notifPrefs.email}
            onValueChange={(v) => setNotifPrefs((p) => ({ ...p, email: v }))}
          />
          <ToggleRow
            label="SMS"
            description="Receive alerts by SMS"
            value={notifPrefs.sms}
            onValueChange={(v) => setNotifPrefs((p) => ({ ...p, sms: v }))}
          />
          <ToggleRow
            label="In-app"
            description="Notifications inside the app"
            value={notifPrefs.inApp}
            onValueChange={(v) => setNotifPrefs((p) => ({ ...p, inApp: v }))}
          />
          <ToggleRow
            label="Push"
            description="Push notifications"
            value={notifPrefs.push}
            onValueChange={(v) => setNotifPrefs((p) => ({ ...p, push: v }))}
          />
          <TouchableOpacity
            style={styles.saveBtn}
            onPress={() => Alert.alert("Success", "Notification preferences saved.")}
          >
            <Text style={styles.saveBtnText}>Save Preferences</Text>
          </TouchableOpacity>
        </SectionCard>

        {/* Data & Privacy */}
        <SectionCard title="Data & Privacy">
          <View style={styles.dataRow}>
            <View style={styles.dataInfo}>
              <Text style={styles.dataLabel}>Export Data</Text>
              <Text style={styles.dataDesc}>Download all your data as JSON</Text>
            </View>
            <TouchableOpacity
              style={styles.outlineBtn}
              onPress={() => Alert.alert("Export", "Your data will be sent by email.")}
            >
              <Text style={styles.outlineBtnText}>Export</Text>
            </TouchableOpacity>
          </View>
          <View style={[styles.dataRow, styles.dataRowDanger]}>
            <View style={styles.dataInfo}>
              <Text style={styles.dangerLabel}>Reset Preferences</Text>
              <Text style={styles.dangerDesc}>Restore all settings to default</Text>
            </View>
            <TouchableOpacity style={styles.dangerBtn} onPress={handleReset}>
              <Text style={styles.dangerBtnText}>Reset</Text>
            </TouchableOpacity>
          </View>
        </SectionCard>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 32 },
  sectionCard: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    shadowColor: "#000",
    shadowOpacity: 0.06,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
    elevation: 4,
  },
  sectionTitle: { fontSize: 15, fontWeight: "600", color: "#1f2937", marginBottom: 8 },
  sectionDivider: { height: 1, backgroundColor: "#f3f4f6", marginBottom: 12 },
  fieldLabel: { fontSize: 13, fontWeight: "500", color: "#374151", marginBottom: 4 },
  input: {
    borderWidth: 1,
    borderColor: "#e5e7eb",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    color: "#111827",
    marginBottom: 12,
  },
  saveBtn: {
    backgroundColor: "#2563eb",
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: "center",
    marginTop: 4,
  },
  saveBtnText: { color: "#ffffff", fontWeight: "700", fontSize: 14 },
  themeRow: { flexDirection: "row", gap: 8 },
  themeBtn: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e5e7eb",
    alignItems: "center",
    backgroundColor: "#f9fafb",
  },
  themeBtnActive: { backgroundColor: "#dbeafe", borderColor: "#2563eb" },
  themeBtnText: { fontSize: 13, fontWeight: "500", color: "#6b7280" },
  themeBtnTextActive: { color: "#1e40af", fontWeight: "700" },
  toggleRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#f3f4f6",
  },
  toggleLabel: { flex: 1, marginRight: 12 },
  toggleLabelText: { fontSize: 14, fontWeight: "500", color: "#374151" },
  toggleDesc: { fontSize: 12, color: "#9ca3af", marginTop: 2 },
  dataRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 12,
    backgroundColor: "#f9fafb",
    borderRadius: 8,
    marginBottom: 8,
  },
  dataRowDanger: { backgroundColor: "#fff5f5" },
  dataInfo: { flex: 1, marginRight: 10 },
  dataLabel: { fontSize: 13, fontWeight: "600", color: "#374151" },
  dataDesc: { fontSize: 11, color: "#9ca3af", marginTop: 2 },
  dangerLabel: { fontSize: 13, fontWeight: "600", color: "#dc2626" },
  dangerDesc: { fontSize: 11, color: "#fca5a5", marginTop: 2 },
  outlineBtn: {
    borderWidth: 1,
    borderColor: "#d1d5db",
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 7,
  },
  outlineBtnText: { fontSize: 13, fontWeight: "500", color: "#374151" },
  dangerBtn: {
    borderWidth: 1,
    borderColor: "#fca5a5",
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 7,
  },
  dangerBtnText: { fontSize: 13, fontWeight: "500", color: "#dc2626" },
});
