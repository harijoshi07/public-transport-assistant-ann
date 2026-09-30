const provider = new window.GeoSearch.OpenStreetMapProvider();
const search = new GeoSearch.GeoSearchControl({
  provider: provider,
  style: 'bar',
  updateMap: true,
  autoClose: true,
}); 
