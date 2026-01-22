"use client";

import React from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { getEmotionColor } from "@/lib/utils";

interface EmotionRadarChartProps {
  emotions: Record<string, number>;
  size?: "sm" | "md" | "lg";
}

export function EmotionRadarChart({
  emotions,
  size = "md",
}: EmotionRadarChartProps) {
  const data = Object.entries(emotions)
    .map(([name, value]) => ({
      emotion: name,
      value: Math.round(value * 100),
      fullMark: 100,
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8); // Show top 8 emotions for readability

  const heights = {
    sm: 200,
    md: 300,
    lg: 400,
  };

  return (
    <div className="w-full" style={{ height: heights[size] }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
          <PolarGrid stroke="hsl(var(--border))" />
          <PolarAngleAxis
            dataKey="emotion"
            tick={{ fill: "hsl(var(--foreground))", fontSize: 12 }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
          />
          <Radar
            name="Emotion"
            dataKey="value"
            stroke="hsl(var(--primary))"
            fill="hsl(var(--primary))"
            fillOpacity={0.3}
            strokeWidth={2}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="bg-popover text-popover-foreground px-3 py-2 rounded-lg shadow-lg border">
                    <p className="font-semibold">{data.emotion}</p>
                    <p className="text-sm text-muted-foreground">
                      {data.value}% confidence
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
