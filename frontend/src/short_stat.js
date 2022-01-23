export default function ({ color, value, title, fillPercentage }) {
  return (
    <div
      style={{
        flexGrow: 1,
        flex: '1 1 0px',
        minWidth: '500px',
        background: '#f9f9f9',
      }}
    >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          padding: '20px 20px 20px 20px',
          rowGap: '20px',
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            columnGap: '20px',
          }}
        >
          <div style={{ margin: 'auto 0', fontSize: '25px' }}>{title}</div>
          <div style={{ color: color, fontSize: '30px', fontWeight: 'bold' }}>
            {value}
          </div>
        </div>
        <div
          style={{
            width: '100%',
            height: '5px',
            background: '#e3e3e3',
            borderRadius: '5px',
          }}
        ></div>
        <div
          style={{
            width: `${fillPercentage}%`,
            height: '5px',
            background: color,
            borderRadius: '5px',
            marginTop: '-25px',
            transition: '0.25s',
          }}
        ></div>
      </div>
    </div>
  );
}
