"use client";

import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart as RechartsRadar, ResponsiveContainer, Tooltip } from "recharts";

interface Props {
  data: {
    capability: number;
    growth: number;
    behavior: number;
    trust: number;
    market: number;
  };
}

export function CandidateRadarChart({ data }: Props) {
  const chartData = [
    { subject: 'Capability', A: data.capability * 100, fullMark: 100 },
    { subject: 'Growth', A: data.growth * 100, fullMark: 100 },
    { subject: 'Behavior', A: data.behavior * 100, fullMark: 100 },
    { subject: 'Trust', A: data.trust * 100, fullMark: 100 },
    { subject: 'Market', A: data.market * 100, fullMark: 100 },
  ];

  return (
    <div className="w-full h-72 glass-card p-6 flex flex-col">
      <h3 className="text-sm font-semibold text-gray-900 mb-2">Dimension Analysis</h3>
      <div className="flex-grow">
        <ResponsiveContainer width="100%" height="100%">
          <RechartsRadar cx="50%" cy="50%" outerRadius="75%" data={chartData}>
            <PolarGrid stroke="#f3f4f6" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#6b7280', fontSize: 11, fontWeight: 500 }} />
            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
            <Radar 
              name="Score" 
              dataKey="A" 
              stroke="#8b5cf6" 
              strokeWidth={2}
              fill="#a78bfa" 
              fillOpacity={0.35} 
            />
            <Tooltip 
              contentStyle={{ 
                borderRadius: '12px', 
                border: '1px solid rgba(255,255,255,0.5)', 
                boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)',
                backdropFilter: 'blur(10px)',
                backgroundColor: 'rgba(255,255,255,0.9)'
              }}
              itemStyle={{ color: '#6d28d9', fontWeight: 600 }}
            />
          </RechartsRadar>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
