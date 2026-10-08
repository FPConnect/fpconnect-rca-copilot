import { APP_NAME } from "@/lib/brand";

export default function Footer() {
  return (
    <footer className="bg-gray-800 text-white py-6 px-4 mt-auto">
      <div className="max-w-7xl mx-auto text-center">
        <p className="text-sm text-gray-300">
          © {new Date().getFullYear()} {APP_NAME}
        </p>
      </div>
    </footer>
  );
}
