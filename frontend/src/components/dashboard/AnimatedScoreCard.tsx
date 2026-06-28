"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

interface Props {
  score: number; // 0 to 1
  label: string;
  className?: string;
}

export function AnimatedScoreCard({ score, label, className }: Props) {
  const [displayScore, setDisplayScore] = useState(0);
  const percentage = Math.round(score * 100);

  useEffect(() => {
    let start = 0;
    const end = percentage;
    if (start === end) return;

    let totalDuration = 1000;
    let incrementTime = (totalDuration / end) * 2;

    let timer = setInterval(() => {
      start += 1;
      setDisplayScore(start);
      if (start === end) clearInterval(timer);
    }, incrementTime);

    return () => clearInterval(timer);
  }, [percentage]);

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5, transition: { duration: 0.2 } }}
      className={cn("glass-card p-6 flex flex-col items-center justify-center gap-2 relative overflow-hidden group", className)}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-lavender-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      <div className="relative w-24 h-24 flex items-center justify-center">
        <svg className="w-full h-full transform -rotate-90">
          <circle cx="48" cy="48" r="40" className="stroke-gray-100 fill-none" strokeWidth="6" />
          <motion.circle 
            cx="48" 
            cy="48" 
            r="40" 
            className="stroke-lavender-500 fill-none" 
            strokeWidth="6"
            strokeDasharray="251.2"
            initial={{ strokeDashoffset: 251.2 }}
            animate={{ strokeDashoffset: 251.2 - (251.2 * percentage) / 100 }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute flex flex-col items-center">
          <span className="text-3xl font-bold text-gray-900 tracking-tighter">{displayScore}</span>
        </div>
      </div>
      <span className="text-xs font-semibold text-gray-500 uppercase tracking-widest mt-2">{label}</span>
    </motion.div>
  );
}
