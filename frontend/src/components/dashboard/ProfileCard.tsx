"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Briefcase, AlertTriangle } from "lucide-react";
import Link from "next/link";

interface ProfileCardProps {
  id: string;
  name: string;
  title: string;
  score: number;
  isHoneypot: boolean;
  skills: string[];
}

export function ProfileCard({ id, name, title, score, isHoneypot, skills }: ProfileCardProps) {
  return (
    <Link href={`/candidate/${id}`}>
      <motion.div
        whileHover={{ y: -4, scale: 1.01 }}
        className="glass-card p-5 flex flex-col gap-4 cursor-pointer relative overflow-hidden transition-all duration-300 hover:shadow-soft-xl"
      >
        {isHoneypot && (
          <div className="absolute top-0 right-0 bg-rose-500 text-white text-[10px] font-bold px-3 py-1 rounded-bl-lg flex items-center gap-1 shadow-sm">
            <AlertTriangle className="w-3 h-3" /> HIGH RISK
          </div>
        )}
        
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-bold text-gray-900 tracking-tight">{name}</h3>
            <p className="text-sm font-medium text-lavender-600 flex items-center gap-1.5 mt-0.5">
              <Briefcase className="w-4 h-4" />
              {title}
            </p>
          </div>
          <div className="bg-lavender-50 px-3 py-1.5 rounded-full border border-lavender-100 shadow-sm">
            <span className="text-sm font-bold text-lavender-700">{(score * 100).toFixed(0)}</span>
          </div>
        </div>
        
        <div className="flex flex-wrap gap-1.5 mt-2">
          {skills.slice(0, 4).map(skill => (
            <span key={skill} className="px-2 py-1 bg-white/80 text-gray-600 text-[11px] font-semibold tracking-wide uppercase rounded-md border border-gray-200/60 shadow-sm">
              {skill}
            </span>
          ))}
          {skills.length > 4 && (
            <span className="px-2 py-1 bg-gray-50/50 text-gray-400 text-[11px] font-medium rounded-md border border-gray-100">
              +{skills.length - 4} more
            </span>
          )}
        </div>
      </motion.div>
    </Link>
  );
}
