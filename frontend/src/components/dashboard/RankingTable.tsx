"use client";

import { motion } from "framer-motion";
import { ArrowRight, ShieldAlert, ArrowUpDown, ChevronUp, ChevronDown } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface CandidateRow {
  id: string;
  rank: number;
  score: number;
  honeypot_probability: number;
  name: string;
  title: string;
  experience_years: number;
  skills: string[];
  why_selected: string;
  strengths: string[];
}

interface Props {
  candidates: CandidateRow[];
}

type SortField = "score" | "risk" | "experience";
type SortOrder = "asc" | "desc" | null;

export function RankingTable({ candidates }: Props) {
  const router = useRouter();
  const [sortField, setSortField] = useState<SortField>("score");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      // Toggle order
      if (sortOrder === "desc") setSortOrder("asc");
      else if (sortOrder === "asc") {
        setSortField("score");
        setSortOrder("desc");
      }
    } else {
      setSortField(field);
      setSortOrder("desc");
    }
  };

  const sortedCandidates = [...candidates].sort((a, b) => {
    if (!sortOrder) return 0;
    let aVal = 0;
    let bVal = 0;

    if (sortField === "score") {
      aVal = a.score;
      bVal = b.score;
    } else if (sortField === "risk") {
      aVal = a.honeypot_probability;
      bVal = b.honeypot_probability;
    } else if (sortField === "experience") {
      aVal = a.experience_years;
      bVal = b.experience_years;
    }

    if (sortOrder === "asc") {
      return aVal - bVal;
    } else {
      return bVal - aVal;
    }
  });

  const SortIndicator = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-3.5 h-3.5 text-gray-400 group-hover:text-gray-600 transition-colors ml-1" />;
    }
    if (sortOrder === "asc") {
      return <ChevronUp className="w-3.5 h-3.5 text-lavender-600 ml-1" />;
    }
    return <ChevronDown className="w-3.5 h-3.5 text-lavender-600 ml-1" />;
  };

  return (
    <div className="w-full glass-card overflow-hidden border border-white shadow-soft-xl">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50/50 border-b border-gray-200/60 backdrop-blur-md">
              <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Rank</th>
              <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Candidate</th>
              
              <th 
                onClick={() => handleSort("experience")}
                className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100/50 group select-none transition-colors"
              >
                <div className="flex items-center">
                  Experience
                  <SortIndicator field="experience" />
                </div>
              </th>
              
              <th 
                onClick={() => handleSort("score")}
                className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100/50 group select-none transition-colors"
              >
                <div className="flex items-center">
                  ML Score
                  <SortIndicator field="score" />
                </div>
              </th>

              <th 
                onClick={() => handleSort("risk")}
                className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100/50 group select-none transition-colors"
              >
                <div className="flex items-center">
                  Honeypot Risk
                  <SortIndicator field="risk" />
                </div>
              </th>
              
              <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">Matched Skills</th>
              <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {sortedCandidates.map((c, idx) => {
              const isHoneypot = c.honeypot_probability > 0.4;
              return (
                <motion.tr 
                  onClick={() => router.push(`/candidate/${c.id}`)}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: Math.min(idx * 0.02, 0.4), duration: 0.2 }}
                  key={c.id} 
                  className={cn(
                    "border-b border-gray-100/60 hover:bg-lavender-50/50 cursor-pointer transition-all duration-200 group relative",
                    isHoneypot ? "bg-rose-50/20 hover:bg-rose-50/40" : ""
                  )}
                  whileHover={{ 
                    y: -1, 
                    boxShadow: "0 8px 24px -6px rgba(124, 58, 237, 0.08)",
                    zIndex: 10
                  }}
                >
                  <td className="px-6 py-5 whitespace-nowrap">
                    <div className={cn(
                      "w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold shadow-sm transition-transform group-hover:scale-105 duration-200", 
                      c.rank <= 3 ? "bg-gradient-to-br from-lavender-400 to-indigo-600 text-white" : "bg-white border border-gray-200 text-gray-500"
                    )}>
                      {c.rank}
                    </div>
                  </td>
                  
                  <td className="px-6 py-5 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <div className="font-bold text-slate-800 tracking-tight group-hover:text-indigo-600 transition-colors">{c.name}</div>
                      {isHoneypot && (
                        <div className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-rose-100 text-rose-700 text-[10px] font-bold">
                          <ShieldAlert className="w-3 h-3" /> Flagged
                        </div>
                      )}
                    </div>
                    <div className="text-xs text-slate-400 mt-1 font-medium">{c.title}</div>
                  </td>

                  <td className="px-6 py-5 whitespace-nowrap">
                    <div className="text-sm font-semibold text-slate-700">{c.experience_years.toFixed(1)} yrs</div>
                  </td>
                  
                  <td className="px-6 py-5 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <div className="w-16 bg-gray-100 rounded-full h-1.5 shadow-inner overflow-hidden">
                        <div className="bg-gradient-to-r from-lavender-500 to-indigo-500 h-1.5 rounded-full" style={{ width: `${c.score * 100}%` }}></div>
                      </div>
                      <span className="text-sm font-extrabold text-slate-800">{(c.score * 100).toFixed(1)}</span>
                    </div>
                  </td>

                  <td className="px-6 py-5 whitespace-nowrap">
                    <span className={cn(
                      "text-xs font-bold px-2.5 py-1 rounded-full",
                      c.honeypot_probability > 0.7 ? "bg-rose-100 text-rose-700 border border-rose-200" :
                      c.honeypot_probability > 0.4 ? "bg-amber-100 text-amber-700 border border-amber-200" :
                      "bg-emerald-100 text-emerald-700 border border-emerald-200"
                    )}>
                      {(c.honeypot_probability * 100).toFixed(0)}%
                    </span>
                  </td>
                  
                  <td className="px-6 py-5 max-w-xs truncate">
                    <div className="flex flex-wrap gap-1">
                      {c.skills.slice(0, 3).map(skill => (
                        <span key={skill} className="px-1.5 py-0.5 bg-slate-100 text-slate-600 text-[10px] font-bold uppercase rounded tracking-wider border border-slate-200/50">
                          {skill}
                        </span>
                      ))}
                      {c.skills.length > 3 && (
                        <span className="text-[10px] font-bold text-slate-400 self-center">
                          +{c.skills.length - 3}
                        </span>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-6 py-5 whitespace-nowrap text-right">
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        router.push(`/candidate/${c.id}`);
                      }}
                      className="inline-flex items-center gap-1 text-xs font-extrabold uppercase tracking-wider text-lavender-600 hover:text-indigo-700 transition-colors opacity-0 group-hover:opacity-100 translate-x-2 group-hover:translate-x-0 duration-300"
                    >
                      Review <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
