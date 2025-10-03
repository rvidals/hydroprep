import os 
import pandas as pd 
import numpy as np

def ler_csv(arquivo_csv, cod_estacao, dt_inicio, dt_fim, encoding="utf-8"):
    """Lê o csv."""
    df = pd.read_csv(arquivo_csv, sep='\t', encoding=encoding, engine='python')
    # Corrigir nomes das colunas para remover aspas e facilitar o acesso
    df.columns = [col.strip().replace('"', '') for col in df.columns]
    
    # Normalizar o nome da coluna de código da estação
    if "Cod.estacao" in df.columns:
        df.rename(columns={"Cod.estacao": "cod_estacao"}, inplace=True)
    if "Cod_estacao" in df.columns:
        df.rename(columns={"Cod_estacao": "cod_estacao"}, inplace=True)
    
    # Converter a coluna Data para datetime
    if "Data" in df.columns:
        df["Data"] = pd.to_datetime(df["Data"], errors='coerce')
    else:
        raise ValueError('Coluna "Data" não encontrada no arquivo CSV')
    
    # Filtrar pelos parâmetros
    df = df[df["cod_estacao"] == cod_estacao]
    df = df[(df["Data"] >= pd.to_datetime(dt_inicio)) & (df["Data"] <= pd.to_datetime(dt_fim))]
    return df

if __name__ == "__main__":
    arquivo_plu = os.path.join(os.getcwd(), "PLU_Series_ANA.txt")
    
    # DADOS DE CHUVAS
    # 1547010
    df_1547010 = ler_csv(arquivo_plu, 1547010, '1971-01-01', '2023-12-31') # Base 

    # 1547038
    df_1547038 = ler_csv(arquivo_plu, 1547038, '2007-01-01', '2009-12-31') # Preenchimento

    # 1547089
    df_1547089 = ler_csv(arquivo_plu, 1547089, '2017-01-01', '2021-12-31') # Preenchimento
    
    
    # PREENCHIMENTO
    dados_pt1_b = df_1547010[(df_1547010['Data'] >= '1971-01-01') & (df_1547010['Data'] <= '2006-12-31')]
    
    dados_pt1_p = df_1547038[(df_1547038['Data'] >= '2007-01-01') & (df_1547038['Data'] <= '2009-12-31')]
    dados_pt1_p['cod_estacao'] = 1547010
    
    dados_pt2_b = df_1547010[(df_1547010['Data'] >= '2010-01-01') & (df_1547010['Data'] <= '2016-12-31')]
    
    dados_pt2_p = df_1547089[(df_1547089['Data'] >= '2017-01-01') & (df_1547089['Data'] <= '2021-12-31')]
    dados_pt2_p['cod_estacao'] = 1547010
    
    dados_pt3_b = df_1547010[(df_1547010['Data'] >= '2022-01-01') & (df_1547010['Data'] <= '2023-12-31')]
    
    del df_1547010, df_1547038, df_1547089

    # Concatenar com o dataframe final
    
    
    df_final = pd.concat([dados_pt1_b, dados_pt1_p, dados_pt2_b, dados_pt2_p, dados_pt3_b]).reset_index(drop=True)
    
    cod_estacao = df_final['cod_estacao'].iloc[0]
    print(f'Estação: {cod_estacao} - Total de registros: {len(df_final)}')
    print(f'Período: {df_final["Data"].min().date()} a {df_final["Data"].max().date()}')
    print(f'Total de dados faltantes: {df_final["Chuva"].isna().sum()}')
    print(f'Total de dados preenchidos: {df_final["Chuva"].notna().sum()}')
    print(f'Porcentagem de dados faltantes: {df_final["Chuva"].isna().mean() * 100:.2f}%')
    
    # Exportar o dataframe final para um novo arquivo CSV
    df_final.to_csv(f"serie_chuva_{cod_estacao}_preenchida.csv", index=False)
