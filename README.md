# Meteo.lt Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

This is a custom component to integrate [Meteo.lt](https://www.meteo.lt/) weather service into Home Assistant.

## Features

- Weather forecast data for Lithuanian cities and towns
- Meteorological station observations
- Hydrological station data
- Automatic location detection based on Home Assistant location
- All data is converted to local timezone (Europe/Vilnius)

## Installation

### HACS (Recommended)

1. Open HACS
2. Go to "Integrations"
3. Click the three dots in top right
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" category
6. Click "Add"
7. Find "Meteo.lt" in integrations list and click "Download"
8. Restart Home Assistant

### Manual Installation

1. Clone this repository
2. Copy the `custom_components/meteolt` folder to your Home Assistant `/config/custom_components` folder
3. Restart Home Assistant

## Configuration

1. Go to Configuration -> Integrations
2. Click "+ Add Integration"
3. Search for "Meteo.lt"
4. Select your location and optionally meteorological and hydrological stations
5. Click "Submit"

## Available Sensors

### Weather Forecast

- Temperature
- Feels Like Temperature
- Wind Speed
- Wind Gust
- Wind Direction
- Cloud Cover
- Sea Level Pressure
- Relative Humidity
- Total Precipitation
- Condition

### Meteorological Station (if configured)

- Temperature
- Feels Like Temperature
- Wind Speed
- Wind Gust
- Wind Direction
- Cloud Cover
- Sea Level Pressure
- Relative Humidity
- Precipitation
- Condition

### Hydrological Station (if configured)

- Water Level
- Water Temperature
- Water Discharge

## Development

1. Clone this repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/bin/activate` (Linux) or `venv\Scripts\activate` (Windows)
4. Install requirements: `pip install -r requirements_dev.txt`
5. Run tests: `pytest tests/`

## Contributing

Feel free to contribute to this project, pull requests are welcome!

## License

This project is under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

This integration was created by the Home Assistant community.

- Data source: [Meteo.lt API](https://api.meteo.lt/)
