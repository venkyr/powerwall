# Powerwall Monitor

A Python script to monitor Tesla Powerwall energy data and store it in InfluxDB. The script collects power measurements for grid, battery, solar, and home consumption every minute.

## Features

- Monitors real-time power data from Tesla Powerwall
- Collects grid, battery, solar, and home power measurements
- Tracks battery charge level percentage
- Stores data in InfluxDB for visualization and analysis
- Configurable measurement interval
- Robust error handling and connection management

## Requirements

- Python 3.12+
- Tesla Powerwall with local network access
- InfluxDB 2.x instance

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/venkyr/powerwall.git
   cd powerwall
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create configuration file:
   ```bash
   cp config.ini.template config.ini
   ```

5. Edit `config.ini` with your credentials:
   ```ini
   [powerwall]
   host = powerwall.local
   password = your_powerwall_password
   email = your_email@example.com

   [influxdb]
   url = http://your.influxdb.server:8086
   token = your_influxdb_token
   org = your_organization
   bucket = your_bucket
   ```

## Usage

Run the monitoring script:
```bash
python powerwall_monitor.py
```

The script will:
- Connect to your Powerwall using local network credentials
- Collect power measurements every minute
- Store two types of measurements in InfluxDB:
  1. `power` measurement with fields:
     - `grid`: Grid power (positive = importing, negative = exporting)
     - `battery`: Battery power (positive = discharging, negative = charging)
     - `solar`: Solar power (positive when generating)
     - `home`: Home consumption (positive when consuming)
  2. `battery` measurement with field:
     - `level`: Battery charge percentage

## Data Visualization

You can visualize the data in InfluxDB using tools like:
- Grafana
- Chronograf
- InfluxDB's built-in Data Explorer

## Error Handling

The script includes error handling for:
- Connection issues with Powerwall
- Connection issues with InfluxDB
- Invalid measurements
- Configuration errors

To stop the script, press Ctrl+C.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 