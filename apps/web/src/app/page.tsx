import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gray-50 p-8">
      <div className="max-w-2xl text-center">
        <h1 className="text-4xl font-bold text-blue-700 mb-4">
          FPConnect RCA Copilot
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          AI-powered Root Cause Analysis & Availability Engine for
          Healthcare/MedTech Operations
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/dashboard"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
          >
            Dashboard
          </Link>
          <Link
            href="/tickets"
            className="bg-white text-blue-600 border border-blue-600 px-6 py-3 rounded-lg hover:bg-blue-50 transition"
          >
            View Tickets
          </Link>
        </div>
      </div>
    </main>
  );
}
