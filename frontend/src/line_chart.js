import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';
const maxNumPoints = 50;

export default function ({ data, x, y, title }) {
  if (data.length > maxNumPoints) {
    const indices = [...Array(maxNumPoints).keys()].map(i =>
      Math.floor((i / maxNumPoints) * data.length),
    );
    data = indices.map(i => data[i]);
  }
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
          isAnimationActive={false}
          type="monotone"
          dataKey={y}
          stroke="#8884d8"
        />
      </LineChart>
    </div>
  );
}
