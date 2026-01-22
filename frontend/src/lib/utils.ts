import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getEmotionColor(emotion: string): string {
  const colors: Record<string, string> = {
    Happiness: "#FFD700",
    Sadness: "#4169E1",
    Anger: "#DC143C",
    Fear: "#8B008B",
    Surprise: "#FF6347",
    Love: "#FF69B4",
    Excitement: "#FF4500",
    Contentment: "#98FB98",
    Confidence: "#DAA520",
    Neutral: "#808080",
    Anticipation: "#FFA500",
    Nostalgia: "#DEB887",
    Confusion: "#9370DB",
    Frustration: "#CD5C5C",
    Longing: "#6A5ACD",
    Optimism: "#00CED1",
    Disgust: "#556B2F",
  };
  return colors[emotion] || "#808080";
}

export function formatConfidence(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function getConfidenceLevel(value: number): "high" | "medium" | "low" {
  if (value >= 0.8) return "high";
  if (value >= 0.5) return "medium";
  return "low";
}

export function getConfidenceBadgeColor(level: "high" | "medium" | "low"): string {
  switch (level) {
    case "high":
      return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
    case "medium":
      return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
    case "low":
      return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
  }
}
