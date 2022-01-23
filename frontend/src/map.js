import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
} from 'react-simple-maps';

const geoUrl =
  'https://raw.githubusercontent.com/zcreativelabs/react-simple-maps/master/topojson-maps/world-110m.json';

export default function ({ activeCity, setActiveCity, cities }) {
  const geoProps = {
    fill: 'white',
    outline: 'none',
    stroke: 'black',
  };

  return (
    <div
      style={{
        width: '500px',
        height: '400px',
        background: '#86eae9',
        flexShrink: 0,
      }}
    >
      <ComposableMap>
        <Geographies geography={geoUrl}>
          {({ geographies }) =>
            geographies.map(geo => (
              <Geography
                key={geo.rsmKey}
                geography={geo}
                style={{
                  default: geoProps,
                  hover: geoProps,
                  pressed: geoProps,
                }}
              />
            ))
          }
        </Geographies>
        {Object.entries(cities).map(([city, pos]) => {
          return (
            <Marker
              key={city}
              coordinates={[pos.lat, pos.lon]}
              onClick={ev => {
                ev.stopPropagation();
                setActiveCity(city);
              }}
            >
              <g
                fill="none"
                stroke={activeCity === city ? '#13538a' : '#FF5533'}
                strokeLinecap="round"
                strokeLinejoin="round"
                transform={`scale(${
                  2 + (activeCity === city)
                }) translate(-12, -24)`}
                style={{
                  transition: '0.25s',
                }}
              >
                <path
                  d="M12 21.7C17.3 17 20 13 20 10a8 8 0 1 0-16 0c0 3 2.7 6.9 8 11.7z"
                  fill={activeCity === city ? '#13538a' : '#FF5533'}
                />
                <circle cx="12" cy="10" r="5" fill="white" />
              </g>
            </Marker>
          );
        })}
      </ComposableMap>
    </div>
  );
}
