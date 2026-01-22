"use client";

import React from "react";
import { motion } from "framer-motion";

interface SpotifyEmbedProps {
  trackId: string;
  className?: string;
}

export function SpotifyEmbed({ trackId, className = "" }: SpotifyEmbedProps) {
  const embedUrl = `https://open.spotify.com/embed/track/${trackId}?utm_source=generator&theme=0`;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className={`spotify-embed ${className}`}
    >
      <iframe
        src={embedUrl}
        width="100%"
        height="352"
        frameBorder="0"
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
        loading="lazy"
        className="rounded-xl"
      />
    </motion.div>
  );
}
