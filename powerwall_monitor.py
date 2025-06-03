#!/usr/bin/env python3

import configparser
import time
from datetime import datetime
from pathlib import Path

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from pypowerwall import Powerwall

class PowerwallMonitor:
    def __init__(self, config_path='config.ini'):
        self.config = self._load_config(config_path)
        self.powerwall = self._init_powerwall()
        self.influx_client = self._init_influxdb()
        self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)

    def _load_config(self, config_path):
        if not Path(config_path).exists():
            raise FileNotFoundError(
                f"Configuration file not found at {config_path}. "
                f"Please copy config.ini.template to config.ini and update the values."
            )
        
        config = configparser.ConfigParser()
        config.read(config_path)
        return config

    def _init_powerwall(self):
        """Initialize connection to Powerwall.
        Raises:
            Exception: If connection fails or host is unreachable
        """
        powerwall = Powerwall(
            host=self.config['powerwall']['host'],
            password=self.config['powerwall']['password'],
            email=self.config['powerwall']['email'],
            timezone="America/Los_Angeles"  # This will be detected automatically
        )
        if not powerwall.is_connected():
            raise Exception(f"Failed to connect to Powerwall at {self.config['powerwall']['host']}: Connection failed. Please verify the hostname is correct.")
        return powerwall

    def _init_influxdb(self):
        try:
            return InfluxDBClient(
                url=self.config['influxdb']['url'],
                token=self.config['influxdb']['token'],
                org=self.config['influxdb']['org']
            )
        except Exception as e:
            raise Exception(f"Failed to connect to InfluxDB: {str(e)}")

    def get_measurements(self):
        """Get current power measurements from the Powerwall.
        
        Returns power measurements with the following sign conventions:
        - grid: positive = importing, negative = exporting
        - battery: positive = discharging, negative = charging
        - solar: positive = generating (as reported by Powerwall)
        - home: positive = consuming
        
        All measurements are rounded to the nearest integer.
        """
        try:
            power = self.powerwall.power()
            return {
                'grid': round(power['site']),
                'battery': round(power['battery']),
                'solar': round(power['solar']),
                'home': round(power['load'])
            }
        except Exception as e:
            print(f"Error getting measurements: {str(e)}")
            return None

    def get_battery_level(self):
        """Get current battery level percentage from the Powerwall."""
        try:
            return round(self.powerwall.level())
        except Exception as e:
            print(f"Error getting battery level: {str(e)}")
            return None

    def write_to_influxdb(self, measurements):
        """Write measurements to InfluxDB."""
        if not measurements:
            return

        try:
            # Write power measurements
            power_point = Point("power")\
                .field("grid", measurements['grid'])\
                .field("battery", measurements['battery'])\
                .field("solar", measurements['solar'])\
                .field("home", measurements['home'])

            # Write battery level
            battery_level = self.get_battery_level()
            if battery_level is not None:
                battery_point = Point("battery")\
                    .field("level", battery_level)
                
                self.write_api.write(
                    bucket=self.config['influxdb']['bucket'],
                    record=[power_point, battery_point]
                )
            else:
                self.write_api.write(
                    bucket=self.config['influxdb']['bucket'],
                    record=power_point
                )
        except Exception as e:
            print(f"Error writing to InfluxDB: {str(e)}")

    def run(self, interval=60):
        """Run the monitoring loop with the specified interval in seconds."""
        print(f"Starting Powerwall monitoring for host: {self.config['powerwall']['host']}...")
        while True:
            try:
                measurements = self.get_measurements()
                if measurements:
                    self.write_to_influxdb(measurements)
                    print(f"Measurements recorded at {datetime.now()}: {measurements}")
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\nStopping Powerwall monitoring...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
                time.sleep(interval)

def main():
    monitor = PowerwallMonitor()
    monitor.run()

if __name__ == "__main__":
    main() 