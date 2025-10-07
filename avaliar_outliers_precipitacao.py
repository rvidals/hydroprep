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



def remover_outliers_lof(df):

    import matplotlib.pyplot as plt
    from pyod.models.lof import LOF

    """
    Remove outliers de precipitação diária usando LOF,
    salva gráfico, csv sem outliers e log de execução.
    """
    # Pasta de saída
    output_dir = 'Outlier Precipitação'
    os.makedirs(output_dir, exist_ok=True)

    # Cópia do dataframe
    df = df.copy()

    # Certifique-se que 'Data' é datetime
    df['Data'] = pd.to_datetime(df['Data'])
    df['mes'] = df['Data'].dt.month

    # Identificador da estação
    cod_estacao = str(df['cod_estacao'].unique()[0])

    # Detecta outliers por mês
    outlier_flags = np.zeros(df.shape[0], dtype=bool)
    for mes in range(1, 13):
        idx = df['mes'] == mes
        idx_valid = idx & df['Chuva'].notna()
        dados_mes = df.loc[idx_valid, 'Chuva'].values.reshape(-1, 1)

        if len(dados_mes) == 0:
            continue

        lof = LOF(contamination=0.05)
        lof.fit(dados_mes)
        preds = lof.labels_  # 1 = outlier, 0 = inlier
        outlier_flags[idx_valid] = preds.astype(bool)

    df['outlier'] = outlier_flags

    # Contar quantos outliers foram detectados
    num_outliers = int(df['outlier'].sum())
    log_msg = f"Número de outliers detectados: {num_outliers}\n"

    # --- GRÁFICO ---
    plt.figure(figsize=(15, 6))
    plt.scatter(df['Data'], df['Chuva'],
                c=df['outlier'].map({False: 'blue', True: 'red'}),
                s=df['outlier'].map({False: 10, True: 30}))
    plt.xlabel('Data')
    plt.ylabel('Precipitação (mm)')
    plt.title('Precipitação diária com outliers (Local Outlier Factor)')
    plt.legend(['Valor padrão', 'Outlier'])
    plt.tight_layout()
    img_path = os.path.join(output_dir, f'Gráfico de Precipitação diária com outliers (LOF) da Estação {cod_estacao}.png')
    plt.savefig(img_path)
    plt.close()

    # Salvar CSV sem outliers
    df.loc[df['outlier'], 'Chuva'] = np.nan
    df_out = df[['cod_estacao', 'NivelConsistencia', 'Data', 'Hora', 'Chuva']]
    csv_path = os.path.join(output_dir, f'serie_chuva_{cod_estacao}_sem_outliers_lof.csv')
    df_out.to_csv(csv_path, index=False)

    # Salvar log em txt
    txt_path = os.path.join(output_dir, f'log_{cod_estacao}.txt')
    with open(txt_path, 'a', encoding='utf-8') as log_file:
        log_file.write(log_msg)
        # Você pode adicionar mais logs, se quiser

    return df_out, img_path, csv_path, txt_path


if __name__ == "__main__":

    arquivo_plu = os.path.join(os.getcwd(), "PLU_Series_ANA.txt")
    
    # DADOS DE CHUVAS
    df_1547004 = ler_csv(arquivo_plu, 1547004, '1962-01-01', '2023-12-31')
    df_1548051 = ler_csv(arquivo_plu, 1548051, '2017-01-01', '2023-12-31')
    
    # Remover outliers usando LOF
    remover_outliers_lof(df_1547004)
    remover_outliers_lof(df_1548051)
