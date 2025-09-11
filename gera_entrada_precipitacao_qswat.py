import os
import pandas as pd
from datetime import datetime
from tqdm import tqdm   # Acrescentado tqdm para barra de progresso

def ler_csv_ou_txt(arquivo_csv_ou_txt, cod_estacao):
    """Lê o csv."""
    if arquivo_csv_ou_txt.endswith('.csv'):
        df = pd.read_csv(arquivo_csv_ou_txt, engine='python')
    elif arquivo_csv_ou_txt.endswith('.txt'):
        df = pd.read_csv(arquivo_csv_ou_txt, sep='\\t', engine='python')
    else:
        raise ValueError("Arquivo deve ser .csv ou .txt")
    
    # Corrigir nomes das colunas para remover aspas e facilitar o acesso
    df.columns = [col.strip().replace('"', '') for col in df.columns]
        
    if "Cod.estacao" not in df.columns:
        df.rename(columns={"Cod.estacao": "cod_estacao"}, inplace=True)
        
    if "cod_estacao" not in df.columns:
        raise ValueError("A coluna 'cod_estacao' não foi encontrada no arquivo.")
    
    df = df[df["cod_estacao"] == cod_estacao]
    return df

def criar_arquivo_estacao_virtual_txt(id, nome, lat, long, elevation, nome_arquivo, write_header=False):
       
    df = pd.DataFrame({
            'ID': [id],
            'NAME': [nome],
            'LAT': [lat],
            'LONG': [long],
            'ELEVATION': [elevation]
        })

        # Criar o arquivo de saída
            # Caminho do arquivo
    caminho_arquivo = os.path.join(os.getcwd(), "00_DADOS", "05_outros_dados", "TABELAS", f"{nome_arquivo}.txt")
# Modo de abertura: 'w' (escrever) se write_header, senão 'a' (acrescentar)
    mode = 'w' if write_header else 'a'
    with open(caminho_arquivo, mode) as f:
        if write_header:
            f.write("ID,NAME,LAT,LONG,ELEVATION\n")
        f.write(f"{df['ID'][0]},{df['NAME'][0]},{df['LAT'][0]},{df['LONG'][0]},{df['ELEVATION'][0]}\n")
    print(f"Linha adicionada ao arquivo '{nome_arquivo}.txt'.")

def criar_arquivo_dados_estacao_virtual_txt(df, var_nome, nome_arquivo, aquecimento=True, df_aquecimento=None):
    """Cria um arquivo de dados climáticos formatado."""

    caminho_arquivo = os.path.join(os.getcwd(), "00_DADOS", "05_outros_dados", "TABELAS", f"{nome_arquivo}.txt")
    with open(caminho_arquivo, 'w') as f:
        if aquecimento:
            if df_aquecimento is None:
                raise ValueError("df_aquecimento deve ser fornecido quando aquecimento é True.")
            
            # Quando tiver aquecimento, escrevo a data inicial do aquecimento
            df_aquecimento['Data'] = pd.to_datetime(df_aquecimento['Data'])
            primeira_data_aquecimento = df_aquecimento['Data'].min().strftime('%Y%m%d')
            f.write(f"{primeira_data_aquecimento}\n")
            
            for _, row in df_aquecimento.iterrows():
                if row[var_nome] is pd.NA or pd.isna(row[var_nome]):
                    f.write("-99\n")
                else:
                    f.write(f"{row[var_nome]}\n")
            for _, row in df.iterrows():
                if row[var_nome] is pd.NA or pd.isna(row[var_nome]):
                    f.write("-99\n")
                else:
                    f.write(f"{row[var_nome]}\n")
            
        else:
            # Não tem aquecimento, só escreve o bloco normal
            df['Data'] = pd.to_datetime(df['Data'])
            primeira_data = df['Data'].min().strftime('%Y%m%d')
            f.write(f"{primeira_data}\n")
            for _, row in df.iterrows():
                if row[var_nome] is pd.NA or pd.isna(row[var_nome]):
                    f.write("-99\n")
                else:
                    f.write(f"{row[var_nome]}\n")
    print(f"Arquivo '{nome_arquivo}' criado com sucesso.")

def filtrar_datas(df, dt_inicial, dt_final):
    """Filtra o DataFrame com base nas datas.
    df: DataFrame a ser filtrado
    dt_inicial: Data inicial - Ano, Mês, Dia
    dt_final: Data final - Ano, Mês, Dia
    """
    df['Data'] = pd.to_datetime(df['Data'], format='%Y-%m-%d')
    if dt_inicial is None:
        return df[df['Data'] <= dt_final]
    elif dt_final is None:
        return df[df['Data'] >= dt_inicial]
    else:
        return df[(df['Data'] >= dt_inicial) & (df['Data'] <= dt_final)]

def pipeline_precipitacao():
    print("Iniciando pipeline de precipitação...")
    arquivo_csv = os.path.join(os.getcwd(), "00_DADOS", "05_outros_dados", "TABELAS", "PLU_Series_ANA.txt")
    cod_estacoes = [1547002, 1547011, 1547071, 1547072, 1547073, 1547078]
    lat = [-15.6431, -15.6572, -15.6686, -15.8094, -15.8186, -15.6822]
    long = [-47.6508, -47.6964, -47.6714, -47.7006, -47.7047, -47.6631]
    alt = [991, 956, 922, 883, 874, 932]
    nome_arquivo_est = "precip"


    for i, (cod_estacao, lat, long, alt) in enumerate(zip(cod_estacoes, lat, long, alt)):
        nome_arquivo_dado = "p" + str(cod_estacao)
        criar_arquivo_estacao_virtual_txt(i, nome_arquivo_dado, lat, long, alt, nome_arquivo_est, write_header=(i == 0))

    for cod_estacao in cod_estacoes:
        df = ler_csv_ou_txt(arquivo_csv, cod_estacao)
        nome_arquivo_dado = "p" + str(cod_estacao)
        nome_estacao = cod_estacao
        
        if cod_estacao == 1547002:
            df = filtrar_datas(df=df, dt_inicial='1974-01-01', dt_final='2012-12-31')
            dados_aquecimento = df[(df["Data"] >= '1974-01-01') & (df["Data"] <= '1977-12-31')]
            
        if cod_estacao == 1547011:
            df = filtrar_datas(df=df, dt_inicial=None, dt_final='2009-12-31')
            dados_aquecimento = df[(df["Data"] >= '1971-01-01') & (df["Data"] <= '1974-12-31')]
        
        if cod_estacao == 1547071:
            df = filtrar_datas(df=df, dt_inicial='2009-01-01', dt_final='2021-12-31')
            dados_aquecimento = df[(df["Data"] >= '1971-01-01') & (df["Data"] <= '1974-12-31')]
        
        if cod_estacao == 1547072:
            df = filtrar_datas(df=df, dt_inicial='2009-01-01', dt_final='2021-12-31')
            dados_aquecimento = df[(df["Data"] >= '1971-01-01') & (df["Data"] <= '1974-12-31')]
        
        if cod_estacao == 1547073:
            df = filtrar_datas(df=df, dt_inicial='2010-01-01', dt_final='2016-12-31')
            dados_aquecimento = df[(df["Data"] >= '1971-01-01') & (df["Data"] <= '1974-12-31')]
        
        if cod_estacao == 1547078:
            df = filtrar_datas(df=df, dt_inicial='2008-01-01', dt_final='2021-12-31')
            dados_aquecimento = df[(df["Data"] >= '1971-01-01') & (df["Data"] <= '1974-12-31')]
            


        criar_arquivo_dados_estacao_virtual_txt(df, 
                                                nome_estacao, 
                                                "Chuva", 
                                                nome_arquivo_dado, 
                                                dados_aquecimento,
                                                aquecimento=True)


# def pipeline_vazao():
#     print("Iniciando pipeline de vazão...")
#     arquivo_csv = "FLU_Series_ANA.txt"
#     cod_estacao = 60490000
#     nome_arquivo_est = "p60490000"
#     nome_arquivo_dado = "vazao"
#     nome_estacao = cod_estacao

#     df = ler_csv(arquivo_csv, cod_estacao)
#     criar_arquivo_estacao_virtual_txt(1, str(cod_estacao), 214406, 8235023, 845.08, nome_arquivo_est)
#     df = df[(df["Data"] >= '1971-01-01') & (df["Data"] <= '2009-12-31')]
#     dados_aquecimento = df[(df["Data"] >= '1971-01-01') & (df["Data"] <= '1974-12-31')]
#     criar_arquivo_dados_estacao_virtual_txt(dados_aquecimento, df, nome_estacao, "Vazao", nome_arquivo_dado)

def main():
    pipeline_precipitacao()
    # pipeline_vazao()

if __name__ == "__main__":
    main()

    # # Precipitação

    # # Caminho do arquivo CSV
    # arquivo_csv = "PLU_Series_ANA.txt"

    # # Lê o arquivo CSV
    # df = ler_csv(arquivo_csv, cod_estacao=1547012)

    # # Criar arquivo de estação virtual
    # criar_arquivo_estacao_virtual_txt(1, "1547012", 215139, 8233758, 860, "p1547012")
    
    # # Remover dados de 2010
    # df = df[df["Data"] < '2010-01-01']
    
    # # Dados para aquecimento do modelo
    # dados_aquecimento = df[(df["Data"] >= '1971-01-01') & (df["Data"] <= '1974-12-31')]

    # # Criar arquivo de dados de estação virtual
    # criar_arquivo_dados_estacao_virtual_txt(dados_aquecimento, df, 1547012, "Chuva", "precip" )
    
    # # Vazão
    # arquivo_csv = "FLU_Series_ANA.txt"
    
    # # Lê o arquivo CSV
    # df = ler_csv(arquivo_csv, cod_estacao=60490000)

    # # Criar arquivo de estação virtual
    # criar_arquivo_estacao_virtual_txt(1, "60490000", 	214406, 8235023, 845.08, "p60490000")

    # # Remover dados de 1970 e 2010
    # df = df[(df["Data"] >= '1971-01-01') & (df["Data"] <= '2009-12-31')]

    # # Dados para aquecimento do modelo
    # dados_aquecimento = df[(df["Data"] >= '1971-01-01') & (df["Data"] <= '1974-12-31')]

    # # Criar arquivo de dados de estação virtual
    # criar_arquivo_dados_estacao_virtual_txt(dados_aquecimento, df, 60490000, "Vazao", "vazao" )
