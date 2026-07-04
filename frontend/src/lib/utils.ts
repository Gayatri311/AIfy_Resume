import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(
  /\/$/,
  ""
);

export function apiUnreachableMessage(): string {
  if (typeof window !== "undefined" && !window.location.hostname.includes("localhost")) {
    return (
      `Cannot reach the API at ${API_URL}. ` +
      "On Vercel: set NEXT_PUBLIC_API_URL to your Railway URL (https://….up.railway.app), redeploy, " +
      `then set CORS_ORIGINS on Railway to ${window.location.origin}.`
    );
  }
  return (
    "Cannot reach the API server. Start the backend with: npm run dev:backend " +
    "(or cd backend && uvicorn app.main:app --reload --port 8000)."
  );
}
