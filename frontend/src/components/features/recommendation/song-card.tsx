"use client";

import React from "react";
import { motion } from "framer-motion";
import { Music2, Star, Heart } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { SpotifyEmbed } from "./spotify-embed";
import type { Song } from "@/lib/api-client";

interface SongCardProps {
  song: Song;
  matchScore: number;
  matchedEmotions: string[];
  explanation?: string;
  whyThisSong?: string[];
  onFeedback?: (rating: number) => void;
}

export function SongCard({
  song,
  matchScore,
  matchedEmotions,
  explanation,
  whyThisSong,
  onFeedback,
}: SongCardProps) {
  const [rating, setRating] = React.useState<number | null>(null);

  const handleRating = (value: number) => {
    setRating(value);
    onFeedback?.(value);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="overflow-hidden">
        <CardContent className="p-6 space-y-6">
          {/* Song Info */}
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <h3 className="text-xl font-semibold flex items-center gap-2">
                <Music2 className="h-5 w-5 text-primary" />
                {song.name}
              </h3>
              <p className="text-muted-foreground">{song.artists}</p>
            </div>
            <Badge variant="success" className="text-lg px-3 py-1">
              {Math.round(matchScore * 100)}% Match
            </Badge>
          </div>

          {/* Matched Emotions */}
          {matchedEmotions.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {matchedEmotions.map((emotion) => (
                <Badge key={emotion} variant="secondary">
                  {emotion}
                </Badge>
              ))}
            </div>
          )}

          {/* Spotify Player */}
          <SpotifyEmbed trackId={song.spotify_track_id} />

          {/* AI Explanation */}
          {explanation && (
            <div className="bg-muted/50 rounded-lg p-4 space-y-2">
              <h4 className="font-semibold text-sm">Why this song?</h4>
              <p className="text-sm text-muted-foreground">{explanation}</p>
              {whyThisSong && whyThisSong.length > 0 && (
                <ul className="text-sm text-muted-foreground space-y-1 mt-2">
                  {whyThisSong.map((reason, i) => (
                    <li key={i} className="flex items-center gap-2">
                      <span className="text-primary">•</span>
                      {reason}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {/* Rating */}
          {onFeedback && (
            <div className="flex items-center justify-between pt-4 border-t">
              <span className="text-sm text-muted-foreground">
                Rate this recommendation:
              </span>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((value) => (
                  <button
                    key={value}
                    onClick={() => handleRating(value)}
                    className={`p-1 transition-colors ${
                      rating && rating >= value
                        ? "text-yellow-500"
                        : "text-muted-foreground hover:text-yellow-400"
                    }`}
                  >
                    <Star
                      className="h-6 w-6"
                      fill={rating && rating >= value ? "currentColor" : "none"}
                    />
                  </button>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
