import streamlit as st
import pandas as pd
import plotly.express as px 


### CONFIG
st.set_page_config(
    page_title="Getaround Project",
    page_icon="🚗",
    layout="wide"
  )

### TITLE AND TEXT
st.title("Getaround Analysis on Delays ⏱")


### VIDEO EXPANDER
with st.expander("⏯️ French commercial for Getaround!"):
    st.video("https://youtu.be/A9NGC9-vsqo")

st.markdown("---")


st.markdown("""
    Easy concept, but unfortunately, sometimes drivers are late for checkouts. This situation can be a problem if another rental is planned right after this checkout.
    Here are some figures to help you take the best decisions about the minimum delay between two car rentals.  👇
""")




### LOAD AND CACHE DATA
DATA_URL = ('https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_delay_analysis.xlsx')

@st.cache_data # this lets the data in cache once it was open
def load_data():
    data = pd.read_excel(DATA_URL)
    return data

data_load_state = st.text('Loading data...')
data = load_data()
data_load_state.text("")



### SIDEBAR
st.sidebar.header("Sections")
st.sidebar.markdown("""
    * **Original Data and Basic Information**
    * **Focus on Delays**
    * **Threshold Simulation**
""")
e = st.sidebar.empty()
e.write("")
st.sidebar.write("Contact [Wendy MARTINS](https://fr.linkedin.com/in/wendy-martins)")



st.markdown("---")

st.subheader("Original Data and Basic Information")

## Run the below code if the check is checked
if st.checkbox('Show dataset'):
    st.subheader('Dataset')
    st.write(data) 
st.markdown("")
st.markdown("")

# We consider no values on "delay_at_checkout_in_minutes" as oversights and consider them "in time checkout"
data["delay_at_checkout_in_minutes"].fillna(0, inplace=True) 

# Creating a new df to be able to merge both of them and add the values from the previous renting on a global df
data_bis = data.loc[:, ['rental_id', 'checkin_type', 'state', 'delay_at_checkout_in_minutes']]
data_bis = data_bis.rename(columns={"rental_id": "previous_rental_id","checkin_type": "previous_checkin_type", "state": "previous_state","delay_at_checkout_in_minutes": "previous_delay_at_checkout_in_minutes" })

# Mergin dataframes
full_df = pd.merge(data, data_bis, how='left', left_on='previous_ended_rental_id', right_on='previous_rental_id')
full_df = full_df.drop("previous_rental_id", axis=1)

# Adding new columns to see if checkout on-time or late, and to have the time delta between 2 rentals (planned + real one)
full_df['on_time-late'] = full_df["delay_at_checkout_in_minutes"].apply(lambda x: "In time or in advance" if x <= 0 else "Late")
full_df['previous_on_time-late'] = full_df["previous_delay_at_checkout_in_minutes"].apply(lambda x: "In time or in advance" if x <= 0 else ("Late" if x > 0 else "no previous renting"))
full_df = full_df[['rental_id', 'car_id', 'checkin_type', 'state',
       'delay_at_checkout_in_minutes','on_time-late', 'previous_ended_rental_id',
       'time_delta_with_previous_rental_in_minutes', 'previous_checkin_type',
       'previous_state', 'previous_delay_at_checkout_in_minutes','previous_on_time-late']]
full_df["time_delta_with_previous_rental_in_minutes"].fillna(1440, inplace=True) # if no information about past rantal, we set a timedelta of 24h
full_df['real_time_delta'] = full_df['time_delta_with_previous_rental_in_minutes'] - full_df['previous_delay_at_checkout_in_minutes']



col1, col2 = st.columns(2)

with col1:
    st.metric(label="Number of cars", value=full_df['car_id'].nunique())

with col2:
    st.metric(label="Number of rentals", value=full_df['rental_id'].nunique())


st.markdown("")
st.markdown("")
st.markdown("")
st.markdown("")
st.markdown("")
st.markdown("")



col1, col2, col3 = st.columns([15,5,40])

with col1:
    st.markdown('')
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("**Proportion of rentals: Mobile / Connect**")
    st.markdown("")
    st.markdown("")
    fig = px.pie(full_df, values='rental_id', names="checkin_type", width= 1000, color='checkin_type',color_discrete_map={'mobile':'blue','connect':'orange'})       
    st.plotly_chart(fig, use_container_width=True)


with col3:
    checkin_type1 = st.selectbox("Checkin type", ['mobile + connect', 'mobile', 'connect'], key=1)

    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('**Proportion of late checkouts per type**')
            df_delay = full_df if checkin_type1 == 'mobile + connect' else full_df[full_df["checkin_type"]==checkin_type1]
            fig = px.pie(df_delay, values='rental_id', names="on_time-late",
                        color='on_time-late',
                        color_discrete_map={'Late':'red','In time or in advance':'green'})
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Proportion of canceled rentals per type**")
            df_cancellation = full_df if checkin_type1 == 'mobile + connect' else full_df[full_df["checkin_type"]==checkin_type1]
            fig = px.pie(df_cancellation, values='rental_id', names="state",
                        color='state',
                        color_discrete_map={'canceled':'red','ended':'green'})
            st.plotly_chart(fig, use_container_width=True)


st.markdown("**There are more late checkouts with mobile rentals**")
st.markdown("We can assume that checkouts are much quicker when there is only one person involved (connect rentals: no need for the owner to be present).")
st.markdown("")
st.markdown("**There are more cancellations with connect rentals**")
st.markdown("We can assume that people are less ashamed of canceling the rental when there is no appointment with the owner.")
st.markdown("")
st.markdown("")



st.markdown("""---""")
st.subheader("Focus on Delays")
st.markdown('Delays at checkout (minutes) - *We do not consider delays over 12 hours*')
fig = px.histogram(full_df, x='delay_at_checkout_in_minutes', range_x=["0","720"])
st.plotly_chart(fig, use_container_width=True)



st.markdown("**Proportion of cancelation when former checkout was late**")
checkin_type2 = st.selectbox("Checkin type", ['mobile + connect', 'mobile', 'connect'], key=2)
df_cancellation_when_previous_delay = full_df if checkin_type2 == 'mobile + connect' else full_df[full_df["checkin_type"]==checkin_type2]
fig = px.pie(df_cancellation_when_previous_delay, values='previous_ended_rental_id', names="state",
            color='state',
            color_discrete_map={'canceled':'red','ended':'green'})
st.plotly_chart(fig, use_container_width=True)




st.markdown("**Planned time delta with previous rental (only if < 12 hours)**")
fig = px.histogram(full_df[full_df['time_delta_with_previous_rental_in_minutes']<720], x='time_delta_with_previous_rental_in_minutes', range_x=["0","720"])
st.plotly_chart(fig, use_container_width=True)


st.markdown("""---""")

st.subheader("Threshold Simulation")

with st.form("Simulation of delay implementation between 2 rentals"):
    threshold_test = st.number_input('Delay in minutes', min_value=0, max_value=720, step=5)
    checkin_type3 = st.selectbox("Checkin type", ['mobile + connect', 'mobile', 'connect'], key=3)
    submit = st.form_submit_button("submit")
    if submit:
        filtered_df = full_df if checkin_type3 == "mobile + connect" else full_df[full_df["checkin_type"]==checkin_type3]
        st.markdown(f"Out of the **{len(filtered_df)} rentals** studied in our data, if we set up a threshold of **{threshold_test} minutes** between two rentals, \
                    we would potientally lose {(len(filtered_df)) - (len(filtered_df[filtered_df['time_delta_with_previous_rental_in_minutes'] >= threshold_test]))} rentals.")
        st.markdown("")
        st.markdown(f"But we have to keep in mind that within these potential losses, there were already some cancelations above this threshold.")
        st.markdown(f"So the **:red[actual loss would be of \
                    {len(filtered_df[(filtered_df['state']=='ended') & (filtered_df['time_delta_with_previous_rental_in_minutes'] < threshold_test)])} rentals]**: \
                    **:blue[{len(filtered_df[(filtered_df['state']=='ended') & (filtered_df['time_delta_with_previous_rental_in_minutes'] < threshold_test) & (filtered_df['checkin_type'] =='connect')])} from connect]** rentals and \
                    **:blue[{len(filtered_df[(filtered_df['state']=='ended') & (filtered_df['time_delta_with_previous_rental_in_minutes'] < threshold_test) & (filtered_df['checkin_type'] =='mobile')])} from mobile]** rentals.")
        st.markdown("")
        st.markdown(f"**This is theoretical, we do not take into account the early checkouts, as they are unpredictable.**")