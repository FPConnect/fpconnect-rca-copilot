import nextCoreWebVitals from "eslint-config-next/core-web-vitals";

export default [
  ...nextCoreWebVitals,
  {
    files: [
      "src/app/analyze/page.tsx",
      "src/app/tickets/page.tsx",
      "src/components/LandingLanguageSwitcher.tsx",
      "src/components/SearchBar.tsx",
      "src/contexts/AuthContext.tsx",
    ],
    rules: {
      // These effects hydrate URL, API, storage, or controlled-input state after mount.
      "react-hooks/set-state-in-effect": "off",
    },
  },
];
