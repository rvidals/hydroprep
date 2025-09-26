import os
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm   # Acrescentado tqdm para barra de progresso
from calendar import monthrange # Cria uma lista de tuplas (mês, dia) apenas para datas válidas


def gerar_pcp1_pcp(df_estacao, df_dados, nome_arquivo='pcp1.pcp'):
    
    # Chegar se o df_estacao e df_dados não estão vazios
    if df_estacao.empty or df_dados.empty:
        raise ValueError("DataFrames de estação ou dados estão vazios.")
    
        
    # Quantidade de linhas do DataFrame de dados
    nrow = df_dados.shape[0]
    
    # Primeira data 
    primeira_data = df_dados.columns[0]
    
    # Converter para datetime
    dt = datetime.strptime(primeira_data, '%Y%m%d')

    # Gerar lista de datas
    datas = [dt + timedelta(days=i) for i in range(nrow)]

    # Converter para ano juliano
    anos_julianos = [f"{d.year}{d.timetuple().tm_yday:03d}" for d in datas]

    # Se quiser adicionar ao seu DataFrame já existente:
    df_julianio = pd.DataFrame({'ano_juliano': anos_julianos})
    
    # Concatenar DataFrames
    df_final = pd.concat([df_julianio, df_dados], axis=1)
    
    with open(nome_arquivo, 'w') as f:
        # Dados das estações
        nm_estacao = str(df_estacao['NAME'].values[0])
        lat_estacao = round(float(df_estacao['LAT'].values[0]),1)
        long_estacao = round(float(df_estacao['LONG'].values[0]),1)
        elev_estacao = int(df_estacao['ELEVATION'].values[0])

        f.write(f"Station  {nm_estacao}\n")
        f.write(f"Lati   {lat_estacao}\n")
        f.write(f"Long   {long_estacao}\n")
        f.write(f"Elev    {elev_estacao}\n")
        # Dados de chuva
        for _, row in tqdm(df_final.iterrows(), desc="Escrevendo dados de chuva"):
            # Formatar a linha de dados da chuva com 2 dígitos para o dia
            valor = float(row['19670101'])
            if valor == -99.0:
                f.write(f"{row['ano_juliano']}{float(row['19670101']):.1f}\n")
            elif valor > 99.9:
                f.write(f"{row['ano_juliano']}{float(row['19670101']):.1f}\n")
            elif valor == 0.0:
                f.write(f"{row['ano_juliano']}000.0\n")
            elif valor < 10.0:
                f.write(f"{row['ano_juliano']}00{float(row['19670101']):.1f}\n")
            else:
                f.write(f"{row['ano_juliano']}0{float(row['19670101']):.1f}\n")

    print(f"Arquivo {nome_arquivo} gerado com sucesso.")
    


if __name__ == "__main__":
    path_dados = 'p1547014.txt'
    path_estacao = 'precip.txt'
    
    df_dados = pd.read_csv(path_dados, sep=';', dtype=str)
    df_precip = pd.read_csv(path_estacao, sep=',', dtype=str)
    
    gerar_pcp1_pcp(df_precip, df_dados, nome_arquivo='pcp1.pcp')