import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { QuarterlyData } from '../../types/performance';

interface HistoricalChartProps {
  data: QuarterlyData[];
}

export const HistoricalChart = ({ data }: HistoricalChartProps) => {
  return (
    <div className="w-full h-[200px]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorMape" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#5B8DEF" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#5B8DEF" stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#2A2A2A" />

          <XAxis
            dataKey="quarter"
            stroke="#6B7280"
            style={{ fontSize: '12px' }}
          />

          <YAxis
            stroke="#6B7280"
            style={{ fontSize: '12px' }}
            domain={[0, 25]}
            ticks={[0, 5, 10, 15, 20, 25]}
            label={{
              value: 'MAPE %',
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: '12px', fill: '#6B7280' },
            }}
          />

          <Tooltip
            contentStyle={{
              backgroundColor: '#1A1A1A',
              border: '1px solid #2A2A2A',
              borderRadius: '6px',
              color: '#FFFFFF',
            }}
            labelStyle={{ color: '#9CA3AF' }}
          />

          {/* Target line at 20% */}
          <ReferenceLine
            y={20}
            stroke="#F5A623"
            strokeDasharray="3 3"
            label={{
              value: 'Target: 20%',
              position: 'right',
              fill: '#F5A623',
              fontSize: 12,
            }}
          />

          <Area
            type="monotone"
            dataKey="mape"
            stroke="#5B8DEF"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorMape)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
