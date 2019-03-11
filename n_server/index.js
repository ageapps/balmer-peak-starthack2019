var mqtt = require('mqtt')
const Influx = require('influx')
const os = require('os')


const MQTT_SERVER = "82.165.25.152"
const MQTT_PORT = 1884
const DATABASE_NAME = "starthack"
const SIGNALS = [
  '/signal/ESP_v_Signal/#',
  '/signal/ESP_Laengsbeschl/#',
  '/signal/ESP_Querbeschleinigung/#',
  '/signal/ESP_Bremsdruck/#',
  '/signal/ESP_Gierrate/#',
  '/signal/MO_Fahrpedalrohwert_01/#',
]
var client  = mqtt.connect("mqtt://"+MQTT_SERVER + ":" + MQTT_PORT )
var cache = {}

const influx = new Influx.InfluxDB({
  host: 'localhost',
  database: DATABASE_NAME,
  schema: [
    {
      measurement: 'signals',
      fields: {
        value: Influx.FieldType.INTEGER,
        utc: Influx.FieldType.STRING
      },
      tags: [
        'key'
      ]
    }
  ]
})

client.on('connect', function () {
  client.subscribe(SIGNALS, function (err) {
    if (!err) {
      console.log("Connected")
    }
  })
})
 

influx.getDatabaseNames()
  .then(names => {
    if (!names.includes(DATABASE_NAME)) {
      return influx.createDatabase(DATABASE_NAME);
    }
  })
  .then(() => {
    console.error(`Database Ready`);
    client.on('message', function (topic, message) {
      var msg = JSON.parse(message.toString())
      // message is Buffer
      // console.log(date.toString())
      timestamp = BigInt(msg.utc)
      if (cache[topic]){
        if ((timestamp - cache[topic]) > 100000000) {
          // console.log(topic + " " + msg.utc)
          cache[topic] = timestamp
          influx.writePoints([
              {
                measurement: 'signals',
                tags: { 
                  key: topic,
                },
                fields: { 
                  value: parseInt(msg.value),
                  utc: msg.utc
                },
              }
            ]).catch(err => {
              console.error(`Error saving data to InfluxDB! ${err.stack}`)
            })
            if (topic === "/signal/ESP_v_Signal"){
              var category = 0
              if (parseInt(msg.value) > 20) {
                if (parseInt(msg.value) > 40){
                  category = 2
                } else{
                  category = 1
                }
              } 
              influx.writePoints([
                {
                  measurement: 'signals',
                  tags: { 
                    key: 'category',
                  },
                  fields: { 
                    value: category,
                    utc: msg.utc
                  },
                }
              ]).catch(err => {
                console.error(`Error saving data to InfluxDB! ${err.stack}`)
              })
            }
        }
      } else {
        cache[topic] = timestamp
      }
    
    });
  })
  .catch(err => {
    console.error(`Error creating Influx database!`);
  })
