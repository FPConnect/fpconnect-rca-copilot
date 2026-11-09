import React, { useEffect, useState } from "react";
import { ActivityIndicator, Alert, Button, ScrollView, Text, TextInput, View } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { ApiError, Ticket } from "../src/services/api";
import { isTicket } from "../src/services/lists";
import { useSession } from "../src/services/SessionProvider";
import { acknowledgeUnconfirmedTicket, createTicket, hasUnconfirmedTicket } from "../src/services/ticketCreate";
import { useApiList } from "../src/services/useApiList";

export default function TicketsScreen() {
  const { client, expire } = useSession();
  const { data, error, loading, reload } = useApiList<Ticket>("/tickets/?limit=100", isTicket);
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState<"low" | "medium" | "high" | "critical">("medium");
  const [search, setSearch] = useState("");
  const [busy, setBusy] = useState(false);
  const [unconfirmed, setUnconfirmed] = useState(true);
  const [submitError, setSubmitError] = useState("");

  useEffect(() => {
    hasUnconfirmedTicket(AsyncStorage).then(setUnconfirmed).catch(() => setSubmitError("Cannot read submission guard; creation is disabled."));
  }, []);

  const submit = async () => {
    if (busy || unconfirmed || !title.trim()) return;
    setBusy(true);
    setSubmitError("");
    try {
      const created = await createTicket(AsyncStorage, client, title.trim(), priority);
      setTitle("");
      setPriority("medium");
      await reload();
      Alert.alert("Ticket created", `Ticket #${created.id} was returned by the API. Review and acknowledge the submission before creating another.`);
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) await expire();
      else setSubmitError(e instanceof ApiError ? `${e.kind}: ${e.message}` : "Submission failed. Check the submission warning before retrying.");
    } finally {
      try { setUnconfirmed(await hasUnconfirmedTicket(AsyncStorage)); }
      catch { setUnconfirmed(true); setSubmitError("Cannot read submission guard; creation is disabled."); }
      setBusy(false);
    }
  };
  const reconcile = () => Alert.alert(
    "Verify the previous submission",
    "Check the server ticket list or ask an administrator before continuing. The previous request may have created a ticket. Continue only after verifying.",
    [{ text: "Cancel", style: "cancel" }, { text: "I verified", onPress: () => {
      void acknowledgeUnconfirmedTicket(AsyncStorage).then(() => setUnconfirmed(false)).catch(() => setSubmitError("Could not clear the guard."));
    } }],
  );
  return (
    <ScrollView contentContainerStyle={{ padding: 20, gap: 14 }}>
      <Text>Ticket access is disabled on the tenant-foundation backend until isolation is complete. Older offline drafts are not displayed, synchronized or deleted.</Text>
      <Button title="Refresh tickets" onPress={() => void reload()} disabled={loading} />
      {loading ? <ActivityIndicator /> : null}
      {error ? <Text accessibilityRole="alert">{error}</Text> : null}
      <TextInput accessibilityLabel="Search tickets" placeholder="Search tickets" value={search} onChangeText={setSearch} style={{ borderWidth: 1, padding: 12 }} />
      {!loading && data?.length === 0 ? <Text>No tickets returned.</Text> : null}
      {data?.filter(ticket => ticket.title.toLowerCase().includes(search.toLowerCase())).map(ticket => <View key={ticket.id} style={{ padding: 12, backgroundColor: "#fff", borderRadius: 8 }}>
        <Text style={{ fontWeight: "700" }}>#{ticket.id} {ticket.title}</Text>
        <Text>{ticket.status} · {ticket.priority}</Text>
      </View>)}
      <Text style={{ fontWeight: "700", fontSize: 18 }}>Create ticket</Text>
      <Text>Creation is disabled until the backend ticket tenant boundary is implemented and reviewed. Do not enter customer or patient data.</Text>
      {unconfirmed ? <View><Text accessibilityRole="alert">A previous submission needs review. Its outcome may be unknown. Do not retry until it is reconciled.</Text><Button title="Review submission" onPress={reconcile} /></View> : null}
      <TextInput accessibilityLabel="Ticket title" placeholder="Ticket title" value={title} onChangeText={setTitle} style={{ borderWidth: 1, padding: 12 }} />
      <Text>Priority: {priority}</Text>
      {(["low", "medium", "high", "critical"] as const).map(value =>
        <Button key={value} title={`${value === priority ? "Selected: " : ""}${value}`} onPress={() => setPriority(value)} disabled={busy} />,
      )}
      {submitError ? <Text accessibilityRole="alert">{submitError}</Text> : null}
      <Button title={busy ? "Submitting..." : "Create ticket (unavailable)"} disabled onPress={() => void submit()} />
    </ScrollView>
  );
}
