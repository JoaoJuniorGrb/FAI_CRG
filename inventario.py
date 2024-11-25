import streamlit as st
import CoolProp.CoolProp as prop
from CoolProp.CoolProp import PropsSI,PhaseSI
from pathlib import Path
from PIL import Image
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.optimize import fsolve
import requests
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import requests
from io import BytesIO
import firebase_admin
from firebase_admin import credentials, storage, initialize_app
import json
from streamlit_autorefresh import st_autorefresh
import time
from datetime import datetime
import pytz
from firebase_admin import db
import firebase_admin
from firebase_admin import credentials, storage
import json
import control as ctrl
import plotly.graph_objects as go

url_imagem = "https://i0.wp.com/cdn.newspulpaper.com/wp-content/uploads/2024/06/05163805/Submarca-Fiedler-01.png?resize=1068%2C373&ssl=1"
# Esconde o cabeçalho e o rodapé padrão do Streamlit
st.set_page_config(page_title="Fiedler Automação", page_icon="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABwAAAAcCAMAAABF0y+mAAAAqFBMVEUuMo0rMI0oLY8lK48kKpARHJIwNIZiX3ZybXQFFZN2cWvUxS/55wj/7gD/8AD/8wDh0SAdJI9ZVnro1x//9gD/7wB+eGcWIJKPh1/u3ROakVZFRoExNYAmLIPz4RSFfmRNTH0qL44+QITLvTN4c2a4q0jBtD7JvD+VjV47PYfayyqqoE9gXnCIgGNbWXivpEtmY25SUnwAEJRKS34AAJamnFSflVfOwC7jtOtQAAAA/0lEQVR4AWIYcACgih60GIahAIDWippas1f7/79sXrLd4+BRlGTu/0pRNd3gNIGTTAtAhL+ITfkddVzPRxwJFHYXRshHxI/dL5vfqQlBxI7SbMGILKbl4WWwApBHXW8+d5stJLt9TDgPUJbw4B0TTODpHHysHOn78QKvK0LyIgfXjx3LqJS48pbF0fOw/0ZqFpWC+gQr27tGevVx+f4UM7/BFcABpfKLJEm8jzModxZqTboRn4Rfqttc26vRBa7/hInBF7Lp4/Sq2cMYj+enlbMRGDqep2Cy9N0Yzw/AogIn29JMwZAneRc+/S1Zq8RKaDfrlt6HLW0oQqAiw6AAACorHoO4OiwrAAAAAElFTkSuQmCC", layout="wide")

st.sidebar.markdown(
    f"<img src='{url_imagem}' style='width:200px;'/>",
    unsafe_allow_html=True
)
#remove estilo stream lit
remove_st_estilo = """
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
"""

st.markdown(remove_st_estilo,unsafe_allow_html=True)
#----------------------------------------------------------------
firebase_creds = dict(st.secrets["firebase"])


# Verifique se o Firebase já está inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'fiedlerapp2024.appspot.com',
        'databaseURL': 'https://fiedlerapp2024-default-rtdb.firebaseio.com'
    })

# Função para carregar o JSON diretamente do Storage
def load_(nome_arquivo):
    bucket = storage.bucket()
    blob = bucket.blob(nome_arquivo)  # Caminho relativo dentro do bucket
    file_data = blob.download_as_bytes()  # Baixa o conteúdo do arquivo como bytes
    return file_data

config = load_("config.yaml")
config = config.decode('utf-8')    
config = yaml.safe_load(config)
#st.write(config)


# Configurando a autenticação
authenticator = stauth.Authenticate(
        
        names=[user['name'] for user in config['credentials']['usernames'].values()],
        usernames=list(config['credentials']['usernames'].keys()),
        passwords=[user['password'] for user in config['credentials']['usernames'].values()],
        cookie_name=config['cookie']['name'],  # Verifique se isso está apontando para 'random_cookie_name'
        key=config['cookie']['key'],  # Verifique se a chave 'random_signature_key' está correta
        cookie_expiry_days=config['cookie']['expiry_days']

    )
# Criando a interface de login
name, authentication_status, username = authenticator.login('Login', 'sidebar')

#Inicial
if authentication_status:
    programas = ["Perda de Carga",'Equações de afinidade',"Propriedades Termodinâmicas","Placa de orificio","QHS","Sistemas de controle","Final", "Base Instalada",'Gestão de projetos']
    legendas1 = ["Cálculo de perda de carga",'Em desenvolvimento',"Fornece gráfico de propriedades termodinamicas selecionadas",'Em desenvolvimento','Em desenvolvimento','Em desenvolvimento',"Informações sobre o programa","Levantamentos","Informações sobre Projetos"]

applicativo = "Base Instalada"

if authentication_status == True:
    authenticator.logout('Logout', 'sidebar')
if authentication_status == False:
        st.error('Nome de usuário ou senha incorretos')
if authentication_status == None:
        st.warning('Por favor, insira suas credenciais')
#------------------------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------------------------------------

if applicativo == "Base Instalada":
    # Especifica o caminho do arquivo no bucket, sem o prefixo "gs://"
    file_path_isolutions = "isolutions/levantamento grundfos hidros_1.4"
    file_path_cargil = "levantamento cargil/resultado_final_cargil.json"
    resultado_final = load_(file_path_cargil).decode('utf-8')
    isolutions = load_(file_path_isolutions).decode('utf-8')

    if authentication_status:
        
        nome= name
        st.markdown(
            f"""
            <h1 style="text-align: left;">
                Bem-vindo, {nome}
            </h1>
            """,
            unsafe_allow_html=True)
        # Divisor personalizado com degradê de amarelo para azul
        st.markdown("""
        <hr style="border: 0; height: 16px; background: linear-gradient(to left, blue,blue,blue,blue,blue,yellow,yellow,blue);">
        """, unsafe_allow_html=True)

        df_original = pd.read_json(resultado_final)
        df_isoltutions = pd.read_json(isolutions)
        #st.dataframe(df_original)

        levantamento = st.selectbox('Levantamento', ('Base instalada Cargil', 'Isolutions Grundfos'))
        
#-----------------------------------------------------------dashboard------------------------------------------------

        if levantamento == 'Base instalada Cargil':        
            dashboard = st.selectbox('Pesquisa',('Geral','Tag'))
            df_original['PN'] = df_original['PN'].astype(str)
            df_original["arquivo"] = df_original["arquivo"].astype(str)
            df_bombas = df_original[df_original["PN"].str[-3:] == df_original["arquivo"].str[-3:]]
            df_peças = df_original[df_original["PN"].str[-3:] != df_original["arquivo"].str[-3:]]
            df_peças['PN'] = df_peças['PN'].astype(str)
            df_peças = df_peças['PN'].value_counts().reset_index()
            df_peças.columns = ['PN', 'Quantidade']
            df_peças = df_peças.sort_values(by='Quantidade', ascending=False).reset_index(drop=True)
            df_peças = pd.merge(df_peças,df_original[['PN','Description','Descrição','arquivo','TAG']] )
            df_peças = df_peças[['Descrição','Description', 'PN', 'Quantidade']]
            df_peças['Descrição'] = df_peças['Descrição'].astype(str)
            df_peças['Description'] = df_peças['Description'].astype(str)
            df_peças['PN'] = "(" + df_peças['PN'].astype(str) + ")"
            df_peças['DescriçãoPN'] = df_peças['Description'] + " " + df_peças['PN'].astype(str)
            df_peças['Quantidade'] = df_peças['Quantidade'].astype(float)
            df_peças = df_peças.drop_duplicates(subset=['PN'])
            lista_peças = df_peças['Description'].unique()
            df_peças_filtrado = df_peças
            tags = df_original['TAG'].unique()
    
            #st.subheader('bombas')
            #st.dataframe(df_original)
            # Configura a página para o modo widescreen
         
            if dashboard == 'Geral':
                #st.set_page_config(layout="wide")
                pecas_pesquisa = st.multiselect("Itens da pesquisa:", lista_peças, ['MECHANICAL SEAL', 'BEARING CARRIER', 'HOLDER BEARING', 'SPRING BEARING', 'HOUSING BEARING', 'BEARING', 'BEARING HOUSE', 'SHAFT', 'SHAFT SLEEVE', 'IMPELLER', 'IMPROSEAL', 'GASKET'])
                df_peças_filtrado = df_peças_filtrado[df_peças_filtrado['Description'].isin(pecas_pesquisa)]
                st.subheader('peças',anchor=False)
                dsh1, dsh2 = st.columns([0.2,0.3], gap='small')
                with dsh1:
                        st.dataframe(df_peças_filtrado)
    
    
                # Criar gráfico básico com Plotly Express
                with dsh2:
                        bar_pecas = px.bar(df_peças_filtrado,y='Quantidade' , x='DescriçãoPN',)
                        #st.bar_chart(df_peças, x="Quantidade", y="PN", horizontal=False)
                        st.plotly_chart(bar_pecas)
    
            if dashboard == 'Tag':
                st.subheader('Tags',anchor=False)
                tags_pesquisa = st.multiselect("Tags da pesquisa:",tags)
                df_tags_filtrado = df_original[df_original['TAG'].isin(tags_pesquisa)]
                pecas_pesquisa_tag = st.multiselect("Peças para Tag selecionada", lista_peças,lista_peças)
                df_tags_filtrado = df_tags_filtrado[df_tags_filtrado['Description'].isin(pecas_pesquisa_tag)]
                st.dataframe(df_tags_filtrado,use_container_width=True)
        
        
        
