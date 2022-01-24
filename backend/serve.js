import express from 'express';
import cors from 'cors';
import { MongoClient } from 'mongodb';
const app = express();

app.get('/', cors(), async (req, res) => {
  const client = new MongoClient('mongodb://mongo-db:27017');
  await client.connect();
  const db = client.db('aggregations');
  const ret = await db
    .collection(req.query.db)
    .find()
    .sort({ date: 1 })
    .toArray();
  await client.close();
  res.json(ret);
});

app.listen(80);
