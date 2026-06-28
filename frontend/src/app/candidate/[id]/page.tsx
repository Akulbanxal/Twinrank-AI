import { CandidateRadarChart } from "@/components/dashboard/RadarChart";
import { ConfidenceMeter } from "@/components/dashboard/ConfidenceMeter";
import { CheckCircle2, AlertOctagon, Info, ArrowLeft, Briefcase, Award } from "lucide-react";
import Link from "next/link";
import fs from "fs";
import path from "path";

export default async function CandidateDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let candidate: any = null;
  let errorMsg: string | null = null;

  try {
    const jsonPath = path.join(process.cwd(), "public", "api", "candidates", `${id}.json`);
    if (!fs.existsSync(jsonPath)) {
      throw new Error(`Candidate details file not found at: ${jsonPath}`);
    }
    const fileContent = fs.readFileSync(jsonPath, "utf-8");
    candidate = JSON.parse(fileContent);
  } catch (err: any) {
    console.error(err);
    errorMsg = err.message || "Failed to load candidate details.";
  }

  if (errorMsg || !candidate) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <div className="glass-card p-8 max-w-md text-center flex flex-col items-center gap-4">
          <AlertOctagon className="w-12 h-12 text-rose-500" />
          <h2 className="text-xl font-bold text-slate-800">Error Loading Candidate</h2>
          <p className="text-slate-500 text-sm">{errorMsg || "Candidate profile could not be retrieved."}</p>
          <Link href="/explorer" className="mt-2 inline-flex items-center gap-2 text-sm font-bold text-lavender-600 hover:text-indigo-700 transition-colors">
            <ArrowLeft className="w-4 h-4" /> Back to Rankings
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 pb-12">
      <Link href="/explorer" className="inline-flex items-center gap-2 text-sm font-bold text-gray-500 hover:text-gray-900 transition-colors w-fit group">
        <ArrowLeft className="w-4 h-4 transform group-hover:-translate-x-1 transition-transform" /> Back to Rankings
      </Link>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Profile & Radar */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <div className="glass-panel p-8 border border-white shadow-soft-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-24 h-24 bg-lavender-500/10 rounded-full blur-xl pointer-events-none"></div>
            
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">{candidate.name}</h1>
            <p className="text-indigo-600 font-bold mt-1 text-lg flex items-center gap-2">
              <Briefcase className="w-4.5 h-4.5" />
              {candidate.title}
            </p>
            
            <div className="mt-8">
              <ConfidenceMeter confidence={candidate.explainability.confidence_score} />
            </div>
            
            <div className="mt-8 pt-6 border-t border-gray-100/80 flex justify-between items-center">
              <div className="flex flex-col gap-1">
                <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Final ML Score</span>
                <span className="text-5xl font-black text-slate-900 tracking-tighter">{(candidate.score * 100).toFixed(1)}</span>
              </div>
              <div className="px-4 py-2 rounded-xl bg-slate-50 border border-gray-100 shadow-sm flex flex-col items-center">
                <span className="text-[9px] font-bold text-gray-400 uppercase tracking-wider">Experience</span>
                <span className="text-lg font-black text-slate-700">{candidate.experience_years.toFixed(1)}y</span>
              </div>
            </div>
          </div>
          
          <CandidateRadarChart data={candidate.chartData} />

          {/* Key Skills Side Bar */}
          <div className="glass-card p-6 border border-white shadow-soft-xl">
            <div className="flex items-center gap-2 mb-4 border-b border-gray-100/60 pb-2">
              <Award className="w-4.5 h-4.5 text-lavender-600" />
              <h3 className="font-bold text-slate-900 text-sm uppercase tracking-wider">Skills Inventory</h3>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {candidate.skills.map((skill: string) => (
                <span key={skill} className="px-2 py-1 bg-slate-50 text-slate-600 text-[10px] font-bold uppercase rounded tracking-wider border border-slate-200/50">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>
        
        {/* Right Column: Explainability View */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <div className="flex items-center justify-between px-1">
            <h2 className="text-xl font-bold tracking-tight text-slate-900">Explainability Engine Output</h2>
            <span className="text-xs font-semibold text-slate-400 font-mono">Candidate ID: {candidate.id}</span>
          </div>
          
          <div className="glass-card p-6 border-l-[6px] border-l-lavender-500 shadow-soft-md">
            <div className="flex items-center gap-2 mb-3">
              <Info className="w-5 h-5 text-lavender-600" />
              <h3 className="font-bold text-gray-900 text-lg">Why Selected</h3>
            </div>
            <p className="text-gray-700 leading-relaxed font-medium">{candidate.explainability.why_selected}</p>
          </div>
          
          <div className="glass-card p-6 border-l-[6px] border-l-emerald-500 shadow-soft-md">
            <div className="flex items-center gap-2 mb-4">
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
              <h3 className="font-bold text-gray-900 text-lg">Evidence-Backed Strengths</h3>
            </div>
            <ul className="space-y-3">
              {candidate.explainability.strengths.map((str: string, i: number) => (
                <li key={i} className="flex items-start gap-3 text-gray-700 font-medium">
                  <span className="text-emerald-500 font-black mt-0.5">•</span> {str}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="glass-card p-6 border-l-[6px] border-l-amber-500 shadow-soft-md">
            <div className="flex items-center gap-2 mb-4">
              <AlertOctagon className="w-5 h-5 text-amber-600" />
              <h3 className="font-bold text-gray-900 text-lg">Identified Risks</h3>
            </div>
            <ul className="space-y-3">
              {candidate.explainability.risks.map((risk: string, i: number) => (
                <li key={i} className="flex items-start gap-3 text-gray-700 font-medium">
                  <span className="text-amber-500 font-black mt-0.5">•</span> {risk}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="glass-panel p-6 bg-slate-900 border-none mt-2 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl pointer-events-none"></div>
            <h3 className="font-bold text-slate-400 mb-2 text-xs uppercase tracking-widest">Recruiter Notes</h3>
            <p className="text-white font-medium leading-relaxed">{candidate.explainability.recruiter_notes}</p>
          </div>
          
        </div>
      </div>
    </div>
  );
}

export async function generateStaticParams() {
  const dir = path.join(process.cwd(), "public", "api", "candidates");
  if (!fs.existsSync(dir)) return [];
  const files = fs.readdirSync(dir);
  return files
    .filter((f) => f.endsWith(".json"))
    .map((f) => ({
      id: f.replace(".json", ""),
    }));
}
