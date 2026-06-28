"use client";

import { RankingTable } from "@/components/dashboard/RankingTable";
import { Filter, Search, Sparkles } from "lucide-react";
import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";

function TableSkeleton() {
  return (
    <div className="w-full glass-card overflow-hidden animate-pulse">
      <div className="h-12 bg-gray-50/40 border-b border-gray-200/60 flex items-center px-6">
        <div className="w-16 h-4 bg-gray-200 rounded"></div>
        <div className="w-48 h-4 bg-gray-200 rounded ml-8"></div>
        <div className="w-24 h-4 bg-gray-200 rounded ml-auto"></div>
      </div>
      <div className="p-6 space-y-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="flex items-center justify-between py-2">
            <div className="w-8 h-8 rounded-full bg-gray-200"></div>
            <div className="flex-1 ml-6 space-y-2">
              <div className="w-1/3 h-4 bg-gray-200 rounded"></div>
              <div className="w-1/4 h-3 bg-gray-150 rounded"></div>
            </div>
            <div className="w-20 h-4 bg-gray-200 rounded"></div>
            <div className="w-24 h-8 bg-gray-200 rounded ml-6"></div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ExplorerContent() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchVal, setSearchVal] = useState("");
  const [showHoneypots, setShowHoneypots] = useState<"all" | "clean" | "honeypot">("all");
  const searchParams = useSearchParams();

  useEffect(() => {
    const fetchCandidates = async () => {
      try {
        const res = await fetch("/api/candidates.json");
        const data = await res.json();
        setCandidates(data);
      } catch (err) {
        console.error("Failed to fetch candidates for Explorer", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCandidates();
  }, []);

  useEffect(() => {
    const querySearch = searchParams.get("search");
    if (querySearch) {
      setSearchVal(querySearch);
    }
  }, [searchParams]);

  // Client-side filtering
  const filteredCandidates = candidates.filter((c) => {
    const matchesSearch = 
      c.name.toLowerCase().includes(searchVal.toLowerCase()) ||
      c.id.toLowerCase().includes(searchVal.toLowerCase()) ||
      c.title.toLowerCase().includes(searchVal.toLowerCase()) ||
      c.skills.some((s: string) => s.toLowerCase().includes(searchVal.toLowerCase()));

    const isHoneypot = c.honeypot_probability > 0.4;
    if (showHoneypots === "clean") return matchesSearch && !isHoneypot;
    if (showHoneypots === "honeypot") return matchesSearch && isHoneypot;
    return matchesSearch;
  });

  return (
    <div className="flex flex-col gap-6">
      {/* Header and Filter Buttons */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Candidate Explorer</h1>
            <div className="px-2 py-0.5 rounded-md bg-indigo-50 border border-indigo-100 text-indigo-600 text-[10px] font-bold uppercase tracking-wider">
              Real-time Pipeline
            </div>
          </div>
          <p className="text-gray-500 mt-1 font-medium">Viewing results for <strong className="text-gray-900">Senior AI Engineer</strong></p>
        </div>

        <div className="flex items-center gap-2 self-start md:self-end">
          <div className="flex rounded-lg bg-gray-100/80 p-0.5 border border-gray-200/50 backdrop-blur-md">
            <button 
              onClick={() => setShowHoneypots("all")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${showHoneypots === "all" ? "bg-white text-gray-900 shadow-soft-sm" : "text-gray-500 hover:text-gray-900"}`}
            >
              All
            </button>
            <button 
              onClick={() => setShowHoneypots("clean")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${showHoneypots === "clean" ? "bg-white text-emerald-600 shadow-soft-sm" : "text-gray-500 hover:text-gray-900"}`}
            >
              Clean Only
            </button>
            <button 
              onClick={() => setShowHoneypots("honeypot")}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${showHoneypots === "honeypot" ? "bg-white text-rose-600 shadow-soft-sm" : "text-gray-500 hover:text-gray-900"}`}
            >
              Risk Flagged
            </button>
          </div>
        </div>
      </div>

      {/* Sticky Search bar */}
      <div className="sticky top-[72px] z-40 bg-[#fcfcfd]/80 backdrop-blur-md py-3 -mx-6 px-6 border-b border-gray-100/50 flex gap-4 items-center">
        <div className="relative flex-grow group">
          <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
            <Search className="h-4.5 w-4.5 text-gray-400 group-focus-within:text-lavender-500 transition-colors" />
          </div>
          <input 
            type="text" 
            value={searchVal}
            onChange={(e) => setSearchVal(e.target.value)}
            className="w-full bg-white border border-gray-200/80 shadow-soft-sm rounded-xl pl-12 pr-4 py-3 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-lavender-500/10 focus:border-lavender-400 transition-all duration-200"
            placeholder="Filter candidates by name, ID, role, or skills..."
          />
        </div>
      </div>
      
      {loading ? (
        <TableSkeleton />
      ) : filteredCandidates.length > 0 ? (
        <RankingTable candidates={filteredCandidates} />
      ) : (
        <div className="p-12 text-center text-gray-500 glass-card">
          No matching candidates found.
        </div>
      )}
    </div>
  );
}

export default function Explorer() {
  return (
    <Suspense fallback={<TableSkeleton />}>
      <ExplorerContent />
    </Suspense>
  );
}
