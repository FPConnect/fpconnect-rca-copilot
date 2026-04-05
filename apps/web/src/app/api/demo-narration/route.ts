import { NextRequest } from "next/server";
import { tts } from "edge-tts/out/index.js";
import { readFile } from "node:fs/promises";
import path from "node:path";

import { DEMO_STEPS } from "@/lib/demo-institucional";

export const runtime = "nodejs";

const audioCache = new Map<string, Uint8Array>();

function buildEdgeVoice() {
  return process.env.DEMO_NARRATION_EDGE_VOICE?.trim() || "pt-BR-AntonioNeural";
}

function buildOpenAiVoice() {
  return process.env.DEMO_NARRATION_VOICE?.trim() || "onyx";
}

function buildOpenAiModel() {
  return process.env.DEMO_NARRATION_MODEL?.trim() || "gpt-4o-mini-tts";
}

async function synthesizeWithOpenAI(input: string) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    return null;
  }

  const response = await fetch("https://api.openai.com/v1/audio/speech", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: buildOpenAiModel(),
      voice: buildOpenAiVoice(),
      input,
      format: "mp3",
    }),
    cache: "no-store",
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`OpenAI TTS failed: ${response.status} ${errorText}`);
  }

  return new Uint8Array(await response.arrayBuffer());
}

async function synthesizeWithEdgeTTS(input: string) {
  const buffer = await tts(input, {
    voice: buildEdgeVoice(),
    rate: "-4%",
    pitch: "-8Hz",
    volume: "+0%",
  });

  return new Uint8Array(buffer);
}

async function readLocalNarration(stepId: string) {
  const audioPath = path.join(process.cwd(), "public", "narration", "demo-institucional", `${stepId}.mp3`);
  try {
    return new Uint8Array(await readFile(audioPath));
  } catch {
    return null;
  }
}

export async function GET(request: NextRequest) {
  const stepId = request.nextUrl.searchParams.get("step")?.trim();
  if (!stepId || stepId.length > 64 || !/^[a-z0-9-]+$/i.test(stepId)) {
    return new Response(JSON.stringify({ error: "Missing step parameter" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const step = DEMO_STEPS.find((item) => item.id === stepId);
  if (!step) {
    return new Response(JSON.stringify({ error: "Unknown step" }), {
      status: 404,
      headers: { "Content-Type": "application/json" },
    });
  }

  const cached = audioCache.get(step.id);
  if (cached) {
    return new Response(cached.slice().buffer, {
      headers: {
        "Content-Type": "audio/mpeg",
        "Cache-Control": "public, max-age=86400",
      },
    });
  }

  try {
    let audio: Uint8Array | null = null;
    let lastError: unknown = null;

    audio = await readLocalNarration(step.id);

    try {
      if (!audio) {
        audio = await synthesizeWithEdgeTTS(step.narration);
      }
    } catch (error) {
      lastError = error;
    }

    if (!audio) {
      try {
        audio = await synthesizeWithOpenAI(step.narration);
      } catch (error) {
        lastError = error;
      }
    }

    if (!audio) {
      console.error("Narration generation failed", lastError);
      return new Response(JSON.stringify({ error: "Human narration provider unavailable" }), {
        status: 503,
        headers: { "Content-Type": "application/json" },
      });
    }

    audioCache.set(step.id, audio);
    return new Response(audio.slice().buffer, {
      headers: {
        "Content-Type": "audio/mpeg",
        "Cache-Control": "public, max-age=86400",
      },
    });
  } catch (error) {
    console.error("Unexpected narration route error", error);
    return new Response(JSON.stringify({ error: "Unexpected narration error" }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    });
  }
}
