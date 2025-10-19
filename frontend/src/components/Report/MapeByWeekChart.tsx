import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface MapeByWeekChartProps {
  data: Array<{
    week: number;
    mape: number;
    target: number;
  }>;
}

export function MapeByWeekChart({ data }: MapeByWeekChartProps) {
  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <p className="text-text-secondary text-sm mb-4">
        Mean Absolute Percentage Error (MAPE) by week. Target: &lt;20%
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2A2A2A" />
          <XAxis
            dataKey="week"
            stroke="#9CA3AF"
            tick={{ fill: '#9CA3AF' }}
            label={{ value: 'Week', position: 'insideBottom', offset: -5, fill: '#9CA3AF' }}
          />
          <YAxis
            stroke="#9CA3AF"
            tick={{ fill: '#9CA3AF' }}
            label={{ value: 'MAPE (%)', angle: -90, position: 'insideLeft', fill: '#9CA3AF' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1A1A1A',
              border: '1px solid #2A2A2A',
              borderRadius: '6px',
              color: '#FFFFFF',
            }}
            formatter={(value: number) => [`${value.toFixed(1)}%`, 'MAPE']}
            labelFormatter={(label) => `Week ${label}`}
          />
          <Legend
            wrapperStyle={{ color: '#9CA3AF' }}
            formatter={(value) => (
              <span className="text-text-secondary">
                {value === 'mape' ? 'Actual MAPE' : 'Target'}
              </span>
            )}
          />
          <ReferenceLine
            y={20}
            stroke="#F5A623"
            strokeDasharray="3 3"
            label={{ value: 'Target (20%)', fill: '#F5A623', position: 'right' }}
          />
          <Line
            type="monotone"
            dataKey="mape"
            stroke="#5E6AD2"
            strokeWidth={2}
            dot={{ fill: '#5E6AD2', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>

      {/* Summary Stats */}
      <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-border">
        <div>
          <p className="text-text-secondary text-xs mb-1">Average MAPE</p>
          <p className="text-text-primary text-lg font-mono">
            {(data.reduce((sum, d) => sum + d.mape, 0) / data.length).toFixed(1)}%
          </p>
        </div>
        <div>
          <p className="text-text-secondary text-xs mb-1">Best Week</p>
          <p className="text-text-primary text-lg font-mono">
            Week {data.reduce((min, d) => (d.mape < min.mape ? d : min)).week}
          </p>
        </div>
        <div>
          <p className="text-text-secondary text-xs mb-1">Worst Week</p>
          <p className="text-text-primary text-lg font-mono">
            Week {data.reduce((max, d) => (d.mape > max.mape ? d : max)).week}
          </p>
        </div>
      </div>
    </div>
  );
}
