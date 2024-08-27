import pandas as pd 
import dash
from dash import Dash, dcc, html, callback
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash import dash_table
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import plotly.graph_objects as go


# Define your custom CSS styles
custom_css = '''
body {
    background-color: #f0f0f0; 
    color: #333; 
    font-family: "Helvetica", sans-serif;
}

h1, h2, h3, h4, h5, h6 {
    font-family: "Helvetica", sans-serif;
    color: black;
    margin-top: 20px;
    margin-bottom: 10px;
}

center-content {
    text-align: center;
    width: 100%;
}

center-block {
    display: block;
    margin-left: auto;
    margin-right: auto;
}

'''



##Data

avg_daily_income = pd.read_csv('./data/avg_daily_income_corrected.csv')
income_inequality = pd.read_csv('./data/income_inequality_full.csv')
democracy = pd.read_csv('./data/democracy_full.csv')
government = pd.read_csv('./data/government_full.csv')
woman_parliament = pd.read_csv('./data/women_parliament_full.csv')
countries = pd.read_csv('./data/countries.csv')
population = pd.read_csv('./data/population_full.csv')
happiness = pd.read_csv('./data/happiness_score_full.csv')
year_columns = ['2005', '2006', '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019']
df_long = pd.melt(happiness, id_vars=['country', 'country_code', 'continent'], value_vars=[str(year) for year in range(2005, 2020)],
                  var_name='year', value_name='happiness_score')
happiness['avg_score'] = happiness[year_columns].mean(axis=1, skipna=True)


avg_income_long = pd.melt(avg_daily_income, id_vars=['country', 'country_code', 'continent'], value_vars=[str(year) for year in range(1800, 2020)],
                  var_name='year', value_name='avg_daily_income')
income_inequality_long = pd.melt(income_inequality, id_vars=['country', 'country_code', 'continent'], value_vars=[str(year) for year in range(1800, 2020)],
                  var_name='year', value_name='income_inequality')
df_income = pd.merge(avg_income_long, income_inequality_long, how='left', on=['country','country_code','continent','year'])
happiness_income = df_long.merge(df_income, how='left', on=['country','country_code','continent','year'])
population_long = pd.melt(population, id_vars=['country', 'country_code', 'continent'], value_vars=[str(year) for year in range(1960, 2020)],
                  var_name='year', value_name='population')
happiness_income = happiness_income.merge(population_long, how='left', on=['country','country_code','continent','year'])
happiness_income.sort_values(by=['country', 'year'])
#happiness_income['population'] = happiness_income.groupby('country')['population'].bfill().ffill()

#filling datasets :
#happiness_income_full = happiness_income
#happiness_income_full.sort_values(by=['country', 'year'])
#happiness_income_full['happiness_score'] = happiness_income_full.groupby('country')['happiness_score'].bfill().ffill()
#happiness_income_full['avg_daily_income'] = happiness_income_full.groupby('country')['avg_daily_income'].bfill().ffill()
#happiness_income_full['income_inequality'] = happiness_income_full.groupby('country')['income_inequality'].bfill().ffill()

woman_parliament_long = pd.melt(woman_parliament, id_vars=['country', 'country_code', 'continent'], value_vars=[str(year) for year in range(1945, 2020)],
                  var_name='year', value_name='women_parliament')
happiness_gouv = df_long.merge(woman_parliament_long, how='left', on=['country','country_code','continent','year'])
democracy_long = pd.melt(democracy, id_vars=['country', 'country_code', 'continent'], value_vars=[str(year) for year in range(2006, 2020)],
                  var_name='year', value_name='democracy')
government_long = pd.melt(government, id_vars=['country', 'country_code', 'continent'], value_vars=[str(year) for year in range(2006, 2020)],
                  var_name='year', value_name='functioning_government')
happiness_gouv = happiness_gouv.merge(democracy_long, how='left', on=['country','country_code','continent','year'])
happiness_gouv = happiness_gouv.merge(government_long, how='left', on=['country','country_code','continent','year'])
average_participation = happiness_gouv.groupby(['year', 'continent']).agg({
    'women_parliament': ('mean'),  # Average women participation in parliament
    'happiness_score': ('mean')    # Average happiness score
}).reset_index()
top10 = ["Denmark", "Finland", "Norway", "Switzerland", "Netherlands",
                    "Iceland", "Canada", "Sweden", "New Zealand", "Australia"]
bottom10 = ["Haiti", "Comoros", "Yemen", "Tanzania", "Rwanda", 
                    "Afghanistan", "Burundi", "Togo", "Central African Republic", "Sudan"]
happiness_top10 = happiness.sort_values(by='avg_score', ascending=False)
happiness_top10 = happiness[happiness['country'].isin(top10)]
happiness_top10.sort_values(by='avg_score', ascending=False)
happiness_top10 = happiness_top10.reset_index(drop=True)
happiness_bottom10 = happiness[happiness['country'].isin(bottom10)]
happiness_bottom10.sort_values(by='avg_score', ascending=True)
happiness_bottom10 = happiness_bottom10.reset_index(drop=True)
happ_top_bot = pd.concat([happiness_top10, happiness_bottom10], axis=0)
happ_top_bot = pd.melt(happ_top_bot, id_vars=['country', 'country_code', 'continent'], value_vars=[str(year) for year in range(2005, 2019)],
                  var_name='year', value_name='happiness_score')
happiness_gouv_top10 = happiness_gouv[happiness_gouv['country'].isin(top10)]
happiness_gouv_bottom10 = happiness_gouv[happiness_gouv['country'].isin(bottom10)]
happiness_gouv_tb = pd.concat([happiness_gouv_top10, happiness_gouv_bottom10], axis=0)
happiness_income_top10 = happiness_income[happiness_income['country'].isin(top10)]
happiness_income_bottom10 = happiness_income[happiness_income['country'].isin(bottom10)]
happiness_income_tb = pd.concat([happiness_income_top10, happiness_income_bottom10], axis=0)

hap_tb = pd.merge(happiness_gouv_tb, happiness_income_tb, on=['country','country_code','continent','year', 'happiness_score'], how='inner')
hap_top = hap_tb[hap_tb['country'].isin(top10)]
hap_bottom = hap_tb[hap_tb['country'].isin(bottom10)]
happiness_total_avg = pd.concat([happiness_top10, happiness_bottom10], axis=0)
happiness_total_avg = happiness_total_avg[['country','avg_score']]

selected_countries = ['China', 'Indonesia', 'Croatia', 'France', 'Germany', 'Lithuania', 
                      'Netherlands', 'Poland', 'Spain', 'Turkey', 'New Zealand', 'Kenya','Cameroon']
filter_hap_income = happiness_income[happiness_income['country'].isin(selected_countries)]
filter_hap_income.loc[:, 'country'] = pd.Categorical(filter_hap_income['country'], categories=selected_countries, ordered=True)
filter_hap_income = filter_hap_income.sort_values(['year','country'])
filter_hap_gouv = happiness_gouv[happiness_gouv['country'].isin(selected_countries)]
filter_hap_gouv.loc[:, 'country'] = pd.Categorical(filter_hap_gouv['country'], categories=selected_countries, ordered=True)
filter_hap_gouv = filter_hap_gouv.sort_values(['year','country'])

happiness = pd.melt(happiness, id_vars=['country', 'country_code', 'continent', 'avg_score'], value_vars=[str(year) for year in range(2005, 2019)],
                  var_name='year', value_name='happiness_score')
happiness_sorted = happiness.sort_values(by='avg_score', ascending=True)
continent_avg_scores = happiness_gouv.groupby(['year','continent']).agg({
    'happiness_score': 'mean'  # Calculate mean scores for each continent
}).reset_index()
continent_avg_scores.rename(columns={'happiness_score': 'mean_year_score'}, inplace=True)
continent_count_distr = pd.merge(happiness_sorted, continent_avg_scores, on=['continent','year'], how='outer')


##Colors dictionnary 
continent_colors = {
    'Asia': '#FADCAA',  # Tomato
    'Africa': '#FBB345',  # SteelBlue
    'Europe': '#93A4C2',  # LimeGreen
    'North America': '#122981',  # Gold
    'South America': '#D89DAF',  # OrangeRed
    'Australia and Oceania': '#BF456B',  # BlueViolet
    'Europe, Asia': '#C3CCE2'  # DarkTurquoise
}

#dict for country colors
country_to_continent = {
    'Antigua and Barbuda': 'North America', 'Bahamas': 'North America', 'Belize': 'North America', 
    'Barbados': 'North America', 'Canada': 'North America', 'Costa Rica': 'North America', 
    'Cuba': 'North America', 'Dominica': 'North America', 'Dominican Republic': 'North America', 
    'Grenada': 'North America', 'Guatemala': 'North America', 'Honduras': 'North America', 
    'Haiti': 'North America', 'Jamaica': 'North America', 'Saint Kitts and Nevis': 'North America', 
    'Saint Lucia': 'North America', 'Mexico': 'North America', 'Nicaragua': 'North America', 
    'Panama': 'North America', 'El Salvador': 'North America', 'Trinidad and Tobago': 'North America', 
    'United States': 'North America', 'Saint Vincent and the Grenadines': 'North America',

    'Argentina': 'South America', 'Bolivia': 'South America', 'Brazil': 'South America', 
    'Chile': 'South America', 'Colombia': 'South America', 'Ecuador': 'South America', 
    'Guyana': 'South America', 'Peru': 'South America', 'Paraguay': 'South America', 
    'Suriname': 'South America', 'Uruguay': 'South America', 'Venezuela': 'South America', 

    'Albania': 'Europe', 'Andorra': 'Europe', 'Armenia': 'Europe', 'Austria': 'Europe', 
    'Azerbaijan': 'Europe', 'Belgium': 'Europe', 'Bulgaria': 'Europe', 'Bosnia and Herzegovina': 'Europe', 
    'Belarus': 'Europe', 'Switzerland': 'Europe', 'Cyprus': 'Europe', 'Czech Republic': 'Europe', 
    'Germany': 'Europe', 'Denmark': 'Europe', 'Spain': 'Europe', 'Estonia': 'Europe', 
    'Finland': 'Europe', 'France': 'Europe', 'United Kingdom': 'Europe', 'Georgia': 'Europe', 
    'Greece': 'Europe', 'Croatia': 'Europe', 'Hungary': 'Europe', 'Ireland': 'Europe', 
    'Iceland': 'Europe', 'Italy': 'Europe', 'Liechtenstein': 'Europe', 'Lithuania': 'Europe', 
    'Luxembourg': 'Europe', 'Latvia': 'Europe', 'Monaco': 'Europe', 'Moldova': 'Europe', 
    'Macedonia': 'Europe', 'Malta': 'Europe', 'Montenegro': 'Europe', 'Netherlands': 'Europe', 
    'Norway': 'Europe', 'Poland': 'Europe', 'Portugal': 'Europe', 'Romania': 'Europe', 
    'San Marino': 'Europe', 'Serbia': 'Europe', 'Slovakia': 'Europe', 'Slovenia': 'Europe', 
    'Sweden': 'Europe', 'Ukraine': 'Europe', 'Vatican City': 'Europe',

    'Angola': 'Africa', 'Burundi': 'Africa', 'Benin': 'Africa', 'Burkina': 'Africa', 
    'Botswana': 'Africa', 'Central African Republic': 'Africa', 'Ivory Coast': 'Africa', 
    'Cameroon': 'Africa', 'Congo, Democratic Republic of': 'Africa', 'Congo': 'Africa', 
    'Comoros': 'Africa', 'Cape Verde': 'Africa', 'Djibouti': 'Africa', 'Algeria': 'Africa', 
    'Egypt': 'Africa', 'Eritrea': 'Africa', 'Ethiopia': 'Africa', 'Gabon': 'Africa', 
    'Ghana': 'Africa', 'Guinea': 'Africa', 'Gambia': 'Africa', 'Guinea-Bissau': 'Africa', 
    'Equatorial Guinea': 'Africa', 'Kenya': 'Africa', 'Liberia': 'Africa', 'Libya': 'Africa', 
    'Lesotho': 'Africa', 'Morocco': 'Africa', 'Madagascar': 'Africa', 'Mali': 'Africa', 
    'Mozambique': 'Africa', 'Mauritania': 'Africa', 'Mauritius': 'Africa', 'Malawi': 'Africa', 
    'Namibia': 'Africa', 'Niger': 'Africa', 'Nigeria': 'Africa', 'Rwanda': 'Africa', 
    'Sudan': 'Africa', 'Senegal': 'Africa', 'Sierra Leone': 'Africa', 'Somalia': 'Africa', 
    'South Sudan': 'Africa', 'Sao Tome and Principe': 'Africa', 'Eswatini': 'Africa', 
    'Seychelles': 'Africa', 'Chad': 'Africa', 'Togo': 'Africa', 'Tunisia': 'Africa', 
    'Tanzania': 'Africa', 'Uganda': 'Africa', 'South Africa': 'Africa', 'Zambia': 'Africa', 
    'Zimbabwe': 'Africa',

    'Afghanistan': 'Asia', 'United Arab Emirates': 'Asia', 'Bangladesh': 'Asia', 'Bahrain': 'Asia', 
    'Brunei': 'Asia', 'Bhutan': 'Asia', 'China': 'Asia', 'Hong Kong, China': 'Asia', 
    'Indonesia': 'Asia', 'India': 'Asia', 'Iran': 'Asia', 'Iraq': 'Asia', 'Israel': 'Asia', 
    'Jordan': 'Asia', 'Japan': 'Asia', 'Kazakhstan': 'Asia', 'Kyrgyzstan': 'Asia', 
    'Cambodia': 'Asia', 'Korea, South': 'Asia', 'Kuwait': 'Asia', 'Laos': 'Asia', 
    'Lebanon': 'Asia', 'Sri Lanka': 'Asia', 'Maldives': 'Asia', 'Burma (Myanmar)': 'Asia', 
    'Mongolia': 'Asia', 'Malaysia': 'Asia', 'Nepal': 'Asia', 'Oman': 'Asia', 'Pakistan': 'Asia', 
    'Philippines': 'Asia', 'Korea, North': 'Asia', 'Palestine': 'Asia', 'Qatar': 'Asia', 
    'Saudi Arabia': 'Asia', 'Singapore': 'Asia', 'Syria': 'Asia', 'Thailand': 'Asia', 
    'Tajikistan': 'Asia', 'Turkmenistan': 'Asia', 'East Timor': 'Asia', 'Turkey': 'Asia', 
    'Taiwan': 'Asia', 'Uzbekistan': 'Asia', 'Vietnam': 'Asia', 'Yemen': 'Asia',

    'Australia': 'Australia and Oceania', 'Fiji': 'Australia and Oceania', 'Micronesia': 'Australia and Oceania', 
    'Kiribati': 'Australia and Oceania', 'Marshall Islands': 'Australia and Oceania', 'Nauru': 'Australia and Oceania', 
    'New Zealand': 'Australia and Oceania', 'Palau': 'Australia and Oceania', 'Papua New Guinea': 'Australia and Oceania', 
    'Solomon Islands': 'Australia and Oceania', 'Tonga': 'Australia and Oceania', 'Tuvalu': 'Australia and Oceania', 
    'Vanuatu': 'Australia and Oceania', 'Samoa': 'Australia and Oceania'
}
country_to_continent['Russia'] = 'Europe, Asia'
country_colors = {}  
for country, continent in country_to_continent.items():
    if continent in continent_colors:
        country_colors[country] = continent_colors[continent]
top_country_colors = {
    'Denmark': '#93A4C2',
    'Finland': '#93A4C2',
    'Norway': '#93A4C2',
    'Switzerland': '#93A4C2',
    'Netherlands': '#93A4C2',
    'Iceland': '#93A4C2',
    'Canada': '#122981',
    'Sweden': '#93A4C2',
    'New Zealand': '#BF456B',
    'Australia': '#BF456B',
    'Haiti': '#122981',
    'Comoros': '#FBB345',
    'Yemen': '#FADCAA',
    'Tanzania': '#FBB345',
    'Rwanda': '#FBB345',
    'Afghanistan': '#FADCAA',
    'Burundi': '#FBB345',
    'Togo': '#FBB345',
    'Central African Republic': '#FBB345',
    'Sudan': '#FBB345'
}


##Figures:

map_happiness_static = px.choropleth(df_long, 
                              locations="country_code",
                              color="happiness_score",
                              hover_name="country",
                              labels={
                              'happiness_score': ' '
                          },
                              color_continuous_scale='RdYlBu',
                              range_color=[df_long['happiness_score'].min(), df_long['happiness_score'].max()],
                             projection='mercator')
map_happiness_static.update_layout(
    geo=dict(showframe=False, showcoastlines=False),
    margin=dict(t=50, l=0, r=0, b=0)
)
map_happiness_static.update_layout(
    coloraxis_colorbar=dict(
        orientation="h",  # Set colorbar to horizontal
        x=0.5,  # Center the colorbar horizontally relative to the plot
        xanchor="center",
        y=-0.05,  # Position it below the plot
        yanchor="bottom",
        len=0.7  # Adjust the length of the colorbar (optional)
    ),
    title={
        'text': 'OVERVIEW OF HAPPINESS SCORE FROM 2005 TO 2019',
        'y': 0.96,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    height=900, 
    width=1050)

#--------------------------------------------------



map_happiness = px.choropleth(df_long, 
                              locations="country_code",
                              color="happiness_score",
                              hover_name="country",
                              labels={
                              'happiness_score': ' '
                          },
                              animation_frame="year",
                              color_continuous_scale='RdYlBu',
                              range_color=[df_long['happiness_score'].min(), df_long['happiness_score'].max()],
                             projection='mercator')
map_happiness.update_layout(
    geo=dict(showframe=False, showcoastlines=False),
    margin=dict(t=50, l=0, r=0, b=0)
)
map_happiness.update_layout(
    coloraxis_colorbar=dict(
        orientation="h",  # Set colorbar to horizontal
        x=0.5,  # Center the colorbar horizontally relative to the plot
        xanchor="center",
        y=-0.05,  # Position it below the plot
        yanchor="bottom",
        len=0.7  # Adjust the length of the colorbar (optional)
    ),
    title={
        'text': 'GLOBAL OVERVIEW OF HAPPINESS',
        'y': 0.96,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    height=900, 
    width=1050)

#--------------------------------------------------


scatt_hap_income = px.scatter(happiness_income,
                            x='avg_daily_income',
                            y='happiness_score',
                          labels={
                              'avg_daily_income': 'Average Daily Income (USD)',
                              'happiness_score': 'Happiness Score (Index)',
                               'year': 'Year ',
                              'continent': ' Continent '
                          },
                            color='continent',
                             animation_frame="continent",
                          color_discrete_map=continent_colors,
                          hover_name='country',
                         range_y=[0,100],
                        range_x=[happiness_income['avg_daily_income'].min(), happiness_income['avg_daily_income'].max()])
scatt_hap_income.update_layout(
    title={
        'text': 'HAPPINESS & AVERAGE DAILY INCOME',
        'y': 0.97,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    height=600, 
    width=700,
    template='plotly_white',
    showlegend=False)

scatt_hap_income.update_traces(marker=dict(size=8,
                              line=dict(width=0.5,
                                        color='DarkSlateGrey')))
scatt_hap_income.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 3000


#--------------------------------------------------

scatt_ine_income = px.scatter(happiness_income,
                            x='income_inequality',
                            y='happiness_score',
                          labels={
                              'income_inequality': 'Income Inequality : Gini coefficient [0 to 100]',
                              'happiness_score': 'Happiness Score (Index)',
                               'year': 'Year ',
                              'continent': ' Continent '
                          },
                            color='continent',
                             animation_frame="continent",
                          color_discrete_map=continent_colors,
                          hover_name='country',
                         range_y=[happiness_income['happiness_score'].min(), happiness_income['happiness_score'].max()],
                          range_x=[0,100])
scatt_ine_income.update_layout(
    title={
        'text': 'HAPPINESS & INCOME INEQUALITY',
        'y': 0.97,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    height=600, 
    width=700,
    template='plotly_white',
    showlegend=False)
scatt_ine_income.update_traces(marker=dict(size=8,
                              line=dict(width=0.5,
                                        color='DarkSlateGrey'),
                                      ))
scatt_ine_income.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 3000

#--------------------------------------------------

scatt_income = px.scatter(happiness_income,
                            x='income_inequality',
                            y='avg_daily_income',
                          labels={
                              'income_inequality': 'Income Inequality : Gini coefficient [0 to 100] ',
                              'avg_daily_income': 'Average Daily Income (USD) ',
                              'year': 'Year ',
                              'continent': ' Continent '
                          },
                            color='continent',
                             animation_frame="continent",
                          color_discrete_map=continent_colors,
                          hover_name='country',
                         range_y=[happiness_income['avg_daily_income'].min(), happiness_income['avg_daily_income'].max()],
                          range_x=[0,100]                         )
scatt_income.update_layout(
    title={
        'text': '  ',
        'y': 0.97,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    height=600, 
    width=700,
    template='plotly_white',
    showlegend=False)
scatt_income.update_traces(marker=dict(size=8,
                              line=dict(width=0.5,
                                        color='DarkSlateGrey'),
                                      ))
scatt_income.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 3000


#--------------------------------------------------

scatt_income_static = px.scatter(happiness_income,
                            x='income_inequality',
                            y='avg_daily_income',
                          labels={
                              'income_inequality': 'Income Inequality : Gini coefficient [0 to 100] ',
                              'avg_daily_income': 'Average Daily Income (USD) ',
                              'year': 'Year ',
                              'continent': ' Continent '
                          },
                            color='continent',
                          color_discrete_map=continent_colors,
                          hover_name='country',
                         range_y=[happiness_income['avg_daily_income'].min(), happiness_income['avg_daily_income'].max()],
                          range_x=[0,100]                         )
scatt_income_static.update_layout(
    title={
        'text': 'AVERAGE DAILY INCOME & INCOME INEQUALITY ',
        'y': 0.97,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    height=600, 
    width=700,
    template='plotly_white',
    showlegend=False)
scatt_income_static.update_traces(marker=dict(size=8,
                              line=dict(width=0.5,
                                        color='DarkSlateGrey'),
                                      ))

#--------------------------------------------------

scatt_hap_wom = px.scatter(happiness_gouv,
                            x='women_parliament',
                            y='happiness_score',
                            labels={
                               'women_parliament': 'Women participation in parliament [%]',
                              'happiness_score': 'Happiness Score (Index)',
                               'year': 'Year ',
                              'continent': ' Continent '
                          },
                            color='continent',
                             animation_frame="continent",
                          color_discrete_map=continent_colors,
                          hover_name='country',
                         range_y=[0,100],
                          range_x=[0,100])
scatt_hap_wom.update_layout(
    title={
        'text': 'HAPPINESS & WOMAN PARTICIPATION IN PARLIAMENT',
        'y': 0.97,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    height=900, 
    width=1000,
    template='plotly_white',
    showlegend=False)
scatt_hap_wom.update_traces(marker=dict(size=10,
                              line=dict(width=0.5,
                                        color='DarkSlateGrey'),
                                      ))
scatt_hap_wom.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 3000


#--------------------------------------------------

scatt_hap_gov = px.scatter(happiness_gouv,
                            x='functioning_government',
                            y='happiness_score',
                            labels={
                               'functioning_government': 'Index of functioning government (EIU) [0 to 100]',
                              'happiness_score': 'Happiness Score (Index)',
                               'year': 'Year ',
                              'continent': ' Continent '
                          },
                            color='continent',
                             animation_frame="continent",
                          color_discrete_map=continent_colors,
                          hover_name='country',
                         range_y=[0,100],
                          range_x=[0,100])
scatt_hap_gov.update_layout(
    title={
        'text': 'HAPPINESS & INDEX OF FUNCTIONING GOVERNMENT',
        'y': 0.97,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    height=900, 
    width=1000,
    template='plotly_white',
    showlegend=False)
scatt_hap_gov.update_traces(marker=dict(size=10,
                              line=dict(width=0.5,
                                        color='DarkSlateGrey'),
                                      ))
scatt_hap_gov.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 3000


#--------------------------------------------------

scatt_gov_dem = px.scatter(happiness_gouv,
                            x='functioning_government',
                            y='democracy',
                           labels={
                               'functioning_government': 'Index of functioning government (EIU) [0 to 100]',
                              'democracy': 'Democracy Index [0 to 100]',
                               'year': 'Year ',
                              'continent': ' Continent '
                          },
                            color='continent',
                             animation_frame="year",
                          color_discrete_map=continent_colors,
                          hover_name='country',
                         range_y=[0,100],
                          range_x=[0,100])
scatt_gov_dem.update_layout(
    title={
        'text': 'INDEX OF FUNCTIONING GOVERNMENT & INDEX OF DEMOCRACY',
        'y': 0.97,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    height=900, 
    width=1000,
    template='plotly_white',
    legend=dict(
        orientation="h",  # Horizontal layout
        yanchor="bottom",
        y=-0.3,  # Places legend below the x-axis
        xanchor="center",
        x=0.5   # Centers the legend
    ))
scatt_gov_dem.update_traces(marker=dict(size=10,
                              line=dict(width=0.5,
                                        color='DarkSlateGrey'),
                                      ))
scatt_gov_dem.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000

#--------------------------------------------------

happ_countr= px.line(filter_hap_income,
                          x='year',
                          y='happiness_score',
                          labels={
                              'happiness_score': 'Happiness Score',
                              'year': 'Year'
                          },
                           #animation_frame="country",
                          color='country',
                          color_discrete_map=country_colors,
                          hover_name='country',
                         range_y=[36,78]
                         )
happ_countr.update_layout(
    title={
        'text': 'EVOLUTION OF HAPPINESS SCORE ON SPECIFIC COUNTRIES',
        'y': 0.96,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    height=900,
    width=1100,
    template='plotly_white',
    showlegend=None,
    
)
happ_countr.update_traces(line=dict(width=2))

#--------------------------------------------------

scatt_happ_avg_countr = px.scatter(filter_hap_income,
                            x='avg_daily_income',
                            y='happiness_score',
                            #size='population',
                          #size_max=50,
                          labels={
                              'avg_daily_income': 'Average Daily Income (USD)',
                              'happiness_score': 'Happiness Score (Index)',
                               'year': 'Year ',
                              'continent': ' Continent '
                          },
                            color='country',
                             animation_frame="country",
                          color_discrete_map=country_colors,
                          hover_name='country',
                         range_y=[0,100],
                        range_x=[happiness_income['avg_daily_income'].min(), happiness_income['avg_daily_income'].max()])
scatt_happ_avg_countr.update_layout(
    title={
        'text': 'HAPPINESS & AVERAGE DAILY INCOME',
        'y': 0.97,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    height=900, 
    width=1100,
    template='plotly_white',
    showlegend=None)
scatt_happ_avg_countr.update_traces(marker=dict(size=12,
                              line=dict(width=0.5,
                                        color='DarkSlateGrey'),
                                      ))
scatt_happ_avg_countr.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 1000

#--------------------------------------------------

 #bar avg happines score continent
bar_avg_cont = px.bar(continent_count_distr,
                 x='continent',
                  y='mean_year_score',       # Size of segments based on happiness score
                  color='continent',              # Color segments by continent
                  color_discrete_map=continent_colors,
            labels={
                                'mean_year_score': 'Avg Happiness Score ',
                               'year': 'Year ',
                              'continent': ' Continent ',
                              'country' : 'Country'
                          },)  # Color scale: adjust if you use categorical coloring

bar_avg_cont.update_layout(
    title={
        'text': 'GLOBAL HAPPINESS SCORE DISTRIBUTION PER CONTINENT',
        'y': 0.97,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    barmode='overlay',
    height=900, 
    width=1100,
    template='plotly_white',
    legend=dict(
        orientation="h",  # Horizontal layout
        yanchor="bottom",
        y=-0.12,  # Places legend below the x-axis
        xanchor="center",
        x=0.5))   # Centers the legend
    
#--------------------------------------------------

fig = make_subplots(rows=1, cols=2, subplot_titles=('Highest Total Average Happiness Score', 
                                                     'Lowest Total Average Happiness Score'), shared_yaxes=True)
top_10 = px.bar(hap_top,
                        x='country',
                            y='happiness_score',
                          labels={
                                'happiness_score': 'Happiness score ',
                               'year': 'Year ',
                              'continent': ' Continent ',
                              'country' : 'Country'
                          },
                            color='continent',
                          color_discrete_map=continent_colors,
                          hover_name='country'
                  )
bottom_10 = px.bar(hap_bottom,
                        x='country',
                            y='happiness_score',
                          labels={
                                'happiness_score': 'Happiness score ',
                               'year': 'Year ',
                              'continent': ' Continent ',
                              'country' : 'Country'
                          },
                            color='continent',
                          color_discrete_map=continent_colors,
                          hover_name='country'
                  )

for trace in top_10.data:
    trace.showlegend = True
    fig.add_trace(trace, row=1, col=1)

for trace in bottom_10.data:
    trace.showlegend = True
    fig.add_trace(trace, row=1, col=2)

fig.update_yaxes(range=[0, 100], row=1, col=1)
fig.update_yaxes(range=[0, 100], row=1, col=2)

fig.update_layout(
    barmode='overlay',
    height=600, 
    width=1100,
    template='plotly_white',
    legend=dict(
        orientation="h",  # Horizontal layout
        yanchor="bottom",
        y=-0.4,  # Places legend below the x-axis
        xanchor="center",
        x=0.5 ))



#--------------------------------------------------

happ_top_bot['year'] = happ_top_bot['year'].astype(int)
line_top_bot = px.line(happ_top_bot, x='year', y='happiness_score', color='country', 
              color_discrete_map=top_country_colors,
                       labels={
                                'happiness_score': 'Happiness Score (Index) ',
                               'year': 'Year ',
                              'continent': ' Continent ',
                           'country':'Country '
                          },
                hover_name='continent',
              markers=False)  # Include markers for each data point

line_top_bot.update_layout(
    title={
        'text': 'Happiness Score Top 10 and Bottom 10 Countries',
        'y': 0.97,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    height=900, 
    width=1050,
    template='plotly_white',
    legend=dict(
        orientation="h",  # Horizontal layout
        yanchor="bottom",
        y=-0.3,  # Places legend below the x-axis
        xanchor="center",
        x=0.5   # Centers the legend
    )
    #plot_bgcolor='rgba(0, 0, 0, 0)',
     #paper_bgcolor='rgba(0, 0, 0, 0)',

)

#--------------------------------------------------


line_wom = px.line(average_participation,
                            x='year',
                            y='women_parliament',
                          labels={
                                'women_parliament': 'Average Women participation in parliament per Continent[%]',
                               'year': 'Year ',
                              'continent': ' Continent '
                          },
                            color='continent',
                          color_discrete_map=continent_colors,)
line_wom.update_layout(
    title={
        'text': 'WOMEN PARTICIPATION IN PARLIAMENT [%]',
        'y': 0.97,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    height=900, 
    width=1100,
    template='plotly_white',
    legend=dict(
        orientation="h",  # Horizontal layout
        yanchor="bottom",
        y=-0.3,  # Places legend below the x-axis
        xanchor="center",
        x=0.5   # Centers the legend
    ))

line_wom_happ = go.Figure(line_wom)
for continent in average_participation['continent'].unique():
    # Filter data for the continent
    continent_data = average_participation[average_participation['continent'] == continent]
    # Add trace
    line_wom_happ.add_trace(
        go.Scatter(
            x=continent_data['year'],
            y=continent_data['happiness_score'],
            line=dict(color=continent_colors[continent], width=5),
            name=f'{continent}',  # Naming to differentiate
            yaxis='y2'  # This specifies the use of the secondary y-axis
        )
    )
line_wom_happ.update_layout(
    title={
        'text': "Trends in Women's Parliamentary Participation and Happiness Scores by Continent",
        'y': 0.97,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    yaxis2=dict(
        title='Average Happiness Score',
        overlaying='y',  # Ensures the second y-axis overlays the first
        side='right',  # Positions the axis to the right side
        showgrid=False  # Optional: turns off grid for the second y-axis
    ),
    height=900, 
    width=1100,
    template='plotly_white',
    legend=dict(
        orientation="h",  # Horizontal layout
        yanchor="bottom",
        y=-0.2,  # Places legend below the x-axis
        xanchor="center",
        x=0.5   # Centers the legend
    )

)

#--------------------------------------------------



bar_wom = px.bar(happiness_gouv,
                        x='year',
                            y='women_parliament',
                          labels={
                                'women_parliament': 'Average Women participation in parliament per Continent[%]',
                               'year': 'Year ',
                              'continent': ' Continent '
                          },
                            color='continent',
                          barmode='group',
                          color_discrete_map=continent_colors,
                          hover_name='country'
                         #,range_x=[0,10000]
                  )

bar_wom.update_layout(
    title={
        'text': 'Women Participation in Parliament [%] from 2006 to 2020',
        'y': 0.97,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    height=900, 
    width=1100,
    template='plotly_white',
    legend=dict(
        orientation="h",  # Horizontal layout
        yanchor="bottom",
        y=-0.3,  # Places legend below the x-axis
        xanchor="center",
        x=0.5   # Centers the legend
    )
)


        
#PNG :

bar_happ_top_bot = './visu/bar_happ_top_bot.png' #bar plot comparative for top and bottom countries
bar_wome = './visu/bar_wom.png' # women participation per country
box_happ_top_bot = './visu/box_happ_top_bot.png'  #box distribution happiness score from top and bottom
line_happ_cont = './visu/line_happ_cont.png'  #line happiness score continent 
line_happ_top_bot = './visu/line_happ_top_bot.png'    #line happiness score top bottom 
line_happ_wom = './visu/line_happ_wom.png'  #line happiness woman parliament evolution in years
map_avg_happ = './visu/map_avg_happ.png' #map global avg

scatt_gov_dem = './visu/scatt_gov_dem.png'  #scatt index of funtioning goverment and democracy
scatt_happ_cont = './visu/scatt_happ_cont'  #scatt happiness per continent, distribution over the years
scatt_happ_demo = './visu/scatt_happ_demo.png'  #scatt happiness democracy
scatt_happ_gov = './visu/scatt_happ_gov.png'  #scatt happiness govermnent
scatt_happ_incom = './visu/scatt_happ_incom.png'  #scatt happiness avg income
scatt_happ_wom = './visu/scatt_happ_wom.png' #scatt happiness women parliament
scatt_income_avg_ineq = './visu/scatt_income_avg_ineq.png'  #scatt inequality and  avg income 





app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1('REPORT FOR INTERNATIONAL DAY OF HAPPINESS', style={'text-align': 'center', 'font-family': 'Helvetica, Arial, sans-serif', 'margin-top' : '100px', 'margin-bottom' : '300px'}),
    
    
    html.Div([
        html.Img(src=dash.get_asset_url('happiness_analysis_logo.png'), style={'width': '20%', 'display': 'inline-block', 'margin-bottom' : '100px'})
], style={'text-align': 'center'}),
    html.H2('  ', style={'text-align': 'center', 'font-family': 'Helvetica, Arial, sans-serif'}),
    html.H2('  ', style={'text-align': 'center', 'font-family': 'Helvetica, Arial, sans-serif', 'margin-bottom' : '200px'}),
    html.Div([
        html.H5('  ', style={'text-align': 'center', 'font-family': 'Helvetica, Arial, sans-serif'}),
        dcc.Graph(figure=map_happiness, style={
        'width': '70%',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-bottom' : '50px'
    })  
    ]),
    html.Div([
        html.H3('   ', style={'text-align': 'center', 'font-family': 'Helvetica, sans-serif'}),
        dcc.Graph(figure=map_happiness_static, style={
        'width': '70%',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-bottom' : '200px'
    })
    ]),

    html.H2('COMPARATIVE ANALYSIS OF TOP AND BOTTOM COUNTRIES', style={'text-align': 'center', 'font-family': 'Helvetica, sans-serif', 'margin-bottom' : '50px'}),
    html.Div([
    #    dcc.Graph(figure=fig, style={
    #    'width': '70%',
    #    'display': 'block',
    #    'margin-left': 'auto',
    #    'margin-right': 'auto',
    #    'margin-bottom' : '200px'
    #}),
        html.Img(src=dash.get_asset_url('box_happ_top_bot.png'), style={'width': '49%', 'display': 'inline-block'}),
        html.Img(src=dash.get_asset_url('line_happ_top_bot.png'), style={'width': '49%', 'display': 'inline-block'})
    ], style={'margin-bottom' : '200px'}),

    html.H2('SOCIOECONOMIC AND POLITICAL FACTORS', style={'text-align': 'center', 'font-family': 'Helvetica, sans-serif'}),
    html.Div([

        html.Img(src=dash.get_asset_url('scatt_happ_incom.png'), style={'width': '49%', 'display': 'inline-block', 'margin-bottom' : '200px'}),
        html.Img(src=dash.get_asset_url('scatt_happ_wom.png'), style={'width': '49%', 'display': 'inline-block', 'margin-bottom' : '200px'}),
        dcc.Graph(figure=bar_wom, style={
        'width': '70%',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-bottom' : '100px',
        'margin-top' : '100px'
    }),
        html.Img(src=dash.get_asset_url('scatt_happ_gov.png'), style={'width': '49%', 'display': 'inline-block','margin-bottom' : '200px'}),
        html.Img(src=dash.get_asset_url('scatt_gov_dem.png'), style={'width': '49%', 'display': 'inline-block','margin-bottom' : '200px'}),
        dcc.Graph(figure=scatt_hap_gov, style={
        'width': '70%',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-bottom' : '50px'
    }),
        dcc.Graph(figure=scatt_hap_wom, style={
        'width': '70%',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-bottom' : '50px'
    }),
    ]),

    html.H2('INCOME ANALYSIS', style={'text-align': 'center', 'font-family': 'Helvetica, sans-serif', 'margin-top' : '200px', 'margin-bottom' : '200px'}),
    html.Div([
        dcc.Graph(figure=scatt_hap_income, style={
        'width': '49%', 'display': 'inline-block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-bottom' : '200px'
    }),
        dcc.Graph(figure=scatt_ine_income, style={
        'width': '49%', 'display': 'inline-block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-bottom' : '200px'
    }),
        dcc.Graph(figure=scatt_income_static, style={
        'width': '49%', 'display': 'inline-block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-bottom' : '200px'
    }),
        #html.Img(src=dash.get_asset_url('scatt_income_avg_ineq.png'), style={'width': '100%', 'display': 'inline-block'}),
        dcc.Graph(figure=scatt_income, style={
        'width': '49%', 'display': 'inline-block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-bottom' : '200px'
    })  # Assuming 'scatt_income' is a Plotly figure object
    ]),

    html.H2('REGIONAL & CONTINENTAL ANALYSIS', style={'text-align': 'center', 'font-family': 'Helvetica, sans-serif'}),
    html.Div([
        html.Img(src=dash.get_asset_url('line_happ_cont.png'), style={'width': '49%', 'display': 'inline-block', 'margin-top' : '100px'}),
        html.Img(src=dash.get_asset_url('scatt_happ_cont.png'), style={'width': '49%', 'display': 'inline-block', 'margin-top' : '100px'}),
        dcc.Graph(figure=line_wom_happ, style={
        'width': '70%',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top' : '200px',
        'margin-bottom' : '200px'
    })
    ]),

    html.H2('COUNTRY-SPECIFIC INSIGHTS', style={'text-align': 'center', 'font-family': 'Helvetica, sans-serif','margin-top' : '200px'}),
    html.Div([
        dcc.Graph(figure=happ_countr, style={
        'width': '70%',
        'display': 'block',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-top' : '100px',
        'margin-bottom' : '200px'
    }),
        dcc.Graph(figure=scatt_happ_avg_countr, style={
        'width': '70%',
        'display': 'block',
        'margin-top': '100px',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-bottom' : '500px'
    })
    ]),

    html.Div([
        dcc.Graph(figure=fig, style={
        'width': '70%',
        'display': 'block',
        'margin-top': '100px',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'margin-bottom' : '500px'
    })
    ]),

])

if __name__ == '__main__':
    app.run_server(debug=True)