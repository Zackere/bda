export default function ({ city, aqi, color }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        background: '#f9f9f9',
        textAlign: 'center',
        justifyContent: 'center',
        padding: '20px',
        alignSelf: 'stretch',
      }}
    >
      <div style={{ fontSize: '25px' }}>{`AQI in ${city.displayName} is:`}</div>
      <div style={{ color: color, fontSize: '30px', fontWeight: 'bold' }}>
        {aqi}
      </div>
    </div>
  );
}
