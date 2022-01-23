import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';

export default function ({ data, x, y, title }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        textAlign: 'center',
        background: '#f9f9f9',
      }}
    >
      <div>{title}</div>
      <LineChart data={data} width={500} height={500}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={x} />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line
          isAnimationActive={true}
          type="monotone"
          dataKey={y}
          stroke="#8884d8"
          activeDot={{ r: 8 }}
        />
      </LineChart>
    </div>
  );
}
