import React, { useState, useMemo } from "react";
import {
  View,
  Text,
  ScrollView,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from "react-native";

interface Ticket {
  id: string;
  title: string;
  status: "open" | "in_progress" | "resolved";
  priority: "critical" | "high" | "medium" | "low";
}

const INITIAL_TICKETS: Ticket[] = [
  { id: "1", title: "MRI Scanner offline - Ward A", status: "open", priority: "critical" },
  { id: "2", title: "ECG Monitor slow response", status: "in_progress", priority: "high" },
  { id: "3", title: "Patient monitor alarm", status: "open", priority: "medium" },
];

const PRIORITY_COLORS: Record<string, { bg: string; text: string }> = {
  critical: { bg: "#fee2e2", text: "#991b1b" },
  high: { bg: "#ffedd5", text: "#9a3412" },
  medium: { bg: "#fef9c3", text: "#854d0e" },
  low: { bg: "#dcfce7", text: "#166534" },
};

const STATUS_LABELS: Record<string, string> = {
  open: "Open",
  in_progress: "In Progress",
  resolved: "Resolved",
};

export default function TicketsScreen() {
  const [tickets, setTickets] = useState<Ticket[]>(INITIAL_TICKETS);
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState<Ticket["priority"]>("medium");
  const [search, setSearch] = useState("");

  const PRIORITIES: Ticket["priority"][] = ["low", "medium", "high", "critical"];

  const handleCreate = () => {
    if (!title.trim()) {
      Alert.alert("Error", "Please enter a ticket title.");
      return;
    }
    const newTicket: Ticket = {
      id: String(Date.now()),
      title: title.trim(),
      status: "open",
      priority,
    };
    setTickets([newTicket, ...tickets]);
    setTitle("");
    setPriority("medium");
  };

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    if (!q) return tickets;
    return tickets.filter((t) => t.title.toLowerCase().includes(q));
  }, [tickets, search]);

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
        {/* Create form */}
        <View style={styles.form}>
          <Text style={styles.formTitle}>Create Ticket</Text>
          <TextInput
            style={styles.input}
            placeholder="Ticket title..."
            placeholderTextColor="#9ca3af"
            value={title}
            onChangeText={setTitle}
          />
          <View style={styles.priorityRow}>
            {PRIORITIES.map((p) => {
              const active = priority === p;
              const pc = PRIORITY_COLORS[p];
              return (
                <TouchableOpacity
                  key={p}
                  style={[
                    styles.priorityBtn,
                    { backgroundColor: active ? pc.bg : "#f3f4f6" },
                    active && styles.priorityBtnActive,
                  ]}
                  onPress={() => setPriority(p)}
                >
                  <Text
                    style={[
                      styles.priorityBtnText,
                      { color: active ? pc.text : "#6b7280" },
                    ]}
                  >
                    {p}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>
          <TouchableOpacity style={styles.createBtn} onPress={handleCreate}>
            <Text style={styles.createBtnText}>+ Create</Text>
          </TouchableOpacity>
        </View>

        {/* Search */}
        <TextInput
          style={styles.searchInput}
          placeholder="Search tickets..."
          placeholderTextColor="#9ca3af"
          value={search}
          onChangeText={setSearch}
        />

        {/* Ticket list */}
        {filtered.length === 0 ? (
          <View style={styles.empty}>
            <Text style={styles.emptyText}>No tickets found.</Text>
          </View>
        ) : (
          filtered.map((t) => {
            const pc = PRIORITY_COLORS[t.priority] ?? { bg: "#f3f4f6", text: "#374151" };
            return (
              <View key={t.id} style={styles.card}>
                <View style={styles.cardHeader}>
                  <Text style={styles.cardTitle} numberOfLines={2}>{t.title}</Text>
                  <Text style={styles.cardId}>#{t.id.slice(0, 4)}</Text>
                </View>
                <View style={styles.badges}>
                  <View style={[styles.badge, { backgroundColor: pc.bg }]}>
                    <Text style={[styles.badgeText, { color: pc.text }]}>
                      {t.priority}
                    </Text>
                  </View>
                  <View style={styles.statusBadge}>
                    <Text style={styles.statusBadgeText}>
                      {STATUS_LABELS[t.status]}
                    </Text>
                  </View>
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
  form: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 16,
    marginBottom: 14,
    shadowColor: "#000",
    shadowOpacity: 0.06,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
    elevation: 4,
  },
  formTitle: { fontSize: 15, fontWeight: "600", color: "#1f2937", marginBottom: 10 },
  input: {
    borderWidth: 1,
    borderColor: "#e5e7eb",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    color: "#111827",
    marginBottom: 10,
  },
  priorityRow: { flexDirection: "row", gap: 6, marginBottom: 10, flexWrap: "wrap" },
  priorityBtn: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 99,
  },
  priorityBtnActive: {
    borderWidth: 1,
    borderColor: "rgba(0,0,0,0.1)",
  },
  priorityBtnText: { fontSize: 12, fontWeight: "600", textTransform: "capitalize" },
  createBtn: {
    backgroundColor: "#2563eb",
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: "center",
  },
  createBtnText: { color: "#ffffff", fontWeight: "700", fontSize: 14 },
  searchInput: {
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#e5e7eb",
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 14,
    color: "#111827",
    marginBottom: 14,
  },
  empty: {
    backgroundColor: "#ffffff",
    borderRadius: 12,
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
    alignItems: "flex-start",
    marginBottom: 8,
  },
  cardTitle: { flex: 1, fontSize: 14, fontWeight: "600", color: "#111827", marginRight: 8 },
  cardId: { fontSize: 12, color: "#9ca3af" },
  badges: { flexDirection: "row", gap: 6 },
  badge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 99 },
  badgeText: { fontSize: 11, fontWeight: "700", textTransform: "capitalize" },
  statusBadge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 99, backgroundColor: "#f3f4f6" },
  statusBadgeText: { fontSize: 11, fontWeight: "600", color: "#374151" },
});
