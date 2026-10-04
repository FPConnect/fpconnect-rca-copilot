import { APP_NAME, BRAND_TRANSITION_NOTICE } from "@/lib/brand";

export default function Footer() {
  return (
    <footer className="bg-gray-800 text-white py-6 px-4 mt-auto">
      <div className="max-w-7xl mx-auto text-center">
        <p className="text-sm text-gray-300">
          © {new Date().getFullYear()} {APP_NAME}
        </p>
        <p className="mt-1 text-xs text-gray-400">{BRAND_TRANSITION_NOTICE}</p>
      </div>
    </footer>
  );
}
