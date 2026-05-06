"use client";

import type { Analysis } from "@/lib/api";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

const COLORS = ["#227c5c", "#c97b3a", "#5d7a99", "#9b4a4a"];

export function Charts({
  analysis,
  labels
}: {
  analysis?: Analysis;
  labels?: {
    revenueProfit: string;
    costBreakdown: string;
  };
}) {
  return (
    <div className="grid charts">
      <div className="panel">
        <div className="panel-header">
          <h2>{labels?.revenueProfit || "Revenue and Profit"}</h2>
        </div>
        <div className="chart-box">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={analysis?.revenue_trends || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#d9e1dd" />
              <XAxis dataKey="period" tickLine={false} axisLine={false} />
              <YAxis tickLine={false} axisLine={false} />
              <Tooltip />
              <Bar dataKey="revenue" fill="#227c5c" radius={[5, 5, 0, 0]} />
              <Bar dataKey="profit" fill="#c97b3a" radius={[5, 5, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="panel">
        <div className="panel-header">
          <h2>{labels?.costBreakdown || "Cost Breakdown"}</h2>
        </div>
        <div className="chart-box">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={analysis?.cost_breakdown || []}
                dataKey="value"
                nameKey="name"
                outerRadius={92}
                innerRadius={52}
                paddingAngle={3}
              >
                {(analysis?.cost_breakdown || []).map((entry, index) => (
                  <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
