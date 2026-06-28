"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface Props {
  confidence: number; // 0 to 100
  className?: string;
}

export function ConfidenceMeter({ confidence, className }: Props) {
  let colorClass = "bg-emerald-500";
  if (confidence < 50) colorClass = "bg-rose-500";
  else if (confidence < 80) colorClass = "bg-amber-500";

  return (
    <div className={cn("w-full", className)}>
      <div className="flex justify-between items-end mb-1.5">
        <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">ML Confidence</span>
        <span className="text-sm font-bold text-gray-900">{confidence.toFixed(1)}%</span>
      </div>
      <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden shadow-inner">
        <motion.div 
          className={cn("h-full rounded-full", colorClass)}
          initial={{ width: 0 }}
          animate={{ width: `${confidence}%` }}
          transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
        />
      </div>
    </div>
  );
}
