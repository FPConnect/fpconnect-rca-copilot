import React, { useState } from "react";
import { ActivityIndicator, Button, ScrollView, Text, TextInput, View } from "react-native";
import { Machine } from "../src/services/api";
import { isMachine } from "../src/services/lists";
import { useApiList } from "../src/services/useApiList";

export default function MachinesScreen() {
  const { data, error, loading, reload } = useApiList<Machine>("/machines/", isMachine);
  const [search, setSearch] = useState("");
  return <ScrollView contentContainerStyle={{ padding: 20, gap: 14 }}>
    <Text>Equipment is scoped by the selected organization on the tenant-foundation backend. Do not use customer data until isolation is independently verified. Statuses are stored records, not verified live telemetry.</Text>
    <Button title="Refresh machines" disabled={loading} onPress={() => void reload()} />
    {loading ? <ActivityIndicator /> : null}
    {error ? <Text accessibilityRole="alert">{error}</Text> : null}
    <TextInput accessibilityLabel="Search machines" placeholder="Search machines" value={search} onChangeText={setSearch} style={{ borderWidth: 1, padding: 12 }} />
    {!loading && data?.length === 0 ? <Text>No machines returned.</Text> : null}
    {data?.filter(machine => [machine.name, machine.code, machine.location].some(value => value.toLowerCase().includes(search.toLowerCase()))).map(machine => <View key={machine.id} style={{ padding: 12, backgroundColor: "#fff", borderRadius: 8 }}>
      <Text style={{ fontWeight: "700" }}>{machine.name} ({machine.code})</Text>
      <Text>{machine.location} · {machine.type}</Text>
      <Text>Recorded status: {machine.status} · Last check: {machine.last_check}</Text>
    </View>)}
  </ScrollView>;
}
