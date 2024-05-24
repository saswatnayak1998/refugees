import pandas as pd
import plotly.express as px

# Load the dataset
csv_file_path = 'asylum_seekers.csv'
asylum_seekers_df = pd.read_csv(csv_file_path)

# Clean the data and ensure numeric columns are correctly interpreted
asylum_seekers_df['Applied during year'] = pd.to_numeric(asylum_seekers_df['Applied during year'], errors='coerce')
asylum_seekers_df['Total decisions'] = pd.to_numeric(asylum_seekers_df['Total decisions'], errors='coerce')

# Aggregate data to get inflow and outflow per country per year
inflow_df = asylum_seekers_df.groupby(['Year', 'Country / territory of asylum/residence']).agg({
    'Applied during year': 'sum'
}).reset_index()

outflow_df = asylum_seekers_df.groupby(['Year', 'Origin']).agg({
    'Applied during year': 'sum'
}).reset_index()

# Rename columns for clarity
inflow_df.rename(columns={'Country / territory of asylum/residence': 'Country', 'Applied during year': 'Inflow'}, inplace=True)
outflow_df.rename(columns={'Origin': 'Country', 'Applied during year': 'Outflow'}, inplace=True)

# Merge inflow and outflow data
flow_df = pd.merge(inflow_df, outflow_df, on=['Year', 'Country'], how='outer').fillna(0)

# Create the animated map
fig = px.scatter_geo(flow_df,
                     locations="Country",
                     locationmode="country names",
                     color="Country",
                     size="Inflow",
                     hover_name="Country",
                     animation_frame="Year",
                     projection="natural earth",
                     title="Inflow and Outflow of Refugees Over the Years")

# Customize the layout
fig.update_layout(legend=dict(title='Country'),
                  geo=dict(showframe=False, showcoastlines=True))

# Show the figure (in Streamlit use st.plotly_chart instead)
fig.show()
