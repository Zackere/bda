export default function ({ city, aqi, color }) {
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontSize: '25px' }}>{`AQI in ${city.displayName} is:`}</div>
      <div style={{ color: color, fontSize: '30px', fontWeight: 'bold' }}>
        {aqi}
      </div>
    </div>
  );
}
