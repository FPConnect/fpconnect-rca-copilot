import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  SafeAreaView,
  Alert,
} from "react-native";

interface Ticket {
  id: string;
  title: string;
  priority: string;
  status: string;
}

const INITIAL_TICKETS: Ticket[] = [
  { id: "1", title: "MRI Scanner offline - Ward A", priority: "critical", status: "open" },
  { id: "2", title: "ECG Monitor slow response", priority: "high", status: "in_progress" },
];

export default function App() {
  const [tickets, setTickets] = useState<Ticket[]>(INITIAL_TICKETS);
  const [newTitle, setNewTitle] = useState("");
  const [screen, setScreen] = useState<"list" | "create">("list");

  const handleCreate = () => {
    if (!newTitle.trim()) {
      Alert.alert("Error", "Please enter a ticket title");
      return;
    }
    const ticket: Ticket = {
      id: String(Date.now()),
      title: newTitle.trim(),
      priority: "medium",
      status: "open",
    };
    setTickets([ticket, ...tickets]);
    setNewTitle("");
    setScreen("list");
  };

  const priorityColor = (p: string) => {
    const map: Record<string, string> = {
      critical: "#fee2e2",
      high: "#ffedd5",
      medium: "#fef9c3",
      low: "#dcfce7",
    };
    return map[p] || "#f3f4f6";
  };

  if (screen === "create") {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => setScreen("list")}>
            <Text style={styles.backBtn}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>New Ticket</Text>
        </View>
        <View style={styles.form}>
          <Text style={styles.label}>Title</Text>
          <TextInput
            style={styles.input}
            value={newTitle}
            onChangeText={setNewTitle}
            placeholder="Describe the issue..."
          />
          <TouchableOpacity style={styles.btn} onPress={handleCreate}>
            <Text style={styles.btnText}>Create Ticket</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>FPConnect</Text>
        <TouchableOpacity
          style={styles.createBtn}
          onPress={() => setScreen("create")}
        >
          <Text style={styles.createBtnText}>+ New</Text>
        </TouchableOpacity>
      </View>
      <FlatList
        data={tickets}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <View style={[styles.card, { backgroundColor: priorityColor(item.priority) }]}>
            <Text style={styles.cardTitle}>{item.title}</Text>
            <View style={styles.cardMeta}>
              <Text style={styles.badge}>{item.priority}</Text>
              <Text style={styles.badge}>{item.status}</Text>
            </View>
          </View>
        )}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    padding: 16,
    backgroundColor: "#1d4ed8",
  },
  headerTitle: { fontSize: 20, fontWeight: "bold", color: "#fff" },
  backBtn: { color: "#fff", fontSize: 16 },
  createBtn: {
    backgroundColor: "#fff",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  createBtnText: { color: "#1d4ed8", fontWeight: "bold" },
  list: { padding: 12 },
  card: {
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  cardTitle: { fontSize: 15, fontWeight: "600", color: "#1f2937", marginBottom: 6 },
  cardMeta: { flexDirection: "row", gap: 6 },
  badge: {
    fontSize: 11,
    fontWeight: "700",
    backgroundColor: "rgba(0,0,0,0.08)",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 99,
    color: "#374151",
    textTransform: "uppercase",
  },
  form: { padding: 20 },
  label: { fontSize: 14, fontWeight: "600", color: "#374151", marginBottom: 6 },
  input: {
    borderWidth: 1,
    borderColor: "#d1d5db",
    borderRadius: 10,
    padding: 12,
    fontSize: 15,
    backgroundColor: "#fff",
    marginBottom: 16,
  },
  btn: {
    backgroundColor: "#1d4ed8",
    borderRadius: 10,
    padding: 14,
    alignItems: "center",
  },
  btnText: { color: "#fff", fontWeight: "bold", fontSize: 16 },
});
