import React, { createContext, useContext, useEffect, useRef, useState } from "react";
import { ActivityIndicator, Button, Platform, ScrollView, Text, TextInput, View } from "react-native";
import * as SecureStore from "expo-secure-store";
import { User } from "./api";
import { restoreSession, signInAndStore, SessionRemovalError, SessionClient, RequestClient, Organization, discoverOrganizations, selectOrganization, requireNativeSessionStorage, restoreErrorMessage } from "./session";
import { ApiError } from "./api";
import { createSessionStore, openSessionStore } from "./secureSessionStorage";

const secureStorage = {
  getItem: SecureStore.getItemAsync,
  setItem: SecureStore.setItemAsync,
  removeItem: SecureStore.deleteItemAsync,
};
type Session = { client: RequestClient; user: User; organization: Organization; switchOrganization: () => void; signOut: () => Promise<void>; expire: () => Promise<void> };
const Context = createContext<Session | null>(null);

export function useSession(): Session {
  const session = useContext(Context);
  if (!session) throw new Error("No session");
  return session;
}

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<{ client: SessionClient; user: User } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [clearFailed, setClearFailed] = useState(false);
  const currentClient = useRef<SessionClient | null>(null);
  const [selected, setSelected] = useState<{ org: Organization; client: RequestClient } | null>(null);
  const [organizations, setOrganizations] = useState<Organization[] | null>(null);
  const [orgBusy, setOrgBusy] = useState(false);
  const [orgError, setOrgError] = useState("");

  const signOut = async (expectedClient?: SessionClient) => {
    if (expectedClient && currentClient.current !== expectedClient) return;
    const client = currentClient.current;
    currentClient.current = null;
    setSelected(null);
    setOrganizations(null);
    setOrgBusy(false);
    setOrgError("");
    setClearing(true);
    setSession(null);
    setPassword("");
    try {
      if (client) await client.close();
      else {
        const store = await openSessionStore(secureStorage);
        if (store) await store.removeItem();
      }
      setClearFailed(false);
      setError("");
    } catch {
      setClearFailed(true);
      setError("Could not remove the saved session. Retry before sharing this device; clearing app data would erase legacy drafts.");
    } finally { setClearing(false); }
  };

  useEffect(() => {
    const restore = async () => {
      try {
        requireNativeSessionStorage(Platform.OS);
        const store = await openSessionStore(secureStorage);
        const restored = store ? await restoreSession(store) : null;
        currentClient.current = restored?.client ?? null;
        setSession(restored);
      } catch (e) {
        if (e instanceof SessionRemovalError) setClearFailed(true);
        setError(restoreErrorMessage(e));
      } finally { setLoading(false); }
    };
    void restore();
  }, []);

  const loadOrganizations = async (client: SessionClient) => {
    setOrgBusy(true);
    setOrgError("");
    try {
      const found = await discoverOrganizations(client);
      if (currentClient.current === client) setOrganizations(found);
    } catch (e) {
      if (currentClient.current !== client) return;
      if (e instanceof ApiError && e.status === 401) await signOut(client);
      else setOrgError(e instanceof ApiError ? e.message : "Could not load organizations.");
    } finally { if (currentClient.current === client) setOrgBusy(false); }
  };

  useEffect(() => {
    if (session && !selected) void loadOrganizations(session.client);
  }, [session, selected]);

  const chooseOrganization = async (org: Organization) => {
    if (!session || orgBusy) return;
    const client = session.client;
    setOrgBusy(true);
    setOrgError("");
    try {
      const scoped = await selectOrganization(client, org.id);
      if (currentClient.current === client) setSelected({ org, client: scoped });
    } catch (e) {
      if (currentClient.current !== client) return;
      if (e instanceof ApiError && e.status === 401) await signOut(client);
      else if (e instanceof ApiError && e.status === 403) setOrgError("Organization access is no longer available. Refresh the list.");
      else setOrgError(e instanceof ApiError ? e.message : "Could not select organization.");
    } finally { if (currentClient.current === client) setOrgBusy(false); }
  };

  const signIn = async () => {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      requireNativeSessionStorage(Platform.OS);
      const store = await createSessionStore(secureStorage);
      const next = await signInAndStore(store, email.trim(), password);
      setPassword("");
      currentClient.current = next.client;
      setSession(next);
    } catch (e) { setError(e instanceof ApiError ? e.message : "Sign-in failed."); }
    finally { setBusy(false); }
  };

  if (loading) return <ActivityIndicator style={{ flex: 1 }} />;
  if (!session) return (
    <View style={{ flex: 1, justifyContent: "center", padding: 24, gap: 12 }}>
      <Text style={{ fontSize: 24, fontWeight: "700" }}>OPSPECTA sign in</Text>
      <Text>Sign in with your OPSPECTA account. Tenant isolation is under development; do not use customer or patient data.</Text>
      <TextInput accessibilityLabel="Email" placeholder="Email" autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={setEmail} style={{ borderWidth: 1, padding: 12 }} />
      <TextInput accessibilityLabel="Password" placeholder="Password" secureTextEntry value={password} onChangeText={setPassword} style={{ borderWidth: 1, padding: 12 }} />
      {error ? <Text accessibilityRole="alert">{error}</Text> : null}
      {clearFailed ? <Button title="Retry removing saved session" disabled={clearing} onPress={() => void signOut()} /> : null}
      <Button title={busy ? "Signing in..." : "Sign in"} disabled={busy || clearing || clearFailed || Platform.OS === "web"} onPress={() => void signIn()} />
    </View>
  );
  if (!selected) return <ScrollView contentContainerStyle={{ padding: 24, gap: 12 }}>
    <Text style={{ fontSize: 24, fontWeight: "700" }}>Select organization</Text>
    <Text>Access is checked by the server. Customer operations remain restricted until tenant isolation is complete.</Text>
    {orgBusy ? <ActivityIndicator /> : null}
    {orgError ? <Text accessibilityRole="alert">{orgError}</Text> : null}
    {organizations?.length === 0 ? <Text>No active organizations are available for this account.</Text> : null}
    {organizations?.map(org => <Button key={org.id} title={org.name} disabled={orgBusy} onPress={() => void chooseOrganization(org)} />)}
    <Button title="Refresh organizations" disabled={orgBusy} onPress={() => void loadOrganizations(session.client)} />
    <Button title="Sign out" disabled={clearing} onPress={() => void signOut()} />
  </ScrollView>;
  return <Context.Provider key={`${selected.org.id}`} value={{
    client: selected.client, user: session.user, organization: selected.org,
    switchOrganization: () => { setOrganizations(null); setSelected(null); },
    signOut: () => signOut(), expire: () => signOut(session.client),
  }}>{children}</Context.Provider>;
}
