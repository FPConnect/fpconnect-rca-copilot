import React from "react";
import { View, Text, StyleSheet, SafeAreaView } from "react-native";
import { Bell } from "lucide-react-native";

interface HeaderProps {
  title: string;
  notificationCount?: number;
}

export default function Header({ title, notificationCount = 0 }: HeaderProps) {
  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.container}>
        <View>
          <Text style={styles.brand}>FPConnect</Text>
          <Text style={styles.subtitle}>Technologies</Text>
        </View>
        <View style={styles.right}>
          <Text style={styles.title}>{title}</Text>
          <View style={styles.bellWrap}>
            <Bell size={20} color="#6b7280" />
            {notificationCount > 0 && (
              <View style={styles.badge}>
                <Text style={styles.badgeText}>
                  {notificationCount > 9 ? "9+" : String(notificationCount)}
                </Text>
              </View>
            )}
          </View>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { backgroundColor: "#ffffff" },
  container: {
    height: 56,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    backgroundColor: "#ffffff",
    borderBottomWidth: 1,
    borderBottomColor: "#e5e7eb",
  },
  brand: { fontSize: 16, fontWeight: "700", color: "#2563eb" },
  subtitle: { fontSize: 10, color: "#9ca3af", marginTop: 1 },
  right: { flexDirection: "row", alignItems: "center", gap: 12 },
  title: { fontSize: 14, fontWeight: "600", color: "#374151" },
  bellWrap: { position: "relative" },
  badge: {
    position: "absolute",
    top: -4,
    right: -4,
    minWidth: 16,
    height: 16,
    backgroundColor: "#ef4444",
    borderRadius: 8,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 2,
  },
  badgeText: { fontSize: 9, color: "#ffffff", fontWeight: "700" },
});
