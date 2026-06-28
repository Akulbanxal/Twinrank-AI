import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import { Layers } from "lucide-react";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter", display: 'swap' });
const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit", display: 'swap' });

export const metadata: Metadata = {
  title: "TwinRank AI | Premium Recruiter Dashboard",
  description: "World-class AI recruitment platform optimizing NDCG.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${outfit.variable} min-h-screen text-slate-900 font-sans selection:bg-lavender-200 selection:text-lavender-900 pb-20 overflow-x-hidden relative`}>
        
        {/* Static Performant Abstract Background */}
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none bg-[#fafafa]">
          <div className="absolute top-[-15%] left-[-10%] w-[50vw] h-[50vw] rounded-full" style={{ background: 'radial-gradient(circle, rgba(196,181,253,0.2) 0%, rgba(196,181,253,0) 70%)' }}></div>
          <div className="absolute top-[20%] right-[-15%] w-[45vw] h-[45vw] rounded-full" style={{ background: 'radial-gradient(circle, rgba(191,219,254,0.3) 0%, rgba(191,219,254,0) 70%)' }}></div>
          <div className="absolute bottom-[-10%] left-[20%] w-[60vw] h-[60vw] rounded-full" style={{ background: 'radial-gradient(circle, rgba(224,231,255,0.5) 0%, rgba(224,231,255,0) 70%)' }}></div>
        </div>

        <header className="sticky top-0 z-50 w-full backdrop-blur-2xl bg-white/40 border-b border-white/40 shadow-soft-sm">
          <div className="max-w-7xl mx-auto px-6 h-[72px] flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3 group">
              <div className="bg-gradient-to-br from-lavender-500 to-indigo-600 text-white p-2 rounded-xl shadow-glow group-hover:scale-105 transition-all duration-300 ease-out">
                <Layers className="w-5 h-5" strokeWidth={2.5} />
              </div>
              <span className="font-extrabold tracking-tight text-xl font-heading text-slate-800">TwinRank<span className="text-lavender-600">.ai</span></span>
            </Link>
            
            <nav className="flex items-center gap-8">
              <Link href="/" className="text-sm font-semibold text-slate-500 hover:text-slate-900 transition-colors">Dashboard</Link>
              <Link href="/explorer" className="text-sm font-semibold text-slate-500 hover:text-slate-900 transition-colors">Explorer</Link>
              <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-lavender-300 to-indigo-500 shadow-soft-md border-[2px] border-white cursor-pointer hover:shadow-glow transition-all" />
            </nav>
          </div>
        </header>
        
        <main className="max-w-7xl mx-auto px-6 mt-12 relative z-10">
          {children}
        </main>
      </body>
    </html>
  );
}
