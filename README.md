# Streamlit Cuadrantes App

This project is a Streamlit application that visualizes data related to "Cambio_cuadrante" with interactive features. Users can select a date range to filter the data and view it in a graph and a table.

## Project Structure

```
streamlit-cuadrantes-app
├── src
│   ├── app.py          # Main application file for the Streamlit app
│   └── utils.py        # Utility functions for data processing
├── requirements.txt     # List of dependencies
└── README.md            # Project documentation
```

## Installation

To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd streamlit-cuadrantes-app
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the App

To run the Streamlit app, execute the following command in your terminal:
```
streamlit run src/app.py
```

This will start the Streamlit server and open the app in your default web browser.

## Features

- **Interactive Graph**: Users can select a start and end date to filter the data displayed in the graph.
- **Data Table**: Below the graph, a table displays the raw data corresponding to the selected "Cambio_cuadrante" without aggregation.

## Dependencies

The project requires the following Python packages:

- Streamlit
- Pandas
- NumPy
- Matplotlib
- Seaborn

Make sure to install these packages using the `requirements.txt` file.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.