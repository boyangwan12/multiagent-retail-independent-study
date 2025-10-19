import { LineChart, Line, ResponsiveContainer } from 'recharts';
import type { AgentContribution as AgentContributionType } from '../../types/performance';

interface AgentContributionProps {
  data: AgentContributionType[];
}

const Sparkline = ({ data, color }: { data: number[]; color: string }) => {
  const chartData = data.map((value, index) => ({ value, index }));

  return (
    <div className="w-16 h-8">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export const AgentContribution = ({ data }: AgentContributionProps) => {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wide mb-3">
        Agent Contributions
      </h3>

      {data.map((agent, index) => (
        <div key={index} className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: agent.color }}
              />
              <span className="text-sm text-text-primary font-medium">
                {agent.name}
              </span>
            </div>

            <div className="flex items-center gap-3">
              <Sparkline data={agent.trend} color={agent.color} />
              <span className="font-mono text-lg font-semibold text-text-primary min-w-[3rem] text-right">
                {agent.percentage}%
              </span>
            </div>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-[#2A2A2A] rounded-full h-2 overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${agent.percentage}%`,
                backgroundColor: agent.color,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};
