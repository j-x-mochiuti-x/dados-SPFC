import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- CONFIGURAÇÃO ---
ARQUIVO_FINANCEIRO = "spfc_financeiro_FINAL_MILHOES.csv"

# Carrega Dados
df = pd.read_csv(ARQUIVO_FINANCEIRO, sep=';', encoding='utf-8-sig')

# --- 1. REAPLICANDO A CORREÇÃO MONETÁRIA (Para ter precisão anual) ---
fator_inflacao_euro = {
    2006: 1.42, 2007: 1.39, 2008: 1.35, 2009: 1.34, 2010: 1.32,
    2011: 1.28, 2012: 1.25, 2013: 1.23, 2014: 1.22, 2015: 1.20,
    2016: 1.19, 2017: 1.17, 2018: 1.15, 2019: 1.14, 2020: 1.14,
    2021: 1.11, 2022: 1.05, 2023: 1.02, 2024: 1.00, 2025: 1.00
}
df['Fator_Ajuste'] = df['Ano'].map(fator_inflacao_euro).fillna(1.0)
df['Valor_Real'] = df['Valor_Milhoes'] * df['Fator_Ajuste']

# --- 2. AGRUPANDO POR ANO (Receita vs Despesa) ---
receitas = df[df['Tipo'].str.contains('Receita', case=False)].groupby('Ano')['Valor_Real'].sum()
despesas = df[df['Tipo'].str.contains('Despesa', case=False)].groupby('Ano')['Valor_Real'].sum()

# Cria DataFrame Anual
df_anual = pd.DataFrame({'Receita_Real': receitas, 'Despesa_Real': despesas}).fillna(0)
df_anual['Saldo_Real'] = df_anual['Receita_Real'] - df_anual['Despesa_Real']

# --- 3. PLOTAGEM DO GRÁFICO ---
plt.figure(figsize=(14, 7))
sns.set_theme(style="white")

# Linhas Principais
plt.plot(df_anual.index, df_anual['Receita_Real'], marker='o', color='#2ecc71', linewidth=2.5, label='Receita Real (Entradas)')
plt.plot(df_anual.index, df_anual['Despesa_Real'], marker='o', color='#e74c3c', linewidth=2.5, label='Despesa Real (Saídas)')

# Preenchimento (Saldo)
plt.fill_between(df_anual.index, df_anual['Receita_Real'], df_anual['Despesa_Real'], 
                 where=(df_anual['Receita_Real'] >= df_anual['Despesa_Real']),
                 interpolate=True, color='#2ecc71', alpha=0.1)
plt.fill_between(df_anual.index, df_anual['Receita_Real'], df_anual['Despesa_Real'], 
                 where=(df_anual['Receita_Real'] < df_anual['Despesa_Real']),
                 interpolate=True, color='#e74c3c', alpha=0.1)

# --- 4. COLORINDO AS GESTÕES (BACKGROUND) ---
# Definindo os períodos (Ajuste se necessário)
periodos = [
    (2006, 2013, "Juvenal", "#f0f0f0"),
    (2014, 2015, "Aidar", "#e0e0e0"),
    (2015.5, 2020, "Leco", "#d0d0d0"), # 2015 meio a meio
    (2021, 2025, "Casares", "#f0f0f0")
]

for inicio, fim, nome, cor in periodos:
    plt.axvspan(inicio, fim, color=cor, alpha=0.3, zorder=0)
    plt.text(inicio + (fim-inicio)/2, df_anual['Receita_Real'].max()*1.05, nome, 
             ha='center', fontsize=10, fontweight='bold', color='gray')

# Detalhes Finais
plt.title('Evolução Financeira Real do SPFC (2006-2024)\nValores corrigidos pela inflação (IPCA Zona do Euro)', fontsize=14, fontweight='bold')
plt.ylabel('Milhões de Euros (€)', fontsize=12)
plt.xlabel('Temporada', fontsize=12)
plt.legend(loc='upper left')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.xticks(df_anual.index, rotation=45)

plt.tight_layout()
plt.show()