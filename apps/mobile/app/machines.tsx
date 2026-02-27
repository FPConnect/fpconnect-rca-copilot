import React, { useState, useMemo } from "react";
import {
  View,
  Text,
  ScrollView,
  TextInput,
  StyleSheet,
} from "react-native";

interface Machine {
  id: string;
  name: string;
  location: string;
  status: "online" | "warning" | "offline";
  lastCheck: string;
  type: string;
}

const MACHINES: Machine[] = [
  { id: "M001", name: "MRI Scanner", location: "Ward A", status: "online", lastCheck: "2 min ago", type: "Imaging" },
  { id: "M002", name: "ECG Monitor", location: "ICU", status: "warning", lastCheck: "5 min ago", type: "Monitoring" },
  { id: "M003", name: "Ventilator", location: "Ward B", status: "online", lastCheck: "1 min ago", type: "Life Support" },
  { id: "M004", name: "Defibrillator", location: "Emergency", status: "offline", lastCheck: "1 hour ago", type: "Life Support" },
  { id: "M005", name: "Patient Monitor", location: "Ward C", status: "online", lastCheck: "3 min ago", type: "Monitoring" },
  { id: "M006", name: "Infusion Pump", location: "Ward A", status: "online", lastCheck: "2 min ago", type: "Infusion" },
];

const STATUS_COLORS: Record<string, { bg: string; text: string }> = {
  online: { bg: "#dcfce7", text: "#166534" },
  warning: { bg: "#fef9c3", text: "#854d0e" },
  offline: { bg: "#fee2e2", text: "#991b1b" },
};

export default function MachinesScreen() {
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    if (!q) return MACHINES;
    return MACHINES.filter(
      (m) =>
        m.name.toLowerCase().includes(q) ||
        m.id.toLowerCase().includes(q) ||
        m.location.toLowerCase().includes(q)
    );
  }, [search]);

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search machines..."
          placeholderTextColor="#9ca3af"
          value={search}
          onChangeText={setSearch}
        />

        {filtered.length === 0 ? (
          <View style={styles.empty}>
            <Text style={styles.emptyText}>No machines found.</Text>
          </View>
        ) : (
          filtered.map((m) => {
            const sc = STATUS_COLORS[m.status] ?? { bg: "#f3f4f6", text: "#374151" };
            return (
              <View key={m.id} style={styles.card}>
                <View style={styles.cardHeader}>
                  <Text style={styles.machineName}>{m.name}</Text>
                  <View style={[styles.badge, { backgroundColor: sc.bg }]}>
                    <Text style={[styles.badgeText, { color: sc.text }]}>
                      {m.status}
                    </Text>
                  </View>
                </View>
                <View style={styles.cardMeta}>
                  <Text style={styles.metaText}>
                    <Text style={styles.metaLabel}>ID: </Text>{m.id}
                  </Text>
                  <Text style={styles.metaDot}>·</Text>
                  <Text style={styles.metaText}>
                    <Text style={styles.metaLabel}>Loc: </Text>{m.location}
                  </Text>
                </View>
                <View style={styles.cardMeta}>
                  <Text style={styles.metaText}>
                    <Text style={styles.metaLabel}>Type: </Text>{m.type}
                  </Text>
                  <Text style={styles.metaDot}>·</Text>
                  <Text style={styles.metaText}>
                    <Text style={styles.metaLabel}>Last check: </Text>{m.lastCheck}
                  </Text>
                </View>
              </View>
            );
          })
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 32 },
  searchInput: {
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#e5e7eb",
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 14,
    color: "#111827",
    marginBottom: 14,
  },
  empty: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 32,
    alignItems: "center",
  },
  emptyText: { fontSize: 14, color: "#9ca3af" },
  card: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 14,
    marginBottom: 10,
    shadowColor: "#000",
    shadowOpacity: 0.06,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
    elevation: 4,
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 8,
  },
  machineName: { fontSize: 15, fontWeight: "600", color: "#111827" },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 99,
  },
  badgeText: { fontSize: 11, fontWeight: "700", textTransform: "capitalize" },
  cardMeta: { flexDirection: "row", alignItems: "center", marginTop: 2 },
  metaText: { fontSize: 12, color: "#6b7280" },
  metaLabel: { fontWeight: "600", color: "#374151" },
  metaDot: { fontSize: 12, color: "#d1d5db", marginHorizontal: 6 },
});
