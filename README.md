# hydroprep 🚀

Scripts práticos para preparar e analisar dados hidrológicos para QSWAT/SWATCUP

---

## ✨ Visão Geral

O **hydroprep** é uma coleção de scripts Python criados para facilitar tarefas comuns no processamento de séries temporais de **precipitação** e **vazão**, além de gerar arquivos de entrada prontos para uso no **QSWAT** e **SWATCUP**.

Cada script tem um objetivo específico, com uso simples e direto.

---

## 🛠️ Scripts Disponíveis

- 📅 **detecta_periodo.py** *Em elaboração*
  Informa o início e o fim dos dados de precipitação ou vazão. 

- 📈 **correlacao_chuva_vazao.py** *Em elaboração*
  Calcula e plota a correlação entre precipitação e vazão. 

- ☔ **gera_entrada_precipitacao_qswat.py**  
  Prepara a entrada de precipitação no formato aceito pelo QSWAT.

- 💧 **gera_sources_qswat.py**  
  Gera os arquivos de pontos de monitoramento de vazão para o QSWAT.

- 🔄 **gera_entrada_vazao_swatcup.py**  *Em elaboracao*
  Prepara os dados de vazão para o SWATCUP.

---

## ▶️ Como Usar

> **Pré-requisitos:**  
> - 🐍 Python 3.8+  
> - 📦 Instale as bibliotecas do `requirements.txt`

### ⚡ Instalação

```bash
git clone https://github.com/rvidals/hydroprep.git
cd hydroprep
pip install -r requirements.txt
```

### 💡 Exemplos de Uso

1. 📅 **Detectar período:**
    ```bash
    python detecta_periodo.py --input dados/chuva.csv
    ```

2. 📈 **Correlação precipitação x vazão:**
    ```bash
    python correlacao_chuva_vazao.py --chuva dados/chuva.csv --vazao dados/vazao.csv
    ```

3. ☔ **Entrada QSWAT:**
    ```bash
    python gera_entrada_qswat.py --chuva dados/chuva.csv
    ```

4. 💧 **Pontos source QSWAT:**
    ```bash
    python gera_sources_qswat.py --vazao dados/vazao.csv
    ```

5. 🔄 **Entrada SWATCUP:**
    ```bash
    python gera_entrada_swatcup.py --vazao dados/vazao.csv
    ```

Veja exemplos na pasta [`examples/`](examples/).

---

## 🤝 Contribuindo

Sugestões, melhorias e correções são bem-vindas!  
Abra uma *issue* ou envie um *pull request*.

---

## 📜 Licença

[MIT](LICENSE)

---

**Contato:** Rafael Vidals (`@rvidals`)

---

## 🔭 Futuro

- [ ] 🗃️ Novos scripts para análise hidrológica
- [ ] 📊 Mais exemplos de uso

      ## 🤝 Contribuições

Sinta-se à vontade para abrir issues, sugerir melhorias ou compartilhar dashboards inspiradores! 🚀

---

## 📩 Contato

👤 **Rogerio Vidal de Siqueira**  
📧 rogeriovidalsiqueira@gmail.com  
🔗 [LinkedIn](https://www.linkedin.com/in/rogerio-vidal-de-siqueira-9478aa136/) | [GitHub](https://github.com/rvidals)

---

> “Com ciência, dados e colaboração, construímos cidades mais resilientes!” 🌱🌏
