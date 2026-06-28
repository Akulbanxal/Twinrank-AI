"use client";

import { AnimatedScoreCard } from "@/components/dashboard/AnimatedScoreCard";
import { ProfileCard } from "@/components/dashboard/ProfileCard";
import { ArrowRight, Search, Sparkles } from "lucide-react";
import Link from "next/link";
import { motion, type Variants } from "framer-motion";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

// Add a loading skeleton
function SkeletonCard() {
  return (
    <div className="glass-card p-5 h-32 animate-pulse flex flex-col justify-between">
      <div className="w-1/2 h-5 bg-gray-200/50 rounded"></div>
      <div className="w-3/4 h-4 bg-gray-200/50 rounded"></div>
      <div className="flex gap-2">
        <div className="w-12 h-6 bg-gray-200/50 rounded-md"></div>
        <div className="w-12 h-6 bg-gray-200/50 rounded-md"></div>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchVal, setSearchVal] = useState("");
  const router = useRouter();

  useEffect(() => {
    const fetchTopCandidates = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
        const res = await fetch(`${apiUrl}/api/v1/jobs/candidates`);
        const data = await res.json();
        // Get top 3 candidates
        setCandidates(data.slice(0, 3));
      } catch (err) {
        console.error("Failed to load candidates", err);
      } finally {
        setLoading(false);
      }
    };
    fetchTopCandidates();
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchVal.trim()) {
      router.push(`/explorer?search=${encodeURIComponent(searchVal)}`);
    }
  };

  const containerVariants: Variants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 300, damping: 24 } }
  };

  return (
    <div className="flex flex-col gap-12">
      {/* Hero Section */}
      <motion.section 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="flex flex-col items-center text-center mt-8 mb-4 relative"
      >
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-lavender-50 border border-lavender-100 text-lavender-700 text-xs font-bold mb-6 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 animate-pulse" />
          Powered by XGBoost & LightGBM
        </div>
        
        <h1 className="text-6xl md:text-7xl font-extrabold tracking-tighter text-slate-900 mb-6 leading-tight">
          Discover the top <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-lavender-500 via-indigo-500 to-purple-600 animate-gradient-x">
            1% of talent.
          </span>
        </h1>
        <p className="text-lg md:text-xl text-slate-500 max-w-2xl font-medium leading-relaxed">
          TwinRank AI orchestrates a massive multi-stage ML pipeline to find the perfect fit, optimizing specifically for <span className="text-slate-800 font-semibold border-b border-lavender-300">NDCG without hallucinations.</span>
        </p>
        
        <motion.form 
          onSubmit={handleSearchSubmit}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="mt-12 w-full max-w-2xl relative group"
        >
          <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-lavender-400 group-focus-within:text-lavender-600 transition-colors" />
          </div>
          <input 
            type="text" 
            value={searchVal}
            onChange={(e) => setSearchVal(e.target.value)}
            className="w-full bg-white/70 backdrop-blur-xl border border-white shadow-soft-xl rounded-2xl pl-14 pr-6 py-5 text-slate-900 text-lg placeholder-slate-400 focus:outline-none focus:ring-4 focus:ring-lavender-500/20 transition-all duration-300"
            placeholder="Search by job title, skill, or candidate ID..."
          />
        </motion.form>
      </motion.section>

      {/* Stats Row */}
      <motion.section 
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        <motion.div variants={itemVariants}><AnimatedScoreCard score={0.99} label="NDCG@10" /></motion.div>
        <motion.div variants={itemVariants}><AnimatedScoreCard score={0.96} label="NDCG@50" /></motion.div>
        <motion.div variants={itemVariants}><AnimatedScoreCard score={0.88} label="Honeypot Accuracy" /></motion.div>
        <motion.div variants={itemVariants}><AnimatedScoreCard score={0.94} label="Pipeline Coverage" /></motion.div>
      </motion.section>

      {/* Recommendations */}
      <section className="mt-4 pb-12">
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">Top Recommended Candidates</h2>
          <Link href="/explorer" className="text-sm font-bold text-lavender-600 hover:text-indigo-700 flex items-center gap-1.5 group transition-colors">
            View full pipeline <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {loading ? (
            <>
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </>
          ) : (
            candidates.map((c, i) => (
              <motion.div 
                key={c.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1, duration: 0.5 }}
              >
                <ProfileCard 
                  id={c.id}
                  name={c.name}
                  title={c.title}
                  score={c.score}
                  isHoneypot={c.honeypot_probability > 0.4}
                  skills={c.skills}
                />
              </motion.div>
            ))
          )}
        </div>
      </section>
    </div>
  );
}
