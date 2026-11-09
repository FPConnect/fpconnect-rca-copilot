import React from "react";
import { ActivityIndicator, Button, ScrollView, Text } from "react-native";
import { Ticket } from "../src/services/api";
import { isTicket } from "../src/services/lists";
import { useApiList } from "../src/services/useApiList";

export default function DashboardScreen() {
  const { data, error, loading, reload } = useApiList<Ticket>("/tickets/?limit=100", isTicket);
  return <ScrollView contentContainerStyle={{ padding: 20, gap: 16 }}>
    <Text style={{ fontSize: 24, fontWeight: "700" }}>Dashboard</Text>
    <Text>Tenant isolation is under development. Do not use customer or patient data. Ticket metrics are unavailable while the backend blocks ticket access.</Text>
    <Text>Counts below cover only the first 100 tickets visible to this account, not the complete fleet.</Text>
    <Button title="Refresh" disabled={loading} onPress={() => void reload()} />
    {loading ? <ActivityIndicator /> : null}
    {error ? <Text accessibilityRole="alert">{error}</Text> : null}
    {data ? <>
      <Text>Tickets returned: {data.length}</Text>
      <Text>Open: {data.filter(t => t.status === "open").length}</Text>
      <Text>In progress: {data.filter(t => t.status === "in_progress").length}</Text>
    </> : null}
  </ScrollView>;
}
