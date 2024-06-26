# Atmaca Rocket Team - Ground Station Data Monitoring Tool

![Logo](resources/logo.png)

This project is a tool developed to monitor the ground station data of the Atmaca Rocket Team. The application uses PyQt5 and other Python libraries to read, visualize, and save real-time data streaming through the serial port.

You can access the sample Arduino code that writes the data received from this program in json format by clicking [here](https://github.com/mertkaplandar/rocket-ground-station-hardware-code). Do not make any changes to the Arduino code for the program to work correctly and properly. Continue by leaving any unused data in the data package blank.

You can view this text in Turkish by clicking [here](README_TR.md).

## Features

- Data acquisition and display via serial port
- Real-time location display on the map
- Real-time charts for altitude, pressure, and speed data monitoring
- Test mode to display sample data
- Data recording and export
- Examining previously recorded data in detail on graphs with the graph-viewer.py tool

## Requirements

The following Python libraries are required to run this project:

- PyQt5
- pyserial
- folium
- matplotlib
- PyQtWebEngine

## Installation

1. **Clone the Repository:**

    ```sh
    git clone https://github.com/mertkaplandar/rocket-ground-station-app.git
    cd rocket-ground-station-app
    ```

2. **Install Required Libraries:**

    ```sh
    pip install -r requirements.txt
    ```

3. **Run the Application:**

    ```sh
    python app.py
    ```

## Usage

1. **Select Port and Baud Rate:**
   - When you start the application, select the available ports and baud rate.
   - Click the "Connect" button.

2. **Data Monitoring:**
   - Once data streaming starts, you can see real-time data in the "Data" tab.
   - In the "Charts" tab, you can examine altitude, pressure, and speed charts.
   - In the "Map" tab, you can track your location on the map.

3. **Test Mode:**
   - Click the "Test Mode" button to run the application with test data.


## Contact

For any questions or suggestions, please contact with [Mert Kaplandar](https://github.com/mertkaplandar).
