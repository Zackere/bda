import dateFormat from 'dateformat';
import express from 'express';
import { readFileSync } from 'fs';
import { v4 as uuid } from 'uuid';

const app = express();

const all_data = {};
const aggregates = {};

['delhi', 'berlin', 'warsaw', 'moscow'].forEach(city => {
  ['weather', 'pollution'].forEach(category => {
    const buf = readFileSync(`data/${category}/${city}.json`);
    const ret = JSON.parse(buf.toString());
    ret.sort((a, b) => a.measured - b.measured);
    ret.forEach((v, i) => {
      v.ts = dateFormat(new Date(v.measured * 1000), 'yyyy-mm-dd hh:MM:ss.l');
      v.id = uuid();
    });

    all_data[category + city] = JSON.parse(JSON.stringify(ret));
    all_data[category + city].forEach(v => (v.kafkatopic = category + city));

    aggregates[category + city] = [];
    Object.entries(
      ret
        .map(v => {
          v.date = new Date(v.measured * 1000);
          v.date.setHours(0, 0, 0, 0);
          return v;
        })
        .reduce((dict, v) => {
          (dict[v.date] = dict[v.date] || []).push(v);
          return dict;
        }, {}),
    ).forEach(([date, values]) => {
      const length = values.length;
      switch (category) {
        case 'weather':
          const temps = values.map(x => x.temp);
          const pressures = values.map(x => x.pressure);
          const humidities = values.map(x => x.humidity);
          const clouds = values.map(x => x.clouds);
          const windspeeds = values.map(x => x.windspeed);
          const winddegs = values.map(x => x.winddeg);
          aggregates[category + city].push({
            mintemp: Math.min(...temps),
            maxtemp: Math.max(...temps),
            avgtemp: temps.reduce((a, b) => a + b, 0) / length,
            minpressure: Math.min(...pressures),
            maxpressure: Math.max(...pressures),
            avgpressure: pressures.reduce((a, b) => a + b, 0) / length,
            minhumidity: Math.min(...humidities),
            maxhumidity: Math.max(...humidities),
            avghumidity: humidities.reduce((a, b) => a + b, 0) / length,
            minclouds: Math.min(...clouds),
            maxclouds: Math.max(...clouds),
            avgclouds: clouds.reduce((a, b) => a + b, 0) / length,
            minwindspeed: Math.min(...windspeeds),
            maxwindspeed: Math.max(...windspeeds),
            avgwindspeed: windspeeds.reduce((a, b) => a + b, 0) / length,
            minwinddeg: Math.min(...winddegs),
            maxwinddeg: Math.max(...winddegs),
            avgwinddeg: winddegs.reduce((a, b) => a + b, 0) / length,
            date: +new Date(date) / 1000,
          });
          break;
        case 'pollution':
          const aqis = values.map(x => x.aqi);
          aggregates[category + city].push({
            minaqi: Math.min(...aqis),
            maxaqi: Math.max(...aqis),
            avgaqi: aqis.reduce((a, b) => a + b, 0) / length,
            date: +new Date(date) / 1000,
          });
          break;
      }
    });

    app.get(`/${category}${city}`, (req, res) => res.json(ret));
  });
});

const all_data_reduced_and_sorted = Object.values(all_data).reduce(
  (p, c) => (p.push(...c), p),
  [],
);
all_data_reduced_and_sorted.sort((a, b) => a.measured - b.measured);
for (const [key, values] of Object.entries(aggregates)) {
  values.sort((a, b) => a.date - b.date);
  app.get(`/${key}aggregations`, (_, res) => res.json(values));
}
app.get('/all', (req, res) => res.json(all_data_reduced_and_sorted));

app.listen(80);
