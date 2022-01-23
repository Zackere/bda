export async function fetchAggregates(city, category) {
  const data = await (
    await fetch(`http://localhost:7642/?db=${category}${city}`)
  ).json();
  return data;
}
