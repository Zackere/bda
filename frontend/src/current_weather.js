import React from 'react';
import ReactWeather, { useOpenWeather } from 'react-open-weather';

export default function ({ city }) {
  const { data, errorMessage } = useOpenWeather({
    key: '2e60ac296b6e007baf4cda66380be86c',
    lon: city.lat, // Dunno why
    lat: city.lon,
    lang: 'en',
    unit: 'metric',
  });
  return (
    <div>
      <ReactWeather
        isLoading={false}
        errorMessage={errorMessage}
        data={data}
        lang="en"
        locationLabel={city.displayName}
        unitsLabels={{ temperature: '°C', windSpeed: 'Km/h' }}
        showForecast={true}
      />
    </div>
  );
}
