import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

nba_data = pd.read_csv("nba_all_elo.csv")    # Cargar Dataset de NBA

# Valores únicos
año = nba_data['year_id'].unique().tolist()
equipo = nba_data['team_id'].unique().tolist()

año.sort(reverse=True)     # Se ordenan los año para mostrarlo en orden

with st.sidebar:               # Barra lateral
    st.header("Selecciones los valores para mostrar las estadistica de un equipo")
    
    # Selector para el año
    selecionar_año = st.selectbox(label="Seleccionar año:", options=año, index=0)
    
    # Selector para el equipo
    selecionar_equipo = st.selectbox(label="Seleccionar equipo:", options=equipo, index=0)
    
    # Selector de pills)
    pills = st.radio(label="Seleccionar pills:", options=["Regular", "Playoffs", "Ambos"], index=0)

# Filtros
filter_NBA = nba_data[
    (nba_data['year_id'] == selecionar_año) & 
    (nba_data['team_id'] == selecionar_equipo)]

if pills == "Regular":
    filter_NBA = filter_NBA[filter_NBA['is_playoffs'] == False]
elif pills == "Playoffs":
    filter_NBA = filter_NBA[filter_NBA['is_playoffs'] == True]

filter_NBA = filter_NBA.sort_values('gameorder')   # ORdenar el orden de los juegos para calcular el acumulado


# Victorias y derrotas acumuladas
wins_Ac = []
losses_Ac = []
wins = 0
losses = 0

filter_NBA = filter_NBA.sort_values('date_game')    # Ordenar por fecha

filter_NBA['date_game'] = pd.to_datetime(filter_NBA['date_game'])   # Pasar a datetime

filter_NBA['month'] = filter_NBA['date_game'].dt.to_period('M')

# Acumulado por mes
acumulado = filter_NBA.groupby('month').agg({
    'game_result': [('wins', lambda x: (x == 'W').sum()), 
                   ('losses', lambda x: (x == 'L').sum())]
}).reset_index()

acumulado.columns = ['month', 'wins', 'losses']

# Acumulado de victorias y derrotas
acumulado['wins_Ac'] = acumulado['wins'].cumsum()
acumulado['losses_Ac'] = acumulado['losses'].cumsum()

acumulado['month_2'] = acumulado['month'].astype(str)


st.title(f"Dashboard NBA - {selecionar_equipo} ({selecionar_año})")

# Mostrar estadísticas
total_games = len(filter_NBA)
total_wins = filter_NBA['game_result'].value_counts().get('W', 0)
total_losses = filter_NBA['game_result'].value_counts().get('L', 0)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Juegos", total_games)
with col2:
    st.metric("Victorias", total_wins)
with col3:
    st.metric("Derrotas", total_losses)

# Grafica 1, acumualdo de victorias y derrotas
st.subheader("Acumulado de Victorias y Derrotas")

if total_games > 0:
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    
    meses = acumulado['month_2']
    
    ax1.plot(meses, acumulado['wins_Ac'], 'g-', linewidth=2, label='Victorias', marker='o', markersize=6)
    ax1.plot(meses, acumulado['losses_Ac'], 'r-', linewidth=2, label='Derrotas', marker='o', markersize=6)
    
    ax1.set_xlabel('Orden de Juego')
    ax1.set_ylabel('Número de victorias / Derrotas')
    ax1.set_title(f'Acumulado de Victorias y Derrotas - {selecionar_equipo} ({selecionar_año})')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    plt.xticks(rotation=45)
    fig1.tight_layout()

    st.pyplot(fig1)
else:
    st.warning("No hay datos para estos filtros")

# Gráfica 2, de pastel
st.subheader("Distribución de Victorias y Derrotas")

if total_games > 0:
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    
    labels = ['Victorias', 'Derrotas']
    sizes = [total_wins, total_losses]
    colors = ["#604CAF", "#BE36F4"]
    explode = (0.1, 0)
    
    ax2.pie(sizes, explode=explode, labels=labels, colors=colors, 
            autopct='%1.1f%%', shadow=True, startangle=90)
    ax2.axis('equal')
    
    st.pyplot(fig2)
else:
    st.warning("No hay datos para estos filtros")