import React, { useState, useEffect } from "react";
import { View, Text, ScrollView, Button, StyleSheet, Alert, Appearance } from "react-native";
import { BarChart, LineChart, PieChart } from "react-native-chart-kit";
import { Dimensions } from "react-native";

const METRICS = [
  { label: "Uptime Médio", value: "99.2%", change: "+0.1%", positive: true },
  { label: "MTBF (horas)", value: "1,240", change: "+5%", positive: true },
  { label: "MTTR (minutos)", value: "18", change: "-12%", positive: true },
  { label: "Alertas (7d)", value: "34", change: "+8%", positive: false },
];

const PERFORMANCE = [
  { machine: "MRI Scanner", uptime: 99.8, incidents: 0 },
  { machine: "ECG Monitor", uptime: 94.5, incidents: 3 },
  { machine: "Ventilator", uptime: 99.9, incidents: 0 },
  { machine: "Defibrillator", uptime: 78.2, incidents: 5 },
  { machine: "Patient Monitor", uptime: 98.7, incidents: 1 },
];

const RELATORIO_ROI = {
  economiaTotal: "R$ 142.300,00",
  downtimeEvitado: "48h",
  alertasCriticos: 12,
  roi: "137%",
};

const DESASTRES_EVITADOS = [
  {
    equipamento: "MRI Scanner - Tomógrafo A",
    economia: "R$ 85.000,00",
  },
  {
    equipamento: "Geladeira UTI",
    economia: "R$ 35.000,00",
  },
  {
    equipamento: "Central de Gases",
    economia: "R$ 22.300,00",
  },
];

export default function DemoRecursos() {
  const [darkMode, setDarkMode] = useState(Appearance.getColorScheme() === "dark");
  const [notification, setNotification] = useState("");

  useEffect(() => {
    const lowUptime = PERFORMANCE.find((p) => p.uptime < 90);
    if (lowUptime && notification === "") {
      setTimeout(() => {
        setNotification(`Alerta: Uptime baixo em ${lowUptime.machine}`);
        Alert.alert("Alerta", `Uptime baixo em ${lowUptime.machine}: ${lowUptime.uptime}%`);
      }, 2000);
    }
  }, [notification]);

  const barData = {
    labels: PERFORMANCE.map((p) => p.machine),
    datasets: [{ data: PERFORMANCE.map((p) => p.uptime) }],
  };
  const lineData = {
    labels: PERFORMANCE.map((p) => p.machine),
    datasets: [{ data: PERFORMANCE.map((p) => p.incidents) }],
  };
  const pieData = [
    { name: "Sem Incidente", population: PERFORMANCE.filter((p) => p.incidents === 0).length, color: "#22c55e", legendFontColor: "#7F7F7F", legendFontSize: 12 },
    { name: "Com Incidente", population: PERFORMANCE.filter((p) => p.incidents > 0).length, color: "#ef4444", legendFontColor: "#7F7F7F", legendFontSize: 12 },
  ];

  return (
    <ScrollView style={[styles.container, darkMode && styles.darkBg]}>
      <View style={styles.header}>
        <Text style={[styles.title, darkMode && styles.darkText]}>Demonstração de Recursos</Text>
        <Button title={darkMode ? "Modo Claro" : "Modo Escuro"} onPress={() => setDarkMode((d) => !d)} />
      </View>
      <View style={styles.metricsRow}>
        {METRICS.map((m) => (
          <View key={m.label} style={[styles.metricBox, darkMode && styles.darkMetricBox]}>
            <Text style={[styles.metricLabel, darkMode && styles.darkText]}>{m.label}</Text>
            <Text style={[styles.metricValue, darkMode && styles.darkText]}>{m.value}</Text>
            <Text style={[styles.metricChange, m.positive ? styles.positive : styles.negative]}>{m.change}</Text>
          </View>
        ))}
      </View>
      <Text style={[styles.sectionTitle, darkMode && styles.darkText]}>Gráficos</Text>
      <BarChart
        data={barData}
        width={Dimensions.get("window").width - 32}
        height={220}
        chartConfig={chartConfig(darkMode)}
        style={styles.chart}
      />
      <LineChart
        data={lineData}
        width={Dimensions.get("window").width - 32}
        height={220}
        chartConfig={chartConfig(darkMode)}
        style={styles.chart}
      />
      <PieChart
        data={pieData}
        width={Dimensions.get("window").width - 32}
        height={180}
        chartConfig={chartConfig(darkMode)}
        accessor="population"
        backgroundColor={"transparent"}
        paddingLeft={"15"}
        absolute
      />
      <View style={styles.roiContainer}>
        <Text style={[styles.roiTitle, darkMode && styles.darkText]}>Extrato de Economia (YTD)</Text>
        <Text style={styles.roiHighlight}>{RELATORIO_ROI.economiaTotal}</Text>
        <Text style={[styles.roiSub, darkMode && styles.darkText]}>Downtime Evitado: {RELATORIO_ROI.downtimeEvitado} | ROI: {RELATORIO_ROI.roi}</Text>
      </View>

      <Text style={[styles.sectionTitle, darkMode && styles.darkText]}>Desastres Evitados (Top 3)</Text>
      {DESASTRES_EVITADOS.map((d, i) => (
        <View key={i} style={[styles.machineBox, darkMode && styles.darkMachineBox, { borderLeftWidth: 4, borderLeftColor: "#22c55e" }]}>
          <Text style={[styles.machineText, { fontWeight: "bold" }, darkMode && styles.darkText]}>{d.equipamento}</Text>
          <Text style={[styles.machineText, { color: "#22c55e", fontWeight: "bold" }]}>Economia: {d.economia}</Text>
        </View>
      ))}

      <View style={styles.upsellBox}>
        <Text style={styles.upsellTitle}>Maximize sua Proteção</Text>
        <Text style={styles.upsellText}>Expandir o preditivo para a UTI pode gerar mais R$ 200.000/ano em economia.</Text>
        <Button title="Simular Contrato Preditivo" color="#4f46e5" onPress={() => Alert.alert("Upsell", "Redirecionando para consultor...")} />
      </View>
      {notification ? (
        <View style={styles.alertBox}><Text style={styles.alertText}>{notification}</Text></View>
      ) : null}
      <View style={styles.helpBox}>
        <Text style={styles.helpTitle}>Ajuda & Onboarding</Text>
        <Text style={styles.helpText}>- Gráficos interativos
- Notificações e alertas
- Histórico detalhado
- Prioridade automática
- IoT simulado
- Feedback técnico
- Modo escuro
- Acessibilidade</Text>
      </View>
    </ScrollView>
  );
}

function chartConfig(dark: boolean) {
  return {
    backgroundGradientFrom: dark ? "#222" : "#fff",
    backgroundGradientTo: dark ? "#222" : "#fff",
    color: (opacity = 1) => dark ? `rgba(255,255,255,${opacity})` : `rgba(0,0,0,${opacity})`,
    labelColor: (opacity = 1) => dark ? `rgba(255,255,255,${opacity})` : `rgba(0,0,0,${opacity})`,
    strokeWidth: 2,
    barPercentage: 0.7,
    useShadowColorFromDataset: false,
  };
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, backgroundColor: "#fff" },
  darkBg: { backgroundColor: "#222" },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 12 },
  title: { fontSize: 22, fontWeight: "bold" },
  darkText: { color: "#fff" },
  metricsRow: { flexDirection: "row", flexWrap: "wrap", marginBottom: 12 },
  metricBox: { backgroundColor: "#f3f4f6", borderRadius: 8, padding: 10, margin: 4, width: "45%" },
  darkMetricBox: { backgroundColor: "#333" },
  metricLabel: { fontSize: 12 },
  metricValue: { fontSize: 20, fontWeight: "bold" },
  metricChange: { fontSize: 12 },
  positive: { color: "#22c55e" },
  negative: { color: "#ef4444" },
  sectionTitle: { fontSize: 16, fontWeight: "bold", marginTop: 16, marginBottom: 8 },
  chart: { marginVertical: 8, borderRadius: 8 },
  machineBox: { backgroundColor: "#f3f4f6", borderRadius: 8, padding: 10, marginVertical: 4 },
  darkMachineBox: { backgroundColor: "#333" },
  machineText: { fontSize: 13 },
  alertBox: { backgroundColor: "#fde68a", padding: 8, borderRadius: 8, marginVertical: 8 },
  alertText: { color: "#92400e", fontWeight: "bold" },
  helpBox: { backgroundColor: "#e0e7ff", padding: 10, borderRadius: 8, marginVertical: 12 },
  helpTitle: { fontWeight: "bold", marginBottom: 4 },
  helpText: { fontSize: 13 },
  roiContainer: { backgroundColor: "#dcfce7", borderRadius: 8, padding: 16, marginVertical: 12 },
  roiTitle: { fontSize: 16, fontWeight: "bold", color: "#166534" },
  roiHighlight: { fontSize: 24, fontWeight: "bold", color: "#166534", marginVertical: 4 },
  roiSub: { fontSize: 12, color: "#166534" },
  upsellBox: { backgroundColor: "#e0e7ff", padding: 16, borderRadius: 8, marginVertical: 16, alignItems: "center" },
  upsellTitle: { fontSize: 18, fontWeight: "bold", color: "#3730a3", marginBottom: 4 },
  upsellText: { fontSize: 14, color: "#4338ca", textAlign: "center", marginBottom: 12 },
});
