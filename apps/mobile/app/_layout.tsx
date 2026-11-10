import { Tabs } from "expo-router";
import Ionicons from "@expo/vector-icons/Ionicons";
import { SessionProvider } from "../src/services/SessionProvider";

export default function RootLayout() {
  return (
    <SessionProvider><Tabs
      screenOptions={{
        headerShown: true,
        headerStyle: { backgroundColor: "#2563eb" },
        headerTintColor: "#ffffff",
        headerTitleStyle: { fontWeight: "700", fontSize: 17 },
        tabBarStyle: {
          backgroundColor: "#ffffff",
          borderTopColor: "#e5e7eb",
          height: 60,
          paddingBottom: 8,
        },
        tabBarActiveTintColor: "#2563eb",
        tabBarInactiveTintColor: "#64748b",
        tabBarLabelStyle: { fontSize: 11, fontWeight: "600" },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Dashboard",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="grid-outline" color={color} size={size} />
          ),
        }}
      />
      <Tabs.Screen
        name="machines"
        options={{
          title: "Machines",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="hardware-chip-outline" color={color} size={size} />
          ),
        }}
      />
      <Tabs.Screen
        name="tickets"
        options={{
          title: "Tickets",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="ticket-outline" color={color} size={size} />
          ),
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: "Settings",
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="settings-outline" color={color} size={size} />
          ),
        }}
      />
    </Tabs></SessionProvider>
  );
}
