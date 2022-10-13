import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

st.title('School Data')

schoolData = pd.read_csv('UpdatedSchoolData/schoolData.csv')
frpl = pd.read_csv('UpdatedSchoolData/frpl.csv')

#Cleaning Data
#Keeping only totals
#This is called advanced indexing
#The .isnull() fx is JUST for NAs

mask = schoolData['school_group'].isnull()
schoolData = schoolData[mask]

#Next, remove the unnecessary columns

schoolData = schoolData.drop(columns=["school_group", "grade", "pi_pct", "blank_col"])

#Remove Grand Total row
#Can also use [schoolData.drop(schoolData.tail(n).index)] to drop last n rows

mask = schoolData['school_name'] != 'Grand Total'
schoolData = schoolData[mask]

#Remove 'Total' from Names

schoolData['school_name']= schoolData['school_name'].str.replace('Total', '')

#Remove leading and trailing spaces. We don't know if they are there so we use the STRIP command

schoolData['school_name']= schoolData['school_name'].str.strip()

#Remove the percentage. Here, we set this as a function because we have so many that we have to convert
def convertPercentToNumber(column):
    column = column.str.replace('%', '')
    column = pd.to_numeric(column)
    return column


schoolData['aa_pct']=convertPercentToNumber(schoolData['aa_pct'])
schoolData['na_pct']=convertPercentToNumber(schoolData['na_pct'])
schoolData['as_pct']=convertPercentToNumber(schoolData['as_pct'])
schoolData['hi_pct']=convertPercentToNumber(schoolData['hi_pct'])
schoolData['wh_pct']=convertPercentToNumber(schoolData['wh_pct'])

#FRPL dataset

#Remove NA from name
#'~' means 'will not retain'. basically 'no'

mask = ~frpl['school_name'].isnull()
frpl = frpl[mask]

frpl['frpl_pct']=convertPercentToNumber(frpl['frpl_pct'])

# Data Wrangling :cowboy

#Joining Datasets

joinedDataset = schoolData.merge(frpl, on='school_name', how='left')

#st.subheader('Look at our joined datasets!')
#st.write('🤠 Consider this data wrangled 🤠')
#st.write(joinedDataset)


# Calculate high_poverty

joinedDataset = joinedDataset.assign(high_poverty=lambda x: x.frpl_pct > 75)

#Interface

st.sidebar.title("Controls")

visualization=st.sidebar.radio('Select Visualization',
                               options=['General Population','Percentage of Poverty','Race/Ethnicity and Poverty',
                                        'Histogram of Percentages'])

sizeRange = st.sidebar.slider("Select the size of the school:",
    min_value=int(joinedDataset['tot'].min()), max_value=int(joinedDataset['tot'].max()),
                              value=(int(joinedDataset['tot'].min()),int(joinedDataset['tot'].max())))

#Filter Dataset

mask=joinedDataset['tot'].between(sizeRange[0],sizeRange[1])
# the 0 and 1 represent the POSITION of the values, not the values themselves
joinedDataset=joinedDataset[mask]

#Select the schools to work with. We do this after the data is filtered so that ONLY the schools meeting that condition will appear.
selectedSchools= st.sidebar.multiselect("Select the schools to be included:",
                                        options=joinedDataset['school_name'].unique(),
                                        default=joinedDataset['school_name'].unique())

#Filter the data for schools to include.

mask=joinedDataset['school_name'].isin(selectedSchools)
joinedDataset=joinedDataset[mask]

## Wrangle the data for populations

SchoolData_population = joinedDataset.melt(
    id_vars=['school_name','high_poverty'], #column that uniquely identifies a row (can be multiple)
    value_vars=['na_num','aa_num','as_num','hi_num','wh_num'],
    var_name='race_ethnicity', #name for the new column created by melting
    value_name='population' #name for new column containing values from melted columns
)

SchoolData_population['race_ethnicity']= SchoolData_population['race_ethnicity'].replace('na_num',"Native American")
SchoolData_population['race_ethnicity']= SchoolData_population['race_ethnicity'].replace('aa_num',"African American")
SchoolData_population['race_ethnicity']= SchoolData_population['race_ethnicity'].replace('as_num',"Asian American")
SchoolData_population['race_ethnicity']= SchoolData_population['race_ethnicity'].replace('hi_num',"Hispanic American")
SchoolData_population['race_ethnicity']= SchoolData_population['race_ethnicity'].replace('wh_num',"White")

population_summary=SchoolData_population.groupby('race_ethnicity').sum()

#st.write(SchoolData_population)


#Visualization "General Population"

if visualization== 'General Population':
    col1, col2 = st.columns(2)

    with col1:
        fig=px.pie(SchoolData_population,values='population',names='race_ethnicity',
                   title='Population Percentage per Race')
        st.plotly_chart(fig)

    with col2:
        fig2 = px.bar(population_summary, x=population_summary.index, y='population')
        st.plotly_chart(fig2)

    population_summary

if visualization=="Percentage of Poverty":
    fig = px.pie(joinedDataset, names='high_poverty')
    st.plotly_chart(fig)


if visualization=='Race/Ethnicity and Poverty':
    fig = px.pie(SchoolData_population, values='population', names='race_ethnicity', facet_col='high_poverty',
                 title='Populations Percentage per Race')
    st.plotly_chart(fig)


if visualization=='Histogram of Percentages':
    fig = px.histogram(joinedDataset, x="aa_pct", color="high_poverty", marginal="rug", title='African American')
    fig.update_layout(barmode='overlay')
    fig.update_traces(opacity=0.75)
    st.plotly_chart(fig)

    fig = px.histogram(joinedDataset, x="na_pct", color="high_poverty", marginal="rug", title='Native American')
    fig.update_layout(barmode='overlay')
    fig.update_traces(opacity=0.75)
    st.plotly_chart(fig)

    fig = px.histogram(joinedDataset, x="as_pct", color="high_poverty", marginal="rug", title='Asian American')
    fig.update_layout(barmode='overlay')
    fig.update_traces(opacity=0.75)
    st.plotly_chart(fig)

    fig = px.histogram(joinedDataset, x="hi_pct", color="high_poverty", marginal="rug", title='Hispanic')
    fig.update_layout(barmode='overlay')
    fig.update_traces(opacity=0.75)
    st.plotly_chart(fig)

    fig = px.histogram(joinedDataset, x="wh_pct", color="high_poverty", marginal="rug", title='White', width=500)
    fig.update_layout(barmode='overlay')
    fig.update_traces(opacity=0.75)
    st.plotly_chart(fig)







