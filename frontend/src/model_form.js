// ['windspeed', 'humidity', 'temp', 'lon', 'pressure', 'winddeg', 'lat', 'clouds']
import React from 'react';
import Button from 'react-bootstrap/Button';

export default function ({
  windspeed,
  humidity,
  temp,
  lon,
  pressure,
  winddeg,
  lat,
  clouds,
  activeCity,
}) {
  const [state, setState] = React.useState({
    windspeed,
    humidity,
    temp,
    lon,
    pressure,
    winddeg,
    lat,
    clouds,
  });
  const [prediction, setPrediction] = React.useState();
  let abortController = new AbortController();
  function fetchPredictions() {
    abortController.abort();
    abortController = new AbortController();
    fetch('http://localhost:4444/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(state),
      signal: abortController.signal,
    })
      .then(r => r.json())
      .then(setPrediction);
  }
  React.useEffect(() => {
    fetchPredictions();
  }, [activeCity]);
  console.log(prediction);
  return (
    <div style={{ display: 'flex', alignItems: 'center', columnGap: '10px' }}>
      <div style={{ display: 'flex', flexDirection: 'column', rowGap: '10px' }}>
        <label style={{ display: 'flex', justifyContent: 'space-between' }}>
          Windspeed
          <input
            type="number"
            defaultValue={state.windspeed}
            onChange={evt =>
              setState({ ...state, windspeed: +evt.target.value })
            }
            style={{ marginLeft: '10px' }}
          ></input>
        </label>
        <label style={{ display: 'flex', justifyContent: 'space-between' }}>
          Humidity
          <input
            type="number"
            defaultValue={state.humidity}
            onChange={evt =>
              setState({ ...state, humidity: +evt.target.value })
            }
            style={{ marginLeft: '10px' }}
          ></input>
        </label>
        <label style={{ display: 'flex', justifyContent: 'space-between' }}>
          Temperature
          <input
            type="number"
            defaultValue={state.temp}
            onChange={evt => setState({ ...state, temp: +evt.target.value })}
            style={{ marginLeft: '10px' }}
          ></input>
        </label>
        <label style={{ display: 'flex', justifyContent: 'space-between' }}>
          Longitude
          <input
            type="number"
            defaultValue={state.lon}
            onChange={evt => setState({ ...state, lon: +evt.target.value })}
            style={{ marginLeft: '10px' }}
          ></input>
        </label>
        <label style={{ display: 'flex', justifyContent: 'space-between' }}>
          Latitude
          <input
            type="number"
            defaultValue={state.lat}
            onChange={evt => setState({ ...state, lat: +evt.target.value })}
            style={{ marginLeft: '10px' }}
          ></input>
        </label>
        <label style={{ display: 'flex', justifyContent: 'space-between' }}>
          Pressure
          <input
            type="number"
            defaultValue={state.pressure}
            onChange={evt =>
              setState({ ...state, pressure: +evt.target.value })
            }
            style={{ marginLeft: '10px' }}
          ></input>
        </label>
        <label style={{ display: 'flex', justifyContent: 'space-between' }}>
          Winddeg
          <input
            type="number"
            defaultValue={state.winddeg}
            onChange={evt => setState({ ...state, winddeg: +evt.target.value })}
            style={{ marginLeft: '10px' }}
          ></input>
        </label>
        <label style={{ display: 'flex', justifyContent: 'space-between' }}>
          Clouds
          <input
            type="number"
            defaultValue={state.clouds}
            onChange={evt => setState({ ...state, clouds: +evt.target.value })}
            style={{ marginLeft: '10px' }}
          ></input>
        </label>
        <Button
          variant="primary"
          onClick={() => {
            fetchPredictions();
          }}
        >
          Predict!
        </Button>
      </div>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          textAlign: 'center',
        }}
      >
        <div>Predicted Air Status</div>
        <div>
          {prediction
            ? `${prediction.prediction} (${Math.round(
                prediction.probability.values[prediction.prediction] * 100,
              )}%)`
            : '??? (???)'}
        </div>
      </div>
    </div>
  );
}
