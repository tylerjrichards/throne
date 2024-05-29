import streamlit as st
import pandas as pd
from streamlit_extras.mandatory_date_range import date_range_picker
import plotly.express as px
from streamlit_extras.chart_container import chart_container

st.set_page_config(layout="wide")

st.title("🍔 Throne's Supersize Me Analysis 🍔")
st.markdown("""A truly wild person on [Twitter](https://x.com/ScottHickle), Scott Hickle, decided to
            give the ultimate sacrifice for science and replicate the Supersize experiment while wearing
            every piece of health tracking technology he could get his hands on. He also has a stool focused
            company called Throne.""")
st.markdown("""The above is **catnip** to me. Will his heart rate get crushed? Will his poops be watery? Let's find out!
            I will add more data as he open sources more and more of it. Data is [here](https://github.com/tylerjrichards/throne).""")
st.markdown("Made with ❤️ by [Tyler Richards](https://x.com/tylerjrichards).")

#import data from data folder
hevy_workout = pd.read_csv('data/hevy_workout_data.csv')
hydration = pd.read_csv('data/hydration.csv')
mood = pd.read_csv('data/mood_focus.csv')
oura_heart_rate = pd.read_csv('data/oura_heart_rate.csv')
oura_sleep = pd.read_csv('data/oura_sleep.csv')
oura_sleep_daily = pd.read_csv('data/oura_sleep_daily.csv')


#workout analysis
#start time is like: 9 Nov 2023, 08:50, convert to datetime
hevy_workout['start_time'] = pd.to_datetime(hevy_workout['start_time'], format='%d %b %Y, %H:%M')
hevy_workout['end_time'] = pd.to_datetime(hevy_workout['end_time'], format='%d %b %Y, %H:%M')
#group by title, get min(start_time), max(end_time), and timediff between them
#add the day of the start_time to each title
hevy_workout['day'] = hevy_workout['start_time'].dt.date
#group by both title and day
workout_summary = hevy_workout.groupby(['title', 'day']).agg({'start_time':'min', 'end_time':'max'}).reset_index()
workout_summary['duration'] = workout_summary['end_time'] - workout_summary['start_time']
#turn the duration into minutes
workout_summary['duration'] = workout_summary['duration'].dt.total_seconds() / 60
date_range = date_range_picker(title="Select Date Range", default_start=workout_summary['day'].min(), default_end=workout_summary['day'].max())

col1, col2 = st.columns(2)
with col1:
    st.subheader("🏋️‍♂️ Workout Analysis 🏋️‍♂️")
    #pick a date range, filter the dataframe, and then display a histogram in plotly of the duration of the workouts
    workout_summary_filtered = workout_summary[(workout_summary['day'] >= date_range[0]) & (workout_summary['day'] <= date_range[1])]

    #plot the duration of the workouts
    fig = px.histogram(workout_summary_filtered, x='duration')
    fig.update_xaxes(title='Duration (minutes)')
    fig.update_yaxes(title='Count')
    with chart_container(workout_summary_filtered):
        st.plotly_chart(fig)

with col2:
    #hydration analysis
    st.subheader("💧 Hydration Analysis 💧")
    #make a line chart of avg_daily_hydration_score by day
    hydration['day'] = pd.to_datetime(hydration['session_start']).dt.date
    #get distinct days and the avg hydration score for each day
    hydration_summary = hydration.groupby('day').agg({'hydration_score':'mean'}).reset_index()
    #get a rolling average of the hydration score
    hydration_summary['rolling_avg'] = hydration_summary['hydration_score'].rolling(window=7).mean()
    #filter out where rolling_avg is null
    hydration_summary = hydration_summary[~hydration_summary['rolling_avg'].isnull()]
    fig = px.line(hydration_summary, x='day', y='rolling_avg')
    fig.update_xaxes(title='Day')
    fig.update_yaxes(title='Avg Hydration Score (rolling 7 day avg)')
    with chart_container(hydration_summary):
        st.plotly_chart(fig)

#make a histogram of the stool_category
#drop nulls or blanks in bss
hydration = hydration[~hydration['bss'].isnull()]
fig = px.histogram(hydration, x='stool_category')
fig.update_xaxes(title='Stool Category')
fig.update_yaxes(title='Count')
with col1:
    st.subheader("💩 Stool Category Histogram 💩")
    with chart_container(hydration):
        st.plotly_chart(fig)
#filter where type = long_sleep
oura_sleep_long = oura_sleep[oura_sleep['type'] == 'long_sleep']
#deep sleep duration from seconds to hours
oura_sleep_long['deep_sleep_duration'] = oura_sleep_long['deep_sleep_duration'] / 3600
#same with light_sleep_duration
oura_sleep_long['light_sleep_duration'] = oura_sleep_long['light_sleep_duration'] / 3600
#same with rem_sleep_duration
oura_sleep_long['rem_sleep_duration'] = oura_sleep_long['rem_sleep_duration'] / 3600
#make each a 7d rolling average
oura_sleep_long['deep_sleep_duration'] = oura_sleep_long['deep_sleep_duration'].rolling(window=7).mean()
oura_sleep_long['light_sleep_duration'] = oura_sleep_long['light_sleep_duration'].rolling(window=7).mean()
oura_sleep_long['rem_sleep_duration'] = oura_sleep_long['rem_sleep_duration'].rolling(window=7).mean()
#sum the total sleep duration
oura_sleep_long['total_sleep_duration'] = oura_sleep_long['deep_sleep_duration'] + oura_sleep_long['light_sleep_duration'] + oura_sleep_long['rem_sleep_duration']
#drop nulls
oura_sleep_long = oura_sleep_long[~oura_sleep_long['deep_sleep_duration'].isnull()]
#make a line chart by day, of deep_sleep_duration, light_sleep_duration, and rem_sleep_duration
fig = px.line(oura_sleep_long, x='day', y=['deep_sleep_duration', 'light_sleep_duration', 'rem_sleep_duration', 'total_sleep_duration'])
fig.update_xaxes(title='Day')
fig.update_yaxes(title='Hours')
with col2:
    st.subheader("🛌 Sleep Analysis 🛌")
    with chart_container(oura_sleep_long):
        st.plotly_chart(fig)