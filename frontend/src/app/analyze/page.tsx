"use client";

import React, { useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Music2,
  Mic,
  MicOff,
  Send,
  Loader2,
  ArrowLeft,
  Info,
  RefreshCw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { EmotionRadarChart } from "@/components/features/emotion-display/emotion-radar-chart";
import { EmotionBarChart } from "@/components/features/emotion-display/emotion-bar-chart";
import { SongCard } from "@/components/features/recommendation/song-card";
import {
  cn,
  formatConfidence,
  getConfidenceLevel,
  getConfidenceBadgeColor,
} from "@/lib/utils";
import apiClient, { type RecommendationResponse } from "@/lib/api-client";

const placeholders = [
  "I just got great news and can't stop smiling...",
  "Feeling a bit melancholic today, thinking about the past...",
  "Had an amazing workout, full of energy!",
  "It's a rainy day and I want to relax...",
  "Missing someone special right now...",
  "Excited about the weekend plans!",
];

export default function AnalyzePage() {
  const [text, setText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [placeholder] = useState(
    () => placeholders[Math.floor(Math.random() * placeholders.length)]
  );

  const handleSubmit = async () => {
    if (!text.trim()) {
      setError("Please enter how you're feeling");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.getRecommendation(text);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceInput = () => {
    if (!("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
      setError("Voice input is not supported in your browser");
      return;
    }

    const SpeechRecognition =
      (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results)
        .map((result: any) => result[0].transcript)
        .join("");
      setText(transcript);
    };

    recognition.onerror = () => {
      setIsListening(false);
      setError("Voice recognition failed. Please try again.");
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  const handleReset = () => {
    setText("");
    setResult(null);
    setError(null);
  };

  const handleFeedback = async (rating: number) => {
    if (result) {
      try {
        await apiClient.submitFeedback(result.id, rating);
      } catch (err) {
        console.error("Failed to submit feedback:", err);
      }
    }
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b glass sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <ArrowLeft className="h-5 w-5" />
            <Music2 className="h-6 w-6 text-primary" />
            <span className="font-bold">MoodTune AI</span>
          </Link>
          {result && (
            <Button variant="ghost" onClick={handleReset} className="gap-2">
              <RefreshCw className="h-4 w-4" />
              New Analysis
            </Button>
          )}
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Input Section */}
          <AnimatePresence mode="wait">
            {!result ? (
              <motion.div
                key="input"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <div className="text-center mb-8">
                  <h1 className="text-3xl font-bold mb-2">
                    How are you feeling?
                  </h1>
                  <p className="text-muted-foreground">
                    Describe your mood, day, or current emotions
                  </p>
                </div>

                <Card>
                  <CardContent className="pt-6">
                    <div className="space-y-4">
                      <div className="relative">
                        <Textarea
                          value={text}
                          onChange={(e) => setText(e.target.value)}
                          placeholder={placeholder}
                          className="min-h-[150px] text-lg pr-12 resize-none"
                          maxLength={5000}
                        />
                        <div className="absolute bottom-3 right-3 flex gap-2">
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            onClick={handleVoiceInput}
                            className={cn(
                              "rounded-full",
                              isListening && "text-red-500 animate-pulse"
                            )}
                          >
                            {isListening ? (
                              <MicOff className="h-5 w-5" />
                            ) : (
                              <Mic className="h-5 w-5" />
                            )}
                          </Button>
                        </div>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">
                          {text.length}/5000 characters
                        </span>
                        <Button
                          onClick={handleSubmit}
                          disabled={isLoading || !text.trim()}
                          className="gap-2"
                          size="lg"
                        >
                          {isLoading ? (
                            <>
                              <Loader2 className="h-4 w-4 animate-spin" />
                              Analyzing...
                            </>
                          ) : (
                            <>
                              <Send className="h-4 w-4" />
                              Get Recommendation
                            </>
                          )}
                        </Button>
                      </div>

                      {error && (
                        <div className="text-red-500 text-sm text-center">
                          {error}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>

                {/* Tips */}
                <div className="flex items-start gap-3 p-4 bg-muted/50 rounded-lg">
                  <Info className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
                  <div className="text-sm text-muted-foreground">
                    <p className="font-medium mb-1">Tips for better results:</p>
                    <ul className="list-disc list-inside space-y-1">
                      <li>Be descriptive about how you feel</li>
                      <li>Mention specific events or situations</li>
                      <li>Use the voice input for natural expression</li>
                    </ul>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="result"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-8"
              >
                {/* Emotion Analysis Results */}
                {result.emotion_analysis && (
                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Primary Emotion */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                          <span>Emotion Analysis</span>
                          <Badge
                            className={getConfidenceBadgeColor(
                              getConfidenceLevel(
                                result.emotion_analysis.primary_confidence
                              )
                            )}
                          >
                            {result.emotion_analysis.confidence_level} confidence
                          </Badge>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-center mb-6">
                          <p className="text-sm text-muted-foreground mb-1">
                            Primary Emotion
                          </p>
                          <p className="text-3xl font-bold text-primary">
                            {result.emotion_analysis.primary_emotion}
                          </p>
                          <p className="text-lg text-muted-foreground">
                            {formatConfidence(
                              result.emotion_analysis.primary_confidence
                            )}
                          </p>
                        </div>

                        {result.emotion_analysis.secondary_emotions.length >
                          0 && (
                          <div className="flex flex-wrap gap-2 justify-center">
                            {result.emotion_analysis.secondary_emotions.map(
                              (emotion) => (
                                <Badge key={emotion} variant="secondary">
                                  {emotion}
                                </Badge>
                              )
                            )}
                          </div>
                        )}

                        {result.emotion_analysis.explanation && (
                          <p className="text-sm text-muted-foreground mt-4 text-center">
                            {result.emotion_analysis.explanation}
                          </p>
                        )}
                      </CardContent>
                    </Card>

                    {/* Emotion Visualization */}
                    <Card>
                      <CardHeader>
                        <CardTitle>Emotion Breakdown</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <EmotionBarChart
                          emotions={result.emotion_analysis.emotions}
                          maxItems={6}
                        />
                      </CardContent>
                    </Card>
                  </div>
                )}

                {/* Radar Chart */}
                {result.emotion_analysis && (
                  <Card>
                    <CardHeader>
                      <CardTitle>Emotion Radar</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <EmotionRadarChart
                        emotions={result.emotion_analysis.emotions}
                        size="md"
                      />
                    </CardContent>
                  </Card>
                )}

                {/* Song Recommendation */}
                <div>
                  <h2 className="text-2xl font-bold mb-4">
                    Your Perfect Match
                  </h2>
                  <SongCard
                    song={result.song}
                    matchScore={result.match_score}
                    matchedEmotions={result.matched_emotions}
                    explanation={result.explanation}
                    whyThisSong={result.why_this_song}
                    onFeedback={handleFeedback}
                  />
                </div>

                {/* Try Again */}
                <div className="text-center">
                  <Button
                    variant="outline"
                    onClick={handleReset}
                    className="gap-2"
                  >
                    <RefreshCw className="h-4 w-4" />
                    Try Another Mood
                  </Button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
