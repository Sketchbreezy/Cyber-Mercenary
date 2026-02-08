import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

interface ChartProps {
  data: any[];
  height?: number;
}

const COLORS = ['#00f0ff', '#7000ff', '#00ff88', '#ffaa00', '#ff003c'];

export function AreaChartComponent({ data, height = 300 }: ChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="colorPrimary" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#00f0ff" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#00f0ff" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
        <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
        <YAxis stroke="#6b7280" fontSize={12} />
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(18, 18, 26, 0.9)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '8px',
            backdropFilter: 'blur(10px)',
          }}
          labelStyle={{ color: '#fff' }}
        />
        <Area
          type="monotone"
          dataKey="value"
          stroke="#00f0ff"
          strokeWidth={2}
          fillOpacity={1}
          fill="url(#colorPrimary)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function BarChartComponent({ data, height = 300 }: ChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
        <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
        <YAxis stroke="#6b7280" fontSize={12} />
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(18, 18, 26, 0.9)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '8px',
          }}
        />
        <Bar dataKey="value" radius={[4, 4, 0, 0]}>
          {data.map((_, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export function LineChartComponent({ data, height = 300 }: ChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
        <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
        <YAxis stroke="#6b7280" fontSize={12} />
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(18, 18, 26, 0.9)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '8px',
          }}
        />
        <Line
          type="monotone"
          dataKey="value"
          stroke="#00f0ff"
          strokeWidth={2}
          dot={{ fill: '#00f0ff', strokeWidth: 2 }}
          activeDot={{ r: 6, fill: '#00f0ff' }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function PieChartComponent({ data, height = 300 }: ChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={5}
          dataKey="value"
        >
          {data.map((_, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(18, 18, 26, 0.9)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '8px',
          }}
        />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

interface StatsChartProps {
  data: { label: string; value: number; change?: number }[];
}

export function StatsChart({ data }: StatsChartProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {data.map((stat, index) => (
        <div key={index} className="glass-panel p-4 text-center">
          <p className="text-2xl font-bold text-white">{stat.value.toLocaleString()}</p>
          <p className="text-sm text-text-muted mt-1">{stat.label}</p>
          {stat.change !== undefined && (
            <p className={`text-xs mt-2 ${stat.change >= 0 ? 'text-success' : 'text-accent'}`}>
              {stat.change >= 0 ? '+' : ''}{stat.change}%
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
