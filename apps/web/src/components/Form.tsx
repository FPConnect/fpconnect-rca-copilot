import { FormHTMLAttributes, ReactNode } from "react";

interface FormProps extends FormHTMLAttributes<HTMLFormElement> {
  children: ReactNode;
  title?: string;
}

export default function Form({ children, title, className = "", ...props }: FormProps) {
  return (
    <form className={`bg-white rounded-xl shadow p-6 ${className}`} {...props}>
      {title && (
        <h2 className="text-lg font-semibold text-gray-800 mb-4">{title}</h2>
      )}
      {children}
    </form>
  );
}
