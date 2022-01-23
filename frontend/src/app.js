import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import Button from 'react-bootstrap/Button';
import Spinner from 'react-bootstrap/Spinner';

import Weather from './current_weather';
import Map from './map';
import ShortStat from './short_stat';
import CurrentPollution from './current_pollution';
import { fetchAggregates } from './fetch_aggregates';
import LineChart from './line_chart';

const availableCities = {
  delhi: {
    lon: 28.63576,
    lat: 77.22445,
    displayName: 'New Delhi',
  },
  warsaw: { lon: 52.22517, lat: 21.014784, displayName: 'Warsaw' },
  berlin: { lon: 52.520008, lat: 13.404954, displayName: 'Berlin' },
  moscow: { lon: 55.759354, lat: 37.595585, displayName: 'Moscow' },
};

const data = {
  delhi: {
    aqi: 298,
    modelAccuracy: 37,
  },
  warsaw: {
    aqi: 125,
    modelAccuracy: 25,
  },
  berlin: {
    aqi: 14,
    modelAccuracy: 67,
  },
  moscow: {
    aqi: 176,
    modelAccuracy: 99,
  },
};

const modelAccuracyColor = val => {
  return `hsl(${Math.floor((val / 100) * 120)},${100 - val / 2}%, 50%)`;
};
const airStatusColor = val => {
  if (val <= 50 || val === 'Good') return '#009966';
  if (val <= 100 || val === 'Moderate') return '#ffde33';
  if (val <= 150 || val === 'Unhealthy for S.G') return '#ff9933';
  if (val <= 200 || val === 'Unhealthy') return '#cc0033';
  if (val <= 300 || val === 'Very Unhealthy') return '#660099';
  return '#7e0023';
};
const aqiCategory = val => {
  if (val <= 50) return 'Good';
  if (val <= 100) return 'Moderate';
  if (val <= 150) return 'Unhealthy for S.G';
  if (val <= 200) return 'Unhealthy';
  if (val <= 300) return 'Very Unhealthy';
  return 'Hazardous';
};

export default function () {
  const [showWeather, setShowWeather] = React.useState(false);
  const [showPollution, setShowPollution] = React.useState(false);
  const [activeCity, setActiveCity] = React.useReducer(
    (oldActiveCity, newActiveCity) => {
      if (oldActiveCity !== newActiveCity) {
        setShowWeather(false);
        setShowPollution(false);
      }
      return newActiveCity;
    },
    Object.keys(availableCities)[0],
  );
  const [pollutionAggregates, setPollutionAggregates] = React.useState();
  const [weatherAggregates, setWeatherAggregates] = React.useState();
  const [newestPollution, setNewestPollution] = React.useState();
  React.useEffect(() => {
    fetchAggregates(activeCity, 'pollution').then(setPollutionAggregates);
    fetchAggregates(activeCity, 'weather').then(setWeatherAggregates);
    fetch(
      `https://api.waqi.info/feed/geo:${availableCities[activeCity].lon};${availableCities[activeCity].lat}/?token=1d9e5a0caf47598601455f82453f22990f088d82`,
    )
      .then(res => res.json())
      .then(d => {
        setNewestPollution(d.data.aqi);
      });
  }, [activeCity]);
  console.log(pollutionAggregates, weatherAggregates);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', rowGap: '20px' }}>
      <div
        style={{
          background: '#f9f9f9',
          padding: '40px 5px',
          textAlign: 'center',
          fontSize: '40px',
          fontWeight: 'bold',
        }}
      >
        <span>
          AIR POLLUTION FORECAST BASED ON WEATHER CONDITIONS IN:&nbsp;
        </span>
        <span style={{ color: '#13538a' }}>
          {availableCities[activeCity].displayName}
        </span>
      </div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-around',
          textAlign: 'center',
          flexWrap: 'wrap',
          columnGap: '20px',
          rowGap: '20px',
        }}
      >
        {pollutionAggregates ? (
          <ShortStat
            color={airStatusColor(pollutionAggregates[0].avgaqi)}
            title="Air Status"
            value={`${pollutionAggregates[0].avgaqi} (${aqiCategory(
              pollutionAggregates[0].avgaqi,
            )})`}
            fillPercentage={
              (Math.min(pollutionAggregates[0].avgaqi, 300) / 300) * 100
            }
          />
        ) : (
          <div
            style={{
              flexGrow: 1,
              flex: '1 1 0px',
              background: '#f9f9f9',
              display: 'flex',
            }}
          >
            <Spinner
              animation="border"
              variant="primary"
              style={{ margin: 'auto' }}
            />
          </div>
        )}
        <ShortStat
          color={modelAccuracyColor(data[activeCity].modelAccuracy)}
          title="Predictions Accuracy"
          value={`${data[activeCity].modelAccuracy}%`}
          fillPercentage={data[activeCity].modelAccuracy}
        />
      </div>
      <div
        style={{
          display: 'flex',
          columnGap: '20px',
          rowGap: '20px',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
      >
        <Map
          activeCity={activeCity}
          setActiveCity={setActiveCity}
          cities={availableCities}
        />
        {!showPollution ? (
          <Button
            variant="primary"
            style={{
              alignSelf: 'center',
              whiteSpace: 'normal',
              maxWidth: '200px',
            }}
            onClick={() => setShowPollution(true)}
          >{`Fetch pollution for ${availableCities[activeCity].displayName} from AQICN API`}</Button>
        ) : (
          <CurrentPollution
            city={availableCities[activeCity]}
            aqi={`${newestPollution} (${aqiCategory(newestPollution)})`}
            color={airStatusColor(newestPollution)}
          />
        )}
        {showWeather ? (
          <Weather city={availableCities[activeCity]} />
        ) : (
          <Button
            variant="primary"
            style={{
              alignSelf: 'center',
              whiteSpace: 'normal',
              maxWidth: '200px',
            }}
            onClick={() => setShowWeather(true)}
          >
            {`Fetch weather for ${availableCities[activeCity].displayName} from Openweathermap API`}
          </Button>
        )}
        {pollutionAggregates ? (
          <LineChart
            data={pollutionAggregates.map(p => ({
              date: new Date(p.date * 1_000).toLocaleDateString(),
              aqi: Math.round(p.avgaqi),
            }))}
            x="date"
            y="aqi"
            title={`Historical daily pollution for ${availableCities[activeCity].displayName}`}
          />
        ) : (
          <div
            style={{
              width: '500px',
              height: '500px',
              display: 'flex',
            }}
          >
            <Spinner
              animation="border"
              variant="primary"
              style={{ margin: 'auto' }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
