import pandas as pd
import plotly.express as px
import streamlit as st

# Load the dataset
csv_file_path = 'asylum_seekers.csv'
asylum_seekers_df = pd.read_csv(csv_file_path)

# Clean the data and ensure numeric columns are correctly interpreted
asylum_seekers_df['Applied during year'] = pd.to_numeric(asylum_seekers_df['Applied during year'], errors='coerce')
asylum_seekers_df['Total decisions'] = pd.to_numeric(asylum_seekers_df['Total decisions'], errors='coerce')

# Aggregate data to get inflow and outflow per country per year
inflow_df = asylum_seekers_df.groupby(['Year', 'Country / territory of asylum/residence', 'Origin']).agg({
    'Applied during year': 'sum'
}).reset_index()

outflow_df = asylum_seekers_df.groupby(['Year', 'Origin', 'Country / territory of asylum/residence']).agg({
    'Applied during year': 'sum'
}).reset_index()

# Rename columns for clarity
inflow_df.rename(columns={'Country / territory of asylum/residence': 'Country', 'Applied during year': 'Inflow'}, inplace=True)
outflow_df.rename(columns={'Country / territory of asylum/residence': 'Destination', 'Applied during year': 'Outflow'}, inplace=True)

# Merge inflow and outflow data for the map
map_df = inflow_df.groupby(['Year', 'Country']).agg({'Inflow': 'sum'}).reset_index()
outflow_agg_df = outflow_df.groupby(['Year', 'Origin']).agg({'Outflow': 'sum'}).reset_index()
outflow_agg_df.rename(columns={'Origin': 'Country'}, inplace=True)
flow_df = pd.merge(map_df, outflow_agg_df, on=['Year', 'Country'], how='outer').fillna(0)
flow_df['Net Flow'] = flow_df['Inflow'] - flow_df['Outflow']

fig = px.choropleth(flow_df,
                    locations="Country",
                    locationmode="country names",
                    color="Net Flow",
                    hover_name="Country",
                    animation_frame="Year",
                    projection="natural earth",
                    title="Inflow and Outflow of Refugees Over the Years",
                    color_continuous_scale=["red", "white", "blue"])

# Customize the layout
fig.update_layout(coloraxis_colorbar=dict(title="Net Flow"),
                  geo=dict(showframe=False, showcoastlines=True))

# Display the map in Streamlit
st.title("Inflow and Outflow of Refugees Over the Years")
st.plotly_chart(fig)
# Set up the Streamlit app
st.title("Asylum Seekers Dashboard")

# Filter by year
years = asylum_seekers_df['Year'].unique()
selected_year = st.sidebar.selectbox('Select Year', sorted(years))

# Filter by country
countries = asylum_seekers_df['Country / territory of asylum/residence'].unique()
selected_country = st.sidebar.selectbox('Select Country', sorted(countries))

# Filter data based on selections for inflow and outflow
filtered_inflow_df = inflow_df[(inflow_df['Year'] == selected_year) & (inflow_df['Country'] == selected_country)]
filtered_outflow_df = outflow_df[(outflow_df['Year'] == selected_year) & (outflow_df['Origin'] == selected_country)]

# Display filtered data
st.write(f"Data for {selected_country} in {selected_year}")

# Display inflow chart
if not filtered_inflow_df.empty:
    inflow_chart = px.bar(filtered_inflow_df, x='Origin', y='Inflow', title='Inflow of Refugees')
    st.plotly_chart(inflow_chart)
else:
    st.write("No inflow data available.")

# Display outflow chart
if not filtered_outflow_df.empty:
    outflow_chart = px.bar(filtered_outflow_df, x='Destination', y='Outflow', title='Outflow of Refugees')
    st.plotly_chart(outflow_chart)
else:
    st.write("No outflow data available.")


