import os
import pandas as pd
from datetime import datetime
from tqdm import tqdm   # Acrescentado tqdm para barra de progresso

def ler_csv(arquivo_csv, cod_estacao, dt_inicio, dt_fim):
    """Lê o csv."""
    df = pd.read_csv(arquivo_csv, sep='\\t', engine='python')
    # Corrigir nomes das colunas para remover aspas e facilitar o acesso
    df.columns = [col.strip().replace('"', '') for col in df.columns]
    df.rename(columns={"Cod.estacao": "cod_estacao"}, inplace=True)
    df = df[df["cod_estacao"] == cod_estacao]
    df = df[(df["Data"] >= dt_inicio) & (df["Data"] <= dt_fim)]
    return df

def criar_arquivo_dados_vazao_SWATCUP_geral(df, var_nome: str, nome_arquivo: str, texto: str = "FLOW_OUT"):
    """Cria um arquivo de dados de vazão formatado."""

    df['n'] = df.index + 1
    df[var_nome] = df[var_nome].round(2)

    with open(f"{nome_arquivo}.txt", 'w') as f:

        for index, row in df.iterrows():
            data = row['Data']
            data = data.strftime("%d_%m_%Y")
            f.write(f"\t{texto}_{data}\t{row['n']}\t{row[var_nome]}\n")
        print(f"Arquivo '{nome_arquivo}' criado com sucesso.")

def criar_arquivo_dados_vazao_SWATCUP_condicionamento_dia(
    df, var_nome: str, nome_arquivo: int, condicao: str, texto: str = "FLOW_OUT", proporcao_cal: float = 0.7
):
    """
    Cria um arquivo de dados de vazão formatado e faz o split em anos completos.
    'condicao' pode ser 'cal' (calibração) ou 'val' (validação).
    'proporcao_cal' permite inverter: 0.3 para calibrar com 30% inicial, 0.7 padrão para 70% inicial.
    """

    # Nome do arquivo int to str
    nome_arquivo = str(nome_arquivo)

    # resetar index 
    df['n'] = df.reset_index(drop=True).index + 1
    df[var_nome] = df[var_nome].round(2)
    df['Data'] = pd.to_datetime(df['Data'])
    df = df[df[var_nome].notna()]
    
    
    # Encontrar o cutoff em proporção de linhas
    cutoff_idx = int(len(df) * proporcao_cal)
    cutoff_data = df.iloc[cutoff_idx]['Data']
    cutoff_year = cutoff_data.year
    
    if condicao == "cal":
        # Calibração: até o último dia do ano do cutoff
        fim_cal = pd.Timestamp(year=cutoff_year, month=12, day=31)
        df_sel = df[df['Data'] <= fim_cal]
        print("Calibração:", df_sel["Data"].min(), "→", df_sel["Data"].max())
    elif condicao == "val":
        # Validação: a partir do primeiro dia do ano seguinte ao cutoff
        ini_val = pd.Timestamp(year=cutoff_year + 1, month=1, day=1)
        df_sel = df[df['Data'] >= ini_val]
        print("Validação:", df_sel["Data"].min(), "→", df_sel["Data"].max())
    else:
        raise ValueError("condicao deve ser 'cal' ou 'val'")

    with open(f"{nome_arquivo}_{condicao}_{proporcao_cal}_dia.txt", 'w') as f:

        for index, row in df_sel.iterrows():
            data = row['Data']
            
            data = data.strftime("%d_%m_%Y")
            f.write(f"{row['n']}\t{texto}_{data}\t{row[var_nome]}\n")
        print(f"Arquivo '{nome_arquivo} {condicao} {proporcao_cal} dia' criado com sucesso.")

def criar_arquivo_dados_vazao_SWATCUP_condicionamento_mes(
    df, var_nome: str, nome_arquivo: int, condicao: str, texto: str = "FLOW_OUT", proporcao_cal: float = 0.7, ano_modelo=None
):
    """
    Cria um arquivo de dados de vazão formatado e faz o split em anos completos.
    'condicao' pode ser 'cal' (calibração) ou 'val' (validação).
    'proporcao_cal' permite inverter: 0.3 para calibrar com 30% inicial, 0.7 padrão para 70% inicial.
    """

    # Nome do arquivo int to str
    nome_arquivo = str(nome_arquivo)

    df['Data'] = pd.to_datetime(df['Data'])
    monthly = df.groupby(df['Data'].dt.to_period("M"))[[var_nome]].mean().reset_index()
    monthly['Data'] = monthly['Data'].dt.to_timestamp()  # Converte Period para Timestamp (primeiro dia do mês)
    monthly[var_nome] = monthly[var_nome].round(2)
    monthly['n'] = monthly.reset_index(drop=True).index + 1
    monthly = monthly[monthly[var_nome].notna()]

    # Encontrar o cutoff em proporção de linhas
    cutoff_idx = int(len(monthly) * proporcao_cal)
    cutoff_data = monthly.iloc[cutoff_idx]['Data']
    cutoff_year = cutoff_data.year
    
    if condicao == "cal":
        # Calibração: até o último dia do ano do cutoff
        fim_cal = pd.Timestamp(year=cutoff_year, month=12, day=31)
        df_sel = monthly[monthly['Data'] <= fim_cal]
        print("Calibração:", df_sel["Data"].min(), "→", df_sel["Data"].max())
    elif condicao == "val":
        # Validação: a partir do primeiro dia do ano seguinte ao cutoff
        ini_val = pd.Timestamp(year=cutoff_year + 1, month=1, day=1)
        df_sel = monthly[monthly['Data'] >= ini_val]
        print("Validação:", df_sel["Data"].min(), "→", df_sel["Data"].max())
    else:
        raise ValueError("condicao deve ser 'cal' ou 'val'")

    # return df_sel
    
    with open(f"{nome_arquivo}_{condicao}_{proporcao_cal}_mes.txt", 'w') as f:

        for index, row in df_sel.iterrows():
            data = row['Data']
            
            data = data.strftime("%m_%Y")
            # print(data)
            f.write(f"{row['n']}\t{texto}_{data}\t{row[var_nome]}\n")
        print(f"Arquivo '{nome_arquivo} {condicao} {proporcao_cal} meses' criado com sucesso.")

def criar_arquivo_dados_vazao_SWATCUP_validacao_txt(df, var_nome, nome_arquivo ):
    """
    Cria um arquivo de dados de vazão formatado.
    """

    with open(f"{nome_arquivo}.txt", 'w') as f:

        for index, row in df.iterrows():
            f.write(f"{row[var_nome]}\n")
        print(f"Arquivo '{nome_arquivo}' criado com sucesso.")


if __name__ == "__main__":
    estacoes = [60471200, 60474100, 60476100]  # Lista de estações para processamento
    datas_inicio = ["1990-01-01", "1995-01-01", "1978-01-01"]
    datas_fim = ["2023-12-31", "2023-12-31", "2014-12-31"]
    for estacao, data_inicio, data_fim in zip(estacoes, datas_inicio, datas_fim):
        df = ler_csv("FLU_Series_ANA.txt", estacao, data_inicio, data_fim)

        # Checar se há nan ou null na coluna 'Vazao'
        if df['Vazao'].isnull().values.any():
            print("Existem valores nulos na coluna 'Vazao'")

        # Mostrar que linhas são
            df_nan = df[df['Vazao'].isnull()]
        
        criar_arquivo_dados_vazao_SWATCUP_condicionamento_dia(df, "Vazao", estacao, condicao="cal", texto="FLOW_OUT", proporcao_cal=0.7)
        criar_arquivo_dados_vazao_SWATCUP_condicionamento_dia(df, "Vazao", estacao, condicao="val", texto="FLOW_OUT", proporcao_cal=0.7)

        print("------------------------------------------------------------------------------")

        criar_arquivo_dados_vazao_SWATCUP_condicionamento_dia(df, "Vazao", estacao, condicao="cal", texto="FLOW_OUT", proporcao_cal=0.3)
        criar_arquivo_dados_vazao_SWATCUP_condicionamento_dia(df, "Vazao", estacao, condicao="val", texto="FLOW_OUT", proporcao_cal=0.3)

        print("------------------------------------------------------------------------------")

        criar_arquivo_dados_vazao_SWATCUP_condicionamento_mes(df, "Vazao", estacao, condicao="cal", texto="FLOW_OUT", proporcao_cal=0.7)
        criar_arquivo_dados_vazao_SWATCUP_condicionamento_mes(df, "Vazao", estacao, condicao="val", texto="FLOW_OUT", proporcao_cal=0.7)

        print("------------------------------------------------------------------------------")

        criar_arquivo_dados_vazao_SWATCUP_condicionamento_mes(df, "Vazao", estacao, condicao="cal", texto="FLOW_OUT", proporcao_cal=0.3)
        criar_arquivo_dados_vazao_SWATCUP_condicionamento_mes(df, "Vazao", estacao, condicao="val", texto="FLOW_OUT", proporcao_cal=0.3)