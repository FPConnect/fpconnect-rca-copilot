import React from "react";
import { View, Text, StyleSheet } from "react-native";

interface CardProps {
  label: string;
  value: string | number;
  backgroundColor?: string;
  textColor?: string;
  icon?: React.ReactNode;
}

export default function Card({
  label,
  value,
  backgroundColor = "#f3f4f6",
  textColor = "#1f2937",
  icon,
}: CardProps) {
  return (
    <View style={[styles.card, { backgroundColor }]}>
      {icon && <View style={styles.iconWrap}>{icon}</View>}
      <Text style={[styles.value, { color: textColor }]}>{value}</Text>
      <Text style={[styles.label, { color: textColor }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    borderRadius: 16,
    padding: 16,
    margin: 4,
    shadowColor: "#000",
    shadowOpacity: 0.08,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 4 },
    elevation: 4,
    minWidth: 140,
  },
  iconWrap: { marginBottom: 8 },
  value: {
    fontSize: 36,
    fontWeight: "800",
    marginBottom: 4,
  },
  label: {
    fontSize: 12,
    fontWeight: "600",
  },
});
