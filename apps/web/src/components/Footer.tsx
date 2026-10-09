import BrandLogo from "@/components/BrandLogo";

export default function Footer() {
  return (
    <footer className="bg-[#071a33] text-white py-6 px-4 mt-auto">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
        <BrandLogo inverse />
        <p className="text-sm text-slate-300">
          © {new Date().getFullYear()} OPSPECTA. Todos os direitos reservados.
        </p>
      </div>
    </footer>
  );
}
