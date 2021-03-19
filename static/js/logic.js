var inputLat = ' ';
var inputLng = ' ';
var inputLatLng = [inputLat,inputLng];
console.log(inputLatLng);


/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// FUNCTION buildMap()
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

var myMap;
var markerLayer = L.layerGroup()

function buildMap(inputLatLng) {

  // Define streetmap and darkmap layers
  var streetmap = L.tileLayer("https://api.mapbox.com/styles/v1/mapbox/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}", {
      attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
    tileSize: 512,
    maxZoom: 18,
    zoomOffset: -1,
    id: "dark-v10",
    accessToken: API_KEY
  });
  
  // Define a baseMaps object to hold our base layers
  var baseMaps = {
    "Street Map": streetmap
  };

  // Create our map, giving it the streetmap and earthquakes layers to display on load
  myMap = L.map("map", {
    center: [
      inputLatLng[0], inputLatLng[1]
    ],
    zoom: 11,
    layers: [streetmap] // , earthquakes]
  });

  fetch("./static/data/giantfood_address_geos.json")
  .then(function(response) {
      return response.json();
  })
  .then(function(storesdata) {
    
    console.log(storesdata);    
    console.log(`storesdata is type: ${typeof(storesdata)}`)

    // Extract 6 simple Arrays from the storesdata Object from the JSON file
    var storeAddress = storesdata.street_address;
    console.log(storeAddress)
    var storeCity = storesdata.city;
    console.log(storeCity)
    var storeState = storesdata.state;
    console.log(storeState);
    var storeZip = storesdata.zip_code;
    console.log(storeZip);
    var storeLat = storesdata.lat;
    console.log(storeLat);
    var storeLng = storesdata.lng;
    console.log(storeLng);

    // Reassemble the 6 simple Arrays into a JSON records shape
    var storesdataX = Object.entries(storeAddress).map((address, index) => {
      return {
        street_address: address[1],
        city: storeCity[index],
        state: storeState[index],
        zip: storeZip[index],
        lat: storeLat[index],
        lng: storeLng[index]
      }
    });
    console.log("--- testing storesdataReshape ---");
    console.log(storesdataX)
    console.log(`storesdataX is type: ${typeof(storesdataX)}`)
    
    var markerclusters = L.markerClusterGroup();

    storesdataX.forEach(store => {
            
      var marker = L.circleMarker([store.lat, store.lng], {
        draggable: false
      }).addTo(markerLayer);
      
      marker.bindPopup(
        `<h4><b>Giant Food ${store.city}, ${store.state}</b></h4>
        <hr><br>
        ${store.street_address}<br>
        ${store.city}, ${store.state}  ${store.zip}`
      );

      marker.on('mouseover', function (e) {
        this.openPopup();
      });
      marker.on('mouseout', function (e) {
          this.closePopup();
      });

      markerclusters.addLayer(marker);

    });

    markerclusters.addTo(markerLayer);

  });

  markerLayer.addTo(myMap);

  // Create a layer control
  // Pass in our baseMaps and overlayMaps
  // Add the layer control to the map
  L.control.layers(baseMaps //, overlayMaps // {
    // collapsed: false
  ).addTo(myMap);

};


/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// FUNCTION init()
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
function init() {
  var inputLat = 38.897250;
  var inputLng = -77.004760;
  var inputLatLng = [inputLat,inputLng];
  console.log(inputLatLng);
  console.log(inputLatLng[0]);
  console.log(inputLatLng[1]);

  buildMap(inputLatLng);
};

// Call the init() function to initially load the map

init();


/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// FUNCTION refreshMap()
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

function refreshMap() {

  var slider = d3.select('#distance');
  var distance_mi = slider.node().value;
  var distance_m = distance_mi * 1600;

  var zipfield = d3.select('#zip-field');
  var zip = zipfield.node().value; 

  console.log(zip, distance_m);

  // populate card body

  var cardItem1 = (`ZIPcode: ${zip}`);
  var cardItem2 = (`Radius (mi): ${distance_mi}`);
  
  cardKeysValues = [
    cardItem1,
    cardItem2
  ];

  console.log("--- testing panelKeysValues ---");
  console.log(cardKeysValues);

  var cardBody = d3.select('#chosen-zip-radius');

  cardBody.html('');

  cardKeysValues.forEach(item => {
    cardBody.append("p").text(item);
  }); 


  /////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////
  // d3 URL call with user zipcode returns geocoordinates
  /////////////////////////////////////////////////////////////////////////
  /////////////////////////////////////////////////////////////////////////

  // make API call and pass the zip code to get coords
  url = `/refreshMap?zip=${zip}&radius=${distance_m}`

  d3.json(url).then(data => {
    

    // clear initial layers
    markerLayer.clearLayers();

    console.log("--- data returned from 2nd Google Maps API call ---");
    console.log(data);
    console.log(data[0]['types']);

    var markerclusters = L.markerClusterGroup();

    data.forEach(d => {

      let result;

      var biztypes = d['types'];
      console.log("--- biztypes ---")
      console.log(biztypes)

      if (biztypes.includes('grocery_or_supermarket') === true) {

        lat = d['geometry']['location']['lat'];
        lng = d['geometry']['location']['lng'];
        coords = [lat, lng];
        store_name = d['name'];
        store_address = d['vicinity'];

        marker = L.circleMarker(coords);

        marker.bindPopup(`${store_name}<br/>${store_address}`)

        marker.on('mouseover', function (e) {
          this.openPopup();
        });
        marker.on('mouseout', function (e) {
            this.closePopup();
        });

        markerclusters.addLayer(marker);

      } else {
        console.log("--- location was not a grocery or supermarket ---")
      };

      return result;

    });

    markerclusters.addTo(markerLayer);
    //myMap.addLayer(markerclusters);
  });
  

  // make API call and pass the zip code to get coords
  url2 = `/refreshMapTwo?zip=${zip}`

  d3.json(url2).then(zipgeocoords => {

    console.log("--- zipgeocoords ---");
    console.log(zipgeocoords['results'][0]['geometry']['location']['lat']);
    console.log(zipgeocoords['results'][0]['geometry']['location']['lng']);

    var inputLatR = zipgeocoords['results'][0]['geometry']['location']['lat'];
    var inputLngR = zipgeocoords['results'][0]['geometry']['location']['lng'];
    var inputLatLngR = [inputLatR,inputLngR];

    console.log("--- inputLatLng on the Refresh ---");
    console.log(inputLatLngR);
    console.log(inputLatLngR[0]);
    console.log(inputLatLngR[1]);

    myMap.setView(new L.LatLng(inputLatR, inputLngR), 13);
  
    // buildMap(inputLatLng);

  });


};



/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
// EVENT LISTENERS
/////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////

// Identify web elements on the page
zipfield = d3.select('#zip-field');
zipbtn = d3.select('#zip-btn');


// Add event listeners to the web elements
// zipfield.on('change', refreshMap);
zipbtn.on('click', refreshMap);

