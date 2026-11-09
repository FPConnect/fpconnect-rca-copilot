import React from "react";
import { Button, ScrollView, Text } from "react-native";
import { useSession } from "../src/services/SessionProvider";

export default function SettingsScreen() {
  const { user, organization, switchOrganization, signOut } = useSession();
  return <ScrollView contentContainerStyle={{ padding: 20, gap: 16 }}>
    <Text style={{ fontSize: 22, fontWeight: "700" }}>Account</Text>
    <Text>{user.full_name || user.email}</Text>
    <Text>Organization: {organization.name}</Text>
    <Button title="Switch organization" onPress={switchOrganization} />
    <Text>Profile editing, theme, notifications and export are not available in this app.</Text>
    <Text>Signing out removes the locally stored tokens; the backend tokens are not revoked.</Text>
    <Button title="Sign out" onPress={() => void signOut()} />
  </ScrollView>;
}
