import React, { useEffect, useMemo, useState } from "react";
import {
  View,
  Text,
  ScrollView,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Modal,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  ActivityIndicator,
} from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import {
  createOfflineTicket,
  getPendingTicketCount,
  loadOfflineTickets,
  OfflineTicket,
  syncPendingTickets,
  TicketPriority,
} from "../src/services/offlineTickets";

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
  closed: "Closed",
};

const SYNC_LABELS: Record<string, { label: string; color: string; bg: string }> = {
  synced: { label: "Synced", color: "#166534", bg: "#dcfce7" },
  pending: { label: "Pending sync", color: "#854d0e", bg: "#fef9c3" },
  syncing: { label: "Syncing", color: "#1d4ed8", bg: "#dbeafe" },
  failed: { label: "Offline", color: "#991b1b", bg: "#fee2e2" },
};

export default function TicketsScreen() {
  const [tickets, setTickets] = useState<OfflineTicket[]>([]);
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState<TicketPriority>("medium");
  const [search, setSearch] = useState("");
  const [modalVisible, setModalVisible] = useState(false);
  const [pendingCount, setPendingCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);

  const PRIORITIES: TicketPriority[] = ["low", "medium", "high", "critical"];

  const refreshPendingCount = async () => {
    setPendingCount(await getPendingTicketCount());
  };

  const runSync = async (showResult = false) => {
    if (isSyncing) return;
    setIsSyncing(true);
    const result = await syncPendingTickets();
    setTickets(result.tickets);
    await refreshPendingCount();
    setIsSyncing(false);

    if (showResult) {
      if (result.failed > 0) {
        Alert.alert(
          "Offline sync",
          `${result.failed} ticket(s) remain queued and will sync when the API is reachable.`,
        );
      } else {
        Alert.alert("Offline sync", `${result.synced} ticket(s) synced successfully.`);
      }
    }
  };

  useEffect(() => {
    const bootstrap = async () => {
      const storedTickets = await loadOfflineTickets();
      setTickets(storedTickets);
      await refreshPendingCount();
      setIsLoading(false);
      await runSync();
    };

    void bootstrap();
  }, []);

  const handleCreate = async () => {
    if (!title.trim()) {
      Alert.alert("Error", "Please enter a ticket title.");
      return;
    }

    const newTicket = await createOfflineTicket({
      title: title.trim(),
      priority,
    });

    setTickets((current) => [newTicket, ...current]);
    await refreshPendingCount();
    setTitle("");
    setPriority("medium");
    setModalVisible(false);
    void runSync();
  };

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    if (!q) return tickets;
    return tickets.filter((t) => t.title.toLowerCase().includes(q));
  }, [tickets, search]);

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.syncBanner}>
        <View style={styles.syncTextWrap}>
          <Ionicons name="cloud-upload-outline" size={18} color="#2563eb" />
          <Text style={styles.syncText}>
            {pendingCount > 0
              ? `${pendingCount} ticket(s) waiting for sync`
              : "Offline queue is clear"}
          </Text>
        </View>
        <TouchableOpacity
          style={[styles.syncButton, isSyncing && styles.syncButtonDisabled]}
          onPress={() => runSync(true)}
          disabled={isSyncing}
          accessibilityLabel="Sync queued tickets"
          accessibilityRole="button"
        >
          {isSyncing ? (
            <ActivityIndicator size="small" color="#ffffff" />
          ) : (
            <Text style={styles.syncButtonText}>Sync</Text>
          )}
        </TouchableOpacity>
      </View>

      <View style={styles.searchWrap}>
        <Ionicons name="search-outline" size={16} color="#9ca3af" style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search tickets..."
          placeholderTextColor="#9ca3af"
          value={search}
          onChangeText={setSearch}
        />
      </View>

      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {isLoading ? (
          <View style={styles.empty}>
            <ActivityIndicator color="#2563eb" />
            <Text style={styles.emptyText}>Loading local tickets...</Text>
          </View>
        ) : filtered.length === 0 ? (
          <View style={styles.empty}>
            <Ionicons name="ticket-outline" size={40} color="#d1d5db" />
            <Text style={styles.emptyText}>No tickets found.</Text>
          </View>
        ) : (
          filtered.map((t) => {
            const pc = PRIORITY_COLORS[t.priority] ?? { bg: "#f3f4f6", text: "#374151" };
            const sync = SYNC_LABELS[t.syncStatus];
            return (
              <View key={t.id} style={styles.card}>
                <View style={styles.cardHeader}>
                  <Text style={styles.cardTitle} numberOfLines={2}>{t.title}</Text>
                  <Text style={styles.cardId}>#{t.serverId ?? t.id.slice(-4)}</Text>
                </View>
                <View style={styles.badges}>
                  <View style={[styles.badge, { backgroundColor: pc.bg }]}>
                    <Text style={[styles.badgeText, { color: pc.text }]}>{t.priority}</Text>
                  </View>
                  <View style={styles.statusBadge}>
                    <Text style={styles.statusBadgeText}>{STATUS_LABELS[t.status]}</Text>
                  </View>
                  <View style={[styles.statusBadge, { backgroundColor: sync.bg }]}>
                    <Text style={[styles.statusBadgeText, { color: sync.color }]}>{sync.label}</Text>
                  </View>
                </View>
              </View>
            );
          })
        )}
      </ScrollView>

      <TouchableOpacity
        style={styles.fab}
        onPress={() => setModalVisible(true)}
        accessibilityLabel="Create new ticket"
        accessibilityRole="button"
      >
        <Ionicons name="add" size={28} color="#ffffff" />
      </TouchableOpacity>

      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent
        onRequestClose={() => setModalVisible(false)}
      >
        <KeyboardAvoidingView
          style={styles.modalOverlay}
          behavior={Platform.OS === "ios" ? "padding" : "height"}
        >
          <View style={styles.modalSheet}>
            <View style={styles.modalHandle} />
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>New Ticket</Text>
              <TouchableOpacity
                onPress={() => setModalVisible(false)}
                accessibilityLabel="Close modal"
                accessibilityRole="button"
              >
                <Ionicons name="close" size={22} color="#6b7280" />
              </TouchableOpacity>
            </View>

            <Text style={styles.fieldLabel}>Title</Text>
            <TextInput
              style={styles.input}
              placeholder="Describe the issue..."
              placeholderTextColor="#9ca3af"
              value={title}
              onChangeText={setTitle}
              multiline
              numberOfLines={2}
              accessibilityLabel="Ticket title"
            />

            <Text style={styles.fieldLabel}>Priority</Text>
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
              <Text style={styles.createBtnText}>Create Ticket</Text>
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#f8fafc" },
  syncBanner: {
    alignItems: "center",
    backgroundColor: "#ffffff",
    borderColor: "#dbeafe",
    borderRadius: 12,
    borderWidth: 1,
    flexDirection: "row",
    justifyContent: "space-between",
    marginHorizontal: 16,
    marginTop: 12,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  syncTextWrap: { alignItems: "center", flex: 1, flexDirection: "row", gap: 8 },
  syncText: { color: "#334155", fontSize: 13, fontWeight: "600" },
  syncButton: {
    alignItems: "center",
    backgroundColor: "#2563eb",
    borderRadius: 8,
    minWidth: 64,
    paddingHorizontal: 12,
    paddingVertical: 7,
  },
  syncButtonDisabled: { opacity: 0.7 },
  syncButtonText: { color: "#ffffff", fontSize: 12, fontWeight: "700" },
  searchWrap: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#ffffff",
    borderWidth: 1,
    borderColor: "#e5e7eb",
    borderRadius: 12,
    marginHorizontal: 16,
    marginTop: 12,
    marginBottom: 4,
    paddingHorizontal: 12,
  },
  searchIcon: { marginRight: 8 },
  searchInput: {
    flex: 1,
    paddingVertical: 10,
    fontSize: 14,
    color: "#111827",
  },
  content: { paddingHorizontal: 16, paddingTop: 12, paddingBottom: 100 },
  empty: {
    backgroundColor: "#ffffff",
    borderRadius: 16,
    padding: 48,
    alignItems: "center",
    gap: 12,
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
  badges: { flexDirection: "row", flexWrap: "wrap", gap: 6 },
  badge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 99 },
  badgeText: { fontSize: 11, fontWeight: "700", textTransform: "capitalize" },
  statusBadge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 99, backgroundColor: "#f3f4f6" },
  statusBadgeText: { fontSize: 11, fontWeight: "600", color: "#374151" },
  fab: {
    position: "absolute",
    bottom: 24,
    right: 24,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: "#2563eb",
    alignItems: "center",
    justifyContent: "center",
    shadowColor: "#2563eb",
    shadowOpacity: 0.4,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 6 },
    elevation: 8,
  },
  modalOverlay: {
    flex: 1,
    justifyContent: "flex-end",
    backgroundColor: "rgba(0,0,0,0.4)",
  },
  modalSheet: {
    backgroundColor: "#ffffff",
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    paddingBottom: 40,
  },
  modalHandle: {
    width: 40,
    height: 4,
    backgroundColor: "#e5e7eb",
    borderRadius: 2,
    alignSelf: "center",
    marginBottom: 16,
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 20,
  },
  modalTitle: { fontSize: 18, fontWeight: "700", color: "#111827" },
  fieldLabel: { fontSize: 13, fontWeight: "600", color: "#374151", marginBottom: 6 },
  input: {
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 14,
    color: "#111827",
    marginBottom: 16,
    textAlignVertical: "top",
  },
  priorityRow: { flexDirection: "row", gap: 8, marginBottom: 20, flexWrap: "wrap" },
  priorityBtn: {
    paddingHorizontal: 14,
    paddingVertical: 6,
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
    paddingVertical: 14,
    alignItems: "center",
  },
  createBtnText: { color: "#ffffff", fontWeight: "700", fontSize: 15 },
});
