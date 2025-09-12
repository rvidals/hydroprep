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
    df, var_nome: str, nome_arquivo: int, condicao: str, texto: str = "FLOW_OUT", proporcao_cal: float = 0.7, dt_modelo=None
):
    """
    Cria um arquivo de dados de vazão diário formatado e faz o split em anos completos.
    'condicao' pode ser 'cal' (calibração) ou 'val' (validação).
    'proporcao_cal' permite inverter: 0.3 para calibrar com 30% inicial, 0.7 padrão para 70% inicial.
    'dt_modelo' define o ANO, MÊS e DIA onde a contagem de dias começa.
      - None (default): usa ano, mês e dia do primeiro dado disponível
      - int: assume como ano, mês=1, dia=1
      - (ano, mes, dia): define ano, mês e dia de início da contagem de n
    """

    # Nome do arquivo int to str
    nome_arquivo = str(nome_arquivo)

    df['Data'] = pd.to_datetime(df['Data'])
    df[var_nome] = df[var_nome].round(2)
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

    # --- Lógica para dt_modelo
    if dt_modelo is None:
        ano_inicio = df_sel['Data'].iloc[0].year
        mes_inicio = df_sel['Data'].iloc[0].month
        dia_inicio = df_sel['Data'].iloc[0].day
    elif isinstance(dt_modelo, int):
        ano_inicio = dt_modelo
        mes_inicio = 1
        dia_inicio = 1
    elif isinstance(dt_modelo, (tuple, list)) and len(dt_modelo) == 3:
        ano_inicio, mes_inicio, dia_inicio = dt_modelo
    else:
        raise ValueError("dt_modelo deve ser None, int ou (ano, mes, dia)")

    dt_inicio = pd.Timestamp(year=ano_inicio, month=mes_inicio, day=dia_inicio)

    # Calcular n para cada linha baseada em dt_modelo
    df_sel = df_sel.copy()
    df_sel['n'] = (df_sel['Data'] - dt_inicio).dt.days + 1

    # --- Gera o arquivo de saída
    with open(f"{nome_arquivo}_{condicao}_{proporcao_cal}_dia.txt", 'w') as f:
        for index, row in df_sel.iterrows():
            data = row['Data'].strftime("%d_%m_%Y")
            f.write(f"{row['n']}\t{texto}_{data}\t{row[var_nome]}\n")
        print(f"Arquivo '{nome_arquivo}_{condicao}_{proporcao_cal}_dia.txt' criado com sucesso.")

def criar_arquivo_dados_vazao_SWATCUP_condicionamento_mes(
    df, var_nome: str, nome_arquivo: int, condicao: str, texto: str = "FLOW_OUT", proporcao_cal: float = 0.7, dt_modelo=None
):
    """
    Cria um arquivo de dados de vazão formatado e faz o split em anos completos.
    'condicao' pode ser 'cal' (calibração) ou 'val' (validação).
    'proporcao_cal' permite inverter: 0.3 para calibrar com 30% inicial, 0.7 padrão para 70% inicial.
    'dt_modelo' define o ANO e MÊS onde a contagem de meses começa. Pode ser:
      - None (default): usa o ano e mês do primeiro dado disponível
      - int: assume como ano e mês=1
      - (ano, mes): define ano e mês de início da contagem de n
    """

    # Nome do arquivo int to str
    nome_arquivo = str(nome_arquivo)

    df['Data'] = pd.to_datetime(df['Data'])
    monthly = df.groupby(df['Data'].dt.to_period("M"))[[var_nome]].mean().reset_index()
    monthly['Data'] = monthly['Data'].dt.to_timestamp()  # Converte Period para Timestamp (primeiro dia do mês)
    monthly[var_nome] = monthly[var_nome].round(2)
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

    # --- Lógica para dt_modelo
    if dt_modelo is None:
        ano_inicio = df_sel['Data'].iloc[0].year
        mes_inicio = df_sel['Data'].iloc[0].month
    elif isinstance(dt_modelo, int):
        ano_inicio = dt_modelo
        mes_inicio = 1
    elif isinstance(dt_modelo, (tuple, list)) and len(dt_modelo) == 2:
        ano_inicio, mes_inicio = dt_modelo
    else:
        raise ValueError("dt_modelo deve ser None, int ou (ano, mes)")

    # Calcular n para cada linha baseada em dt_modelo
    def calcula_n(row):
        return (row['Data'].year - ano_inicio) * 12 + (row['Data'].month - mes_inicio) + 1

    df_sel = df_sel.copy()
    df_sel['n'] = df_sel.apply(calcula_n, axis=1)

    # --- Gera o arquivo de saída
    with open(f"{nome_arquivo}_{condicao}_{proporcao_cal}_mes.txt", 'w') as f:
        for index, row in df_sel.iterrows():
            data = row['Data']
            data_str = data.strftime("%m_%Y")
            f.write(f"{row['n']}\t{texto}_{data_str}\t{row[var_nome]}\n")
        print(f"Arquivo '{nome_arquivo}_{condicao}_{proporcao_cal}_mes.txt' criado com sucesso.")

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
        
        criar_arquivo_dados_vazao_SWATCUP_condicionamento_dia(df, "Vazao", estacao, condicao="cal", texto="FLOW_OUT", proporcao_cal=0.7, dt_modelo=(1978,1,1))
        criar_arquivo_dados_vazao_SWATCUP_condicionamento_dia(df, "Vazao", estacao, condicao="val", texto="FLOW_OUT", proporcao_cal=0.7, dt_modelo=(1978,1,1))

        print("------------------------------------------------------------------------------")

        criar_arquivo_dados_vazao_SWATCUP_condicionamento_dia(df, "Vazao", estacao, condicao="cal", texto="FLOW_OUT", proporcao_cal=0.3, dt_modelo=(1978,1,1))
        criar_arquivo_dados_vazao_SWATCUP_condicionamento_dia(df, "Vazao", estacao, condicao="val", texto="FLOW_OUT", proporcao_cal=0.3, dt_modelo=(1978,1,1))

        print("------------------------------------------------------------------------------")

        criar_arquivo_dados_vazao_SWATCUP_condicionamento_mes(df, "Vazao", estacao, condicao="cal", texto="FLOW_OUT", proporcao_cal=0.7, dt_modelo=(1978,1))
        criar_arquivo_dados_vazao_SWATCUP_condicionamento_mes(df, "Vazao", estacao, condicao="val", texto="FLOW_OUT", proporcao_cal=0.7, dt_modelo=(1978,1))

        print("------------------------------------------------------------------------------")

        criar_arquivo_dados_vazao_SWATCUP_condicionamento_mes(df, "Vazao", estacao, condicao="cal", texto="FLOW_OUT", proporcao_cal=0.3, dt_modelo=(1978,1))
        criar_arquivo_dados_vazao_SWATCUP_condicionamento_mes(df, "Vazao", estacao, condicao="val", texto="FLOW_OUT", proporcao_cal=0.3, dt_modelo=(1978,1))