import pandas as pd
import plotly.express as px

# Load the dataset (update the file path if needed)
file_path = '../parking_history_data.csv'  # Place the CSV in the same directory as this script
parking_data = pd.read_csv(file_path)

# Convert the "Data" and "Czas" columns into a single datetime column
parking_data['Datetime'] = pd.to_datetime(parking_data['Data'] + ' ' + parking_data['Czas'])

# Add a new column for the day of the week
parking_data['Day of Week'] = parking_data['Datetime'].dt.strftime('%A')  # Full weekday name

# Add a column for the hour of the day
parking_data['Hour'] = parking_data['Datetime'].dt.strftime('%H:%M')

# Drop the original date and time columns
parking_data.drop(columns=['Data', 'Czas'], inplace=True)

# Melt the dataframe to create a long format suitable for plotting
melted_data = parking_data.melt(
    id_vars=['Datetime', 'Day of Week', 'Hour'], 
    var_name='Parking Location', 
    value_name='Value'
)

# Create an interactive plot for each parking location
fig = px.line(
    melted_data,
    x='Datetime',
    y='Value',
    color='Parking Location',
    title='Parking Occupancy Over Time',
    labels={'Value': 'Occupancy', 'Datetime': 'Time', 'Day of Week': 'Weekday', 'Hour': 'Time of Day'},
    line_group='Parking Location',
    hover_data={'Day of Week': True, 'Hour': True}  # Add weekday and hour to the hover tooltip
)

# Update layout to improve visualization
fig.update_layout(
    xaxis_title='Time',
    yaxis_title='Occupancy',
    xaxis=dict(
        tickformat="%a\n%b %d",  # Short weekday name (e.g., "Mon") and date
    )
)

# Save the plot as an HTML file
output_file_path = 'parking_occupancy_with_weekdays_and_hours.html'
fig.write_html(output_file_path)

print(f"Interactive plot with weekdays and hours saved to {output_file_path}. Open this file in your browser to view it.")
