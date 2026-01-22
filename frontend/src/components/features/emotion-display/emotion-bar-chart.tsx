"use client";

import React from "react";
import { motion } from "framer-motion";
import { getEmotionColor, formatConfidence } from "@/lib/utils";

interface EmotionBarChartProps {
  emotions: Record<string, number>;
  maxItems?: number;
  showAll?: boolean;
}

export function EmotionBarChart({
  emotions,
  maxItems = 5,
  showAll = false,
}: EmotionBarChartProps) {
  const sortedEmotions = Object.entries(emotions)
    .sort(([, a], [, b]) => b - a)
    .slice(0, showAll ? undefined : maxItems);

  return (
    <div className="space-y-3">
      {sortedEmotions.map(([emotion, value], index) => (
        <motion.div
          key={emotion}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 }}
          className="space-y-1"
        >
          <div className="flex justify-between text-sm">
            <span className="font-medium">{emotion}</span>
            <span className="text-muted-foreground">
              {formatConfidence(value)}
            </span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${value * 100}%` }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="h-full rounded-full"
              style={{ backgroundColor: getEmotionColor(emotion) }}
            />
          </div>
        </motion.div>
      ))}
    </div>
  );
}
