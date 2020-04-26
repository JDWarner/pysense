class DataPoint:

    __slots__ = ['timestamp', 'temp_mp', 'temp_si', 'humidity', 
                 'pressure', 'altitude', 'dewpoint', 'light']

    def __init__(self, **kwargs):
        required = list(self.__slots__)
        for key, value in kwargs.items():
            setattr(self, key, value)
            required.remove(key)
        if len(required) > 0:
            raise ValueError("Not enough values passed! Missing: {}".format(required))

    def to_thingspeak(self):
        return 'field1={}&field2={}&field3={}&field4={}&field5={}&field6={}&field7={}'.format(
            self.temp_mp, 
            self.temp_si, 
            self.humidity, 
            self.pressure, 
            self.altitude, 
            self.dewpoint,
            self.light,
            )

    @classmethod
    def mean(cls, datapoints):
        mean_pm10 = 0
        mean_pm25 = 0
        mean_temperature = 0
        mean_humidity = 0
        mean_duration = 0
        valid_temp_datapoints = 0

        for d in datapoints:
            mean_pm10 += d.pm10
            mean_pm25 += d.pm25
            mean_duration += d.duration
            if d.temperature is not -1:
                mean_temperature += d.temperature
                mean_humidity += d.humidity
                valid_temp_datapoints += 1

        return cls(
            pm10 = mean_pm10/len(datapoints),
            pm25 = mean_pm25/len(datapoints),
            temperature = -1 if valid_temp_datapoints == 0 else mean_temperature/valid_temp_datapoints,
            humidity = -1 if valid_temp_datapoints == 0 else mean_humidity/valid_temp_datapoints,
            duration = mean_duration/len(datapoints),
            voltage = datapoints[-1].voltage,
            version = datapoints[-1].version,
            timestamp = datapoints[-1].timestamp
        )
