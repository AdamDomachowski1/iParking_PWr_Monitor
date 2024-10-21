# iParking Data Fetcher

## Overview

This project consists of two Python scripts that retrieve parking data from the iParking system at Wrocław University of Science and Technology. The data is fetched via HTTP POST requests to the iParking API and saved into CSV files for analysis or archival purposes.

## Scripts

### 1. Daily Parking History Script (`parking_history_data.csv`)
- Retrieves parking data for specific parking lots (IDs: 2, 4, 5, 6, 7) showing available spaces throughout the day.
- The data is stored in a CSV file, with columns for parking lot names and rows for time points.

### 2. Current Parking Status Script (`parking_data.csv`)
- Sends a request to the iParking API to get the current availability of all parking lots.
- The data is written to a CSV file, with columns for the timestamp and the number of available spaces per parking lot.
