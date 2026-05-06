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

const COLORS = ["#0058be", "#4edea3", "#adc6ff", "#2d3133"];

export function Charts({
  analysis,
  formatMoney,
  labels
}: {
  analysis?: Analysis;
  formatMoney?: (value: number) => string;
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
              <CartesianGrid strokeDasharray="3 3" stroke="#e0e3e5" />
              <XAxis dataKey="period" tickLine={false} axisLine={false} />
              <YAxis tickLine={false} axisLine={false} />
              <Tooltip formatter={(value) => formatMoney ? formatMoney(Number(value)) : value} />
              <Bar dataKey="revenue" fill="#0058be" radius={[4, 4, 0, 0]} />
              <Bar dataKey="profit" fill="#4edea3" radius={[4, 4, 0, 0]} />
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
              <Tooltip formatter={(value) => formatMoney ? formatMoney(Number(value)) : value} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
