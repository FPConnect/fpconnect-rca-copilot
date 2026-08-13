import { NextResponse } from "next/server";
import {
  evidenceSignals,
  experiments,
  strategicMoats,
  stakeholderPerspectives,
} from "@/lib/strategic-moats";

export function GET() {
  return NextResponse.json({
    generatedAt: new Date().toISOString(),
    strategy: {
      objective:
        "Adicionar diferenciais defensaveis a FPConnect sem alterar fluxos existentes.",
      modules: strategicMoats,
      stakeholderPerspectives,
      experiments,
      evidenceSignals,
    },
  });
}
