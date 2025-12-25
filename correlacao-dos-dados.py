import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- CONFIGURAÇÃO ---
ARQUIVO_JOGOS = "SPFC_JOGOS_COMPLETOS_CONSOLIDADO.csv"
ARQUIVO_FINANCEIRO = "spfc_financeiro_FINAL_MILHOES.csv"

print("--- GERANDO MATRIZ DE CORRELAÇÃO POR GESTÃO (HEATMAP) ---\n")

try:
    # 1. CARREGAR DADOS
    df_jogos = pd.read_csv(ARQUIVO_JOGOS, sep=';', encoding='utf-8-sig')
    df_fin = pd.read_csv(ARQUIVO_FINANCEIRO, sep=';', encoding='utf-8-sig')

    # 2. PADRONIZAÇÃO DOS NOMES DAS GESTÕES (Obrigatório para o cruzamento)
    mapa_nomes = {
        "Julio Casares (2021-Presente)": "Julio Casares",
        "Leco (2015-2020)": "Leco",
        "Juvenal Juvêncio (2006-2014)": "Juvenal Juvêncio",
        "Carlos Miguel Aidar (2014-2015)": "Carlos Miguel Aidar" 
    }
    df_jogos['Gestao'] = df_jogos['Gestao'].replace(mapa_nomes)
    
    df_fin['Gestao'] = df_fin['Gestao'].replace({
        "Carlos Miguel Aidar (Transição JJ)": "Carlos Miguel Aidar",
        "Carlos Miguel Aidar (Transição Leco)": "Carlos Miguel Aidar"
    })

    # 3. PREPARAR DADOS ESPORTIVOS (Agrupar por Gestão)
    df_jogos['Vitoria'] = df_jogos['Status_Jogo'].apply(lambda x: 1 if x == 'Vitória' else 0)
    
    # Criamos as médias/totais por presidente
    esportivo = df_jogos.groupby('Gestao').agg({
        'Status_Jogo': 'count', # Total Jogos
        'Vitoria': 'sum',       # Total Vitórias
        'Gols_Pro': 'mean'      # Média de Gols por Jogo
    }).reset_index()

    esportivo.rename(columns={'Status_Jogo': 'Total_Jogos', 'Gols_Pro': 'Media_Gols_Jogo'}, inplace=True)
    
    # Calcula % de Vitória
    esportivo['Pct_Vitoria'] = esportivo['Vitoria'] / esportivo['Total_Jogos']

    # 4. PREPARAR DADOS FINANCEIROS (Com Inflação)
    # A inflação é aplicada no financeiro ANTES de agrupar, pois lá temos a coluna Ano!
    fator_inflacao_euro = {
        2006: 1.42, 2007: 1.39, 2008: 1.35, 2009: 1.34, 2010: 1.32,
        2011: 1.28, 2012: 1.25, 2013: 1.23, 2014: 1.22, 2015: 1.20,
        2016: 1.19, 2017: 1.17, 2018: 1.15, 2019: 1.14, 2020: 1.14,
        2021: 1.11, 2022: 1.05, 2023: 1.02, 2024: 1.00, 2025: 1.00
    }
    df_fin['Fator_Ajuste'] = df_fin['Ano'].map(fator_inflacao_euro).fillna(1.0)
    df_fin['Valor_Real'] = df_fin['Valor_Milhoes'] * df_fin['Fator_Ajuste']

    # Agrupa por gestão somando tudo
    financeiro = df_fin[df_fin['Tipo'].str.contains('Despesa', case=False)].groupby('Gestao')['Valor_Real'].sum().reset_index(name='Total_Despesa_Real')
    receita = df_fin[df_fin['Tipo'].str.contains('Receita', case=False)].groupby('Gestao')['Valor_Real'].sum().reset_index(name='Total_Receita_Real')
    
    # Junta Receita e Despesa num dataframe só
    financeiro = pd.merge(financeiro, receita, on='Gestao')

    # 5. CRUZAMENTO FINAL (Esportivo + Financeiro)
    df_final = pd.merge(esportivo, financeiro, on='Gestao', how='inner')

    # Como os totais de despesa são absolutos e os jogos variam (Juvenal ficou 8 anos, Aidar 1),
    # Precisamos criar a "Despesa Média por Jogo" para a correlação ser justa.
    df_final['Gasto_Por_Jogo'] = df_final['Total_Despesa_Real'] / df_final['Total_Jogos']

    # 6. HEATMAP DE CORRELAÇÃO
    # Vamos ver a relação entre: Gastar por Jogo vs % de Vitória vs Média de Gols
    cols_corr = ['Gasto_Por_Jogo', 'Total_Receita_Real', 'Pct_Vitoria', 'Media_Gols_Jogo']
    
    matriz_corr = df_final[cols_corr].corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        matriz_corr, 
        annot=True, 
        cmap='RdYlGn', # Vermelho (Ruim) a Verde (Bom)
        fmt=".2f",
        vmin=-1, vmax=1,
        linewidths=1
    )
    plt.title('Correlação: Investimento vs. Resultado (Por Gestão)\n(Existe relação entre gastar mais por jogo e vencer mais?)', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.show()

    print("--- DADOS UTILIZADOS NA CORRELAÇÃO ---")
    print(df_final[['Gestao', 'Gasto_Por_Jogo', 'Pct_Vitoria']])

except Exception as e:
    print(f"Erro: {e}")