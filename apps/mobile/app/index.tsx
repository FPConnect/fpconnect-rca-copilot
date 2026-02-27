import React from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import Header from "../src/components/Header";
import Card from "../src/components/Card";

const METRICS = [
  { label: "Open Tickets", value: 12, bg: "#fef9c3", color: "#854d0e" },
  { label: "In Progress", value: 5, bg: "#dbeafe", color: "#1e40af" },
  { label: "Resolved Today", value: 8, bg: "#dcfce7", color: "#166534" },
  { label: "Critical", value: 2, bg: "#fee2e2", color: "#991b1b" },
];

const RECENT_ACTIVITY = [
  { id: "1", text: "MRI Scanner back online — Ward A", time: "2 min ago" },
  { id: "2", text: "Ticket #42 escalated to critical", time: "15 min ago" },
  { id: "3", text: "Health check passed — 6 machines", time: "1 hour ago" },
  { id: "4", text: "ECG Monitor alert acknowledged", time: "2 hours ago" },
];

export default function DashboardScreen() {
  return (
    <View style={styles.container}>
      <Header title="Dashboard" />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.heading}>Dashboard</Text>

        {/* Metric cards — 2 per row */}
        <View style={styles.grid}>
          {METRICS.map((m) => (
            <Card
              key={m.label}
              label={m.label}
              value={m.value}
              backgroundColor={m.bg}
              textColor={m.color}
            />
          ))}
        </View>

        {/* Recent Activity */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Activity</Text>
          {RECENT_ACTIVITY.map((item) => (
            <View key={item.id} style={styles.activityRow}>
              <View style={styles.dot} />
              <View style={styles.activityText}>
                <Text style={styles.activityMsg}>{item.text}</Text>
                <Text style={styles.activityTime}>{item.time}</Text>
              </View>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 32 },
  heading: {
    fontSize: 24,
    fontWeight: "700",
    color: "#111827",
    marginBottom: 16,
  },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    marginHorizontal: -4,
    marginBottom: 20,
  },
  section: {
    backgroundColor: "#ffffff",
    borderRadius: 12,
    padding: 16,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#1f2937",
    marginBottom: 12,
  },
  activityRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: "#f3f4f6",
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: "#3b82f6",
    marginTop: 5,
    marginRight: 10,
  },
  activityText: { flex: 1 },
  activityMsg: { fontSize: 13, color: "#374151", fontWeight: "500" },
  activityTime: { fontSize: 11, color: "#9ca3af", marginTop: 2 },
});
