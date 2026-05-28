import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meu Histórico Spotify", page_icon="🎵", layout="wide")

st.title("🎵 Análise do Histórico de Streaming — Spotify")
st.markdown("Dados exportados diretamente da minha conta Spotify.")

# ── 1. Carregar CSV ──────────────────────────────────────────────
df = pd.read_csv('spotify_history.csv', parse_dates=['ts'])

st.success(f"✅ CSV carregado com **{len(df):,}** registros")

# ── 2. Sidebar com filtros ───────────────────────────────────────
st.sidebar.header("🔎 Filtros")
tipo = st.sidebar.radio("Tipo de conteúdo", ["Músicas", "Podcasts", "Tudo"])

if tipo == "Músicas":
    df = df[df['master_metadata_track_name'].notna()]
elif tipo == "Podcasts":
    df = df[df['episode_name'].notna()]

# ── 3. Métricas rápidas ──────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("🎧 Streams totais", f"{len(df):,}")
col2.metric("⏱️ Horas ouvidas", f"{df['minutos_ouvidos'].sum() / 60:,.0f}h")
col3.metric("🎤 Artistas únicos", f"{df['master_metadata_album_artist_name'].nunique():,}")

st.divider()

# ── 4. Gráfico: Top 10 Artistas ──────────────────────────────────
st.subheader("🏆 Top 10 Artistas mais ouvidos")
top_artists = (
    df.groupby('master_metadata_album_artist_name')['minutos_ouvidos']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)
top_artists.columns = ['Artista', 'Minutos Ouvidos']

fig1 = px.bar(
    top_artists,
    x='Minutos Ouvidos',
    y='Artista',
    orientation='h',
    color='Minutos Ouvidos',
    color_continuous_scale='Greens',
    text=top_artists['Minutos Ouvidos'].round(0).astype(int)
)
fig1.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
st.plotly_chart(fig1, use_container_width=True)

# ── 5. Gráfico: Streams por Mês ──────────────────────────────────
st.subheader("📅 Streams por mês")
df['mes'] = df['ts'].dt.to_period('M').astype(str)
streams_mes = df.groupby('mes').size().reset_index(name='Streams')

fig2 = px.line(streams_mes, x='mes', y='Streams', markers=True,
               color_discrete_sequence=['#1DB954'])
fig2.update_xaxes(title="Mês")
st.plotly_chart(fig2, use_container_width=True)

# ── 6. Tabela: Músicas mais tocadas ─────────────────────────────
st.subheader("🎵 Músicas mais tocadas")
top_tracks = (
    df[df['master_metadata_track_name'].notna()]
    .groupby(['master_metadata_track_name', 'master_metadata_album_artist_name'])
    .agg(plays=('ts', 'count'), minutos=('minutos_ouvidos', 'sum'))
    .sort_values('plays', ascending=False)
    .head(20)
    .reset_index()
)
top_tracks.columns = ['Música', 'Artista', 'Plays', 'Minutos']
top_tracks['Minutos'] = top_tracks['Minutos'].round(1)
st.dataframe(top_tracks, use_container_width=True)

st.caption("Fonte: dados exportados da conta pessoal no Spotify")
