"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Music2,
  Brain,
  Sparkles,
  ArrowRight,
  Mic,
  BarChart3,
  Heart,
  Zap,
  Github,
  ExternalLink,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const features = [
  {
    icon: Brain,
    title: "AI-Powered Emotion Detection",
    description:
      "BERT-based NLP model trained on 10,000+ dialogues detects 17 nuanced emotions from your text.",
  },
  {
    icon: Sparkles,
    title: "Explainable AI",
    description:
      "Understand why we recommend each song with SHAP-powered explanations and confidence scores.",
  },
  {
    icon: Mic,
    title: "Voice Input",
    description:
      "Speak your mood instead of typing. Our voice recognition captures your emotional state naturally.",
  },
  {
    icon: BarChart3,
    title: "Mood Insights",
    description:
      "Track your emotional patterns over time and discover insights about your music preferences.",
  },
  {
    icon: Heart,
    title: "Personalized Learning",
    description:
      "The more you use it, the better it gets. Our AI learns your preferences for perfect recommendations.",
  },
  {
    icon: Zap,
    title: "Real-Time Analysis",
    description:
      "Sub-100ms inference time for instant emotion analysis and music recommendations.",
  },
];

const emotions = [
  "Happiness",
  "Excitement",
  "Love",
  "Contentment",
  "Optimism",
  "Confidence",
  "Nostalgia",
  "Anticipation",
  "Sadness",
  "Anger",
  "Fear",
  "Confusion",
  "Frustration",
  "Longing",
  "Surprise",
  "Disgust",
  "Neutral",
];

const techStack = [
  { name: "BERT", category: "NLP" },
  { name: "PyTorch", category: "ML" },
  { name: "FastAPI", category: "Backend" },
  { name: "PostgreSQL", category: "Database" },
  { name: "Next.js 14", category: "Frontend" },
  { name: "TypeScript", category: "Language" },
  { name: "Tailwind CSS", category: "Styling" },
  { name: "SHAP", category: "XAI" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <Music2 className="h-8 w-8 text-primary" />
            <span className="text-xl font-bold gradient-text">MoodTune AI</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/analyze">
              <Button variant="ghost">Try Now</Button>
            </Link>
            <a
              href="https://github.com/parthmghayal/NLP-Music-Recommendation"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button variant="outline" size="icon">
                <Github className="h-5 w-5" />
              </Button>
            </a>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="container mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Badge variant="secondary" className="mb-6">
              AI-Powered Music Discovery
            </Badge>
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              <span className="gradient-text">Feel the Music</span>
              <br />
              That Feels You
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
              Express your emotions in words, and let our AI find the perfect
              soundtrack for your mood. Powered by BERT and trained on thousands
              of emotional expressions.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/analyze">
                <Button size="xl" variant="gradient" className="gap-2">
                  Start Discovering
                  <ArrowRight className="h-5 w-5" />
                </Button>
              </Link>
              <Link href="#features">
                <Button size="xl" variant="outline">
                  Learn More
                </Button>
              </Link>
            </div>
          </motion.div>

          {/* Emotion Pills Animation */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.8 }}
            className="mt-16 flex flex-wrap justify-center gap-2 max-w-4xl mx-auto"
          >
            {emotions.map((emotion, i) => (
              <motion.div
                key={emotion}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.6 + i * 0.05 }}
              >
                <Badge
                  variant="outline"
                  className="text-sm py-1 px-3 hover:bg-primary/10 transition-colors cursor-default"
                >
                  {emotion}
                </Badge>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "1",
                title: "Express Your Mood",
                description:
                  "Type or speak how you're feeling. Describe your day, your emotions, or just a thought.",
              },
              {
                step: "2",
                title: "AI Analyzes Emotions",
                description:
                  "Our BERT model detects nuanced emotions with confidence scores and explanations.",
              },
              {
                step: "3",
                title: "Get Perfect Music",
                description:
                  "Receive a personalized song recommendation that matches your emotional state.",
              },
            ].map((item, i) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.2 }}
                viewport={{ once: true }}
              >
                <Card className="text-center h-full">
                  <CardContent className="pt-6">
                    <div className="w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xl font-bold mx-auto mb-4">
                      {item.step}
                    </div>
                    <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                    <p className="text-muted-foreground">{item.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 px-4">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">
            Powerful Features
          </h2>
          <p className="text-muted-foreground text-center mb-12 max-w-2xl mx-auto">
            Built with cutting-edge AI technology to deliver the most accurate
            emotion detection and music recommendations.
          </p>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full hover:shadow-lg transition-shadow">
                  <CardContent className="pt-6">
                    <feature.icon className="h-10 w-10 text-primary mb-4" />
                    <h3 className="text-lg font-semibold mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-muted-foreground text-sm">
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">
            Built With Modern Tech
          </h2>
          <p className="text-muted-foreground text-center mb-12">
            Production-grade architecture showcasing full-stack AI expertise
          </p>
          <div className="flex flex-wrap justify-center gap-4 max-w-3xl mx-auto">
            {techStack.map((tech) => (
              <Badge
                key={tech.name}
                variant="secondary"
                className="text-sm py-2 px-4"
              >
                <span className="font-semibold">{tech.name}</span>
                <span className="text-muted-foreground ml-2">
                  {tech.category}
                </span>
              </Badge>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Find Your Sound?</h2>
          <p className="text-muted-foreground mb-8 max-w-xl mx-auto">
            Start discovering music that truly resonates with how you feel.
            No account required.
          </p>
          <Link href="/analyze">
            <Button size="xl" variant="gradient" className="gap-2">
              Try MoodTune AI Now
              <ArrowRight className="h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8 px-4">
        <div className="container mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Music2 className="h-6 w-6 text-primary" />
            <span className="font-semibold">MoodTune AI</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Emotion-aware music recommendations powered by BERT
          </p>
          <div className="flex items-center gap-4">
            <a
              href="https://github.com/parthmghayal/NLP-Music-Recommendation"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              <Github className="h-5 w-5" />
            </a>
            <a
              href="/docs"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              <ExternalLink className="h-5 w-5" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
