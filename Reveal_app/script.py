from django.contrib.staticfiles.storage import staticfiles_storage

output = {  }

# %% [markdown]
# # REVEAL
# ### Your Real Estate Visualization and Exploration tool for Analytical Learning
# 
# 
# Used libraries :

# %%
import pandas as pd
import plotly.express as px
from plotly import graph_objects as go
import calendar

# %% [markdown]
# For the visual of the notebook :

# %%
import plotly.io as pio
pio.renderers.default='notebook'
pio.templates.default='plotly_dark'

# %% [markdown]
# ## 1 - Loading
# Load the data file directly with the usefull columns.

# %%
paths = {
    "2019" : "valeursfoncieres-2019.txt",
    "2020" : "valeursfoncieres-2020.txt",
    "2021" : "valeursfoncieres-2021.txt",
    "2022" : "valeursfoncieres-2022.txt",
}

used_colomns = [ "Date mutation", "Valeur fonciere", "No voie", "Type de voie", "Voie", "Code postal", \
        "Type local", "Surface reelle bati", "Nombre pieces principales", "Surface terrain", "Commune", "Code departement" ]


datas = {  }

def load_data():
    global datas
    global data_population

    print("Loading data...")

    for period, path in paths.items():
        datas[period] = pd.read_csv(staticfiles_storage.path(path), sep='|', usecols=used_colomns, dtype={ "Code departement" : str })

# %% [markdown]
# Load France population for deeper analysis.

# %%
    data_population = pd.read_csv(staticfiles_storage.path("population-dep.csv"), sep=';', usecols=['Code Département', 'Population'])
    data_population.rename(columns={ "Code Département" : "Code departement" }, inplace=True)
    data_population.sort_values(by="Code departement", inplace=True)
    data_population.head()

# %% [markdown]
# ## 2 - Cleaning

# %% [markdown]
# Real estate value of 0€, surface of 0m^2, room count of 0, are non-sense.

# %%
    for data in datas.values():
        data.dropna(subset=["Valeur fonciere", "Surface reelle bati", "Nombre pieces principales"], inplace=True)

        data["Date mutation"] = pd.to_datetime(data["Date mutation"], format='%d/%m/%Y')

        data["Valeur fonciere"] = data["Valeur fonciere"].str.replace(',', '.').astype(float)
        data["Nombre pieces principales"] = data["Nombre pieces principales"].astype(int)

        data.drop(data[data["Surface reelle bati"] == 0].index, inplace=True)
        data.drop(data[data["Nombre pieces principales"] == 0].index, inplace=True)

    print("Data loaded.")

data = pd.DataFrame()

def select_period(period):
    global data
    data = datas[period].copy()
    return data

def make_charts(data):
# %% [markdown]
# ## 3 - Filtering

# %%
    price_min = 0
    price_max = 1000000

    data = data[data["Valeur fonciere"].between(left=price_min, right=price_max)]

# %% [markdown]
# ## 4 - Interpreting and visualizing

# %% [markdown]
# **Real estate value

# %%
    s = data.groupby(data["Date mutation"].dt.month)["Valeur fonciere"].mean()

    fig = px.line(x=list(calendar.month_name)[1:], y=s.values, labels={'x':'', 'y':''})
    output["Valeur foncière"] = fig.to_html(full_html=False)

# %% [markdown]
# **Real estate value

# %%
    s = data.groupby(data["Date mutation"].dt.month)["Valeur fonciere"].count()

    fig = px.bar(x=list(calendar.month_name)[1:], y=s.values, labels={'x':'', 'y':''})
    output["Nombre de ventes"] = fig.to_html(full_html=False)

# %% [markdown]
# **Mean square meter price**

# %%
    data.insert(1, "Prix/m2", [ int(p/s) for p, s in zip(data["Valeur fonciere"], data["Surface reelle bati"]) ])
    data.head()

# %%
    s = data.groupby(data["Date mutation"].dt.month)["Date mutation"].count()

    fig = px.line(x=list(calendar.month_name)[1:], y=list(s.values), labels={'x':'', 'y':''})
    output["Prix moyen au mètre carré"] = fig.to_html(full_html=False)

# %% [markdown]
# **Real estate value by totale surface**

# %%
    fig = px.scatter(data.sample(1000), x="Surface reelle bati", y="Valeur fonciere", color="Type local")
    output["Valeur foncière par surface totale"] = fig.to_html(full_html=False)


# %% [markdown]
# **Sold surface**

# %%
    s = data.groupby(data["Date mutation"].dt.month)["Surface reelle bati"].mean()
    meanprice = list(s.values)

    fig = px.line(x=list(calendar.month_name)[1:], y=meanprice, labels={'x':'', 'y':''})
    output["Surface totale vendue"] = fig.to_html(full_html=False)

# %% [markdown]
# **Mean real estate value per department**

# %%
    s = data.groupby("Code departement")["Valeur fonciere"].mean()
    dep, meanprice = list(s.index), list(s.values)

    geojson="https://france-geojson.gregoiredavid.fr/repo/departements.geojson"

    fig = go.Figure(go.Choroplethmapbox(geojson=geojson, featureidkey = "properties.code", \
            locations=dep, z=meanprice, zauto = True, colorscale = 'viridis', showscale = True))
    fig.update_geos(scope="europe")
    fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=4, mapbox_center = {"lat": 47, "lon": 2.3522}, \
            margin={"r":0,"t":0,"l":0,"b":0})
    output["Valeur fonciere moyenne par département"] = fig.to_html(full_html=False)

# %% [markdown]
# **Mean square meter price per department**

# %%
    s = data.groupby("Code departement")["Prix/m2"].mean()
    dep, meanpricem2 = list(s.index), list(s.values)

    fig = go.Figure(go.Choroplethmapbox(geojson=geojson, featureidkey = "properties.code", \
            locations=dep, z=meanpricem2, zauto = True, colorscale = 'viridis', showscale = True))
    fig.update_geos(scope="europe")
    fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=4, mapbox_center = {"lat": 47, "lon": 2.3522}, \
            margin={"r":0,"t":0,"l":0,"b":0})
    output["Prix moyen au mètre carré par département"] = fig.to_html(full_html=False)

# %% [markdown]
# **Sale value by typologies** (limited to 6 rooms)

# %%
    s = data.groupby([data["Nombre pieces principales"], data["Date mutation"].dt.month])["Nombre pieces principales"].count()

    df = pd.DataFrame({str(i) + (" pièce" if i == 1 else " pièces") : s[i].tolist() for i in range(1, 7)})
    df.insert(0, "Date mutation", list(calendar.month_name)[1:])

    fig = px.bar(df, x="Date mutation", y=[str(i) + (" pièce" if i == 1 else " pièces") for i in range(1, 7)], labels={'value':'', 'Date mutation':''})
    output["Nombre de ventes par typologies"] = fig.to_html(full_html=False)

# %% [markdown]
# **Mean square meter price by typologies** (limited to 6 rooms)

# %%
    s = data.groupby("Nombre pieces principales")["Prix/m2"].mean()
    s = s.head(6)

    fig = px.bar(y=[str(x) + (" pièce" if x == 1 else " pièces") for x in s.index], x=s.values, orientation='h', labels={'y':'', 'x':'Prix/m2'})
    output["Prix moyen au mètre carré par typologies"] = fig.to_html(full_html=False)

# %% [markdown]
# **Mean typologie by department**

# %%
    s = data.groupby("Code departement")["Nombre pieces principales"].mean()
    dep, meantypo = s.index, s.values

    fig = go.Figure(go.Choroplethmapbox(geojson=geojson, featureidkey = "properties.code", \
            locations=dep, z=meantypo, zauto = True, colorscale = 'purples', showscale = True))
    fig.update_geos(scope="europe")
    fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=4, mapbox_center = {"lat": 47, "lon": 2.3522}, \
            margin={"r":0,"t":0,"l":0,"b":0})
    output["Typologie moyenne par département"] = fig.to_html(full_html=False)

# %% [markdown]
# **Mean square meter price by building types**

# %%
    s = data.groupby("Type local")["Prix/m2"].mean()

    fig = px.bar(y=s.index, x=s.values, orientation='h', labels={'y':'', 'x':'Prix/m2'})
    output["Prix moyen au mètre carré par type de batiments"] = fig.to_html(full_html=False)

# %% [markdown]
# **Share of typologies**

# %%
    s = data.groupby("Nombre pieces principales")["Nombre pieces principales"].count()
    s = s.head(20)

    fig = px.pie(names=[str(x) + (" pièce" if x == 1 else " pièces") for x in s.index], values=list(s.values))
    output["Part des typologies"] = fig.to_html(full_html=False)

# %% [markdown]
# **Share of buildings types**

# %%
    s = data.groupby("Type local")["Type local"].count()

    fig = px.pie(names=s.index, values=s.values)
    output["Part des types de batiments"] = fig.to_html(full_html=False)


# %% [markdown]
# **Real estate value by department population**

# %%
    dataj = data.merge(data_population, on="Code departement", how="left")

    s = dataj.groupby("Population")["Valeur fonciere"].mean()

    fig = px.line(x=s.index, y=s.values, labels={'x':'Population', 'y':'Real estate value'})
    output["Valeur fonciere par population"] = fig.to_html(full_html=False)

# %% [markdown]
# **Real estate value by department population**

# %%
    fig  = px.scatter_3d(dataj.sample(1000), x="Surface reelle bati", y="Population", z="Valeur fonciere", color = "Type local")
    output["Valeur foncière par surface totale et population"] = fig.to_html(full_html=False)

# %% [markdown]
# **Sale count by department population**

# %%
    s = dataj.groupby("Population")["Population"].count()

    fig = px.line(x=s.index, y=s.values, labels={'x':'Population', 'y':'Sales'})
    output["Nombre de ventes par population"] = fig.to_html(full_html=False)

# %% [markdown]
# **Mean sold surface by department population**

# %%
    s = dataj.groupby("Population")["Surface reelle bati"].mean()

    fig = px.line(x=s.index, y=s.values, labels={'x':'Population', 'y':'Sales'})
    output["Surface moyenne vendue par population"] = fig.to_html(full_html=False)

# %% [markdown]
# **Square meter price by department population**

# %%
    s = dataj.groupby("Population")["Prix/m2"].mean()

    fig = px.line(x=s.index, y=s.values, labels={'x':'Population', 'y':'Sales'})
    output["Prix moyen au mètre carré par population"] = fig.to_html(full_html=False)

# %%
    s = dataj.groupby(["Type local", "Population"])["Type local"].count()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s["Maison"].index, y=s["Maison"].values, mode='lines', name='Maison'))
    fig.add_trace(go.Scatter(x=s["Maison"].index, y=s["Appartement"].values, mode='lines', name='Appartement'))
    output["Type de batiments par population"] = fig.to_html(full_html=False)

    return output

def make_covid_charts():
    global datas
    output = {  }

# %% [markdown]
# **Real estate value

# %%
    fig = go.Figure()
    for period, data in datas.items():
        s = data.groupby(data["Date mutation"].dt.month)["Valeur fonciere"].count()
        fig.add_trace(go.Scatter(x=list(calendar.month_name)[1:], y=s.values, mode='lines', name=period))

    output["Nombre de ventes"] = fig.to_html(full_html=False)

# %% [markdown]
# **Total real estate value share

# %%
    counts = []
    for data in datas.values():
        count = data["Valeur fonciere"].sum()
        counts.append(count)

    fig = px.pie(names=datas.keys(), values=counts)
    output["Part de la valeur foncière totale sur 4 ans"] = fig.to_html(full_html=False)

# %% [markdown]
# **Total surface sold share

# %%
    counts = []
    for data in datas.values():
        count = data["Surface reelle bati"].sum()
        counts.append(count)

    fig = go.Figure(go.Treemap(
        labels=list(datas.keys()),
        parents=[""] * len(datas),
        values=counts,
        textinfo="label+text+value",
    ))
    output["Part de la surface vendue sur 4 ans"] = fig.to_html(full_html=False)

    return output
