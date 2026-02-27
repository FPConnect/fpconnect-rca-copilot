import React from "react";
import { View, Text, StyleSheet } from "react-native";

interface CardProps {
  label: string;
  value: string | number;
  backgroundColor?: string;
  textColor?: string;
}

export default function Card({
  label,
  value,
  backgroundColor = "#f3f4f6",
  textColor = "#1f2937",
}: CardProps) {
  return (
    <View style={[styles.card, { backgroundColor }]}>
      <Text style={[styles.value, { color: textColor }]}>{value}</Text>
      <Text style={[styles.label, { color: textColor }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    borderRadius: 12,
    padding: 16,
    margin: 4,
    shadowColor: "#000",
    shadowOpacity: 0.06,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
    elevation: 2,
    minWidth: 130,
  },
  value: {
    fontSize: 32,
    fontWeight: "700",
    marginBottom: 4,
  },
  label: {
    fontSize: 12,
    fontWeight: "500",
  },
});
