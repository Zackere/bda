import dateFormat from 'dateformat';
import express from 'express';
import { readFileSync } from 'fs';
import { v4 as uuid } from 'uuid';

const app = express();

const all_data = {};

['delhi', 'berlin', 'warsaw', 'moscow'].forEach(city => {
  ['weather', 'pollution'].forEach(category => {
    const buf = readFileSync(`data/${category}/${city}.json`);
    const now = +new Date();
    const ret = JSON.parse(buf.toString());
    ret.sort((a, b) => a.measured - b.measured);
    ret.forEach((v, i) => {
      v.ts = dateFormat(new Date(now + i * 1000), 'yyyy-mm-dd hh:MM:ss.l');
      v.id = uuid();
    });

    all_data[category + city] = JSON.parse(JSON.stringify(ret));
    all_data[category + city].forEach(v => (v.kafkatopic = category + city));

    app.get(`/${category}${city}`, (req, res) => res.json(ret));
  });
});

const all_data_reduced_and_sorted = Object.values(all_data).reduce((p, c) => (p.push(...c), p), []);
all_data_reduced_and_sorted.sort((a, b) => a.measured - b.measured);
app.get('/all', (req, res) => res.json(all_data_reduced_and_sorted));

app.listen(80);
