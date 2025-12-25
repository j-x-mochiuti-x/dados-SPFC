import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Carrega o arquivo final que acabamos de gerar
df = pd.read_csv("SPFC_DATASET_MESTRE_AJUSTADO.csv", sep=';')

# Configuração de Estilo
sns.set_theme(style="whitegrid")
plt.figure(figsize=(12, 8))

# --- GRÁFICO DE DISPERSÃO ---
scatter = sns.scatterplot(
    data=df,
    x="Despesa_Real_Mi",
    y="Aproveitamento_Pct",
    size="Receita_Real_Mi",  # O tamanho da bola é a Receita
    sizes=(200, 2000),       # Tamanho mínimo e máximo das bolas
    hue="Gestao",            # Cores diferentes por presidente
    palette="viridis",
    alpha=0.7,
    edgecolor="black",
    linewidth=2
)

# --- ADICIONANDO OS QUADRANTES (MÉDIAS) ---
media_aproveitamento = df['Aproveitamento_Pct'].mean()
media_gasto = df['Despesa_Real_Mi'].mean()

plt.axhline(y=media_aproveitamento, color='gray', linestyle='--', alpha=0.5)
plt.axvline(x=media_gasto, color='gray', linestyle='--', alpha=0.5)

# Textos dos Quadrantes (Para explicar a lógica)
plt.text(df['Despesa_Real_Mi'].max()*0.9, df['Aproveitamento_Pct'].max()*1.01, 
         "CARO E EFICIENTE", color='green', fontsize=9, ha='center')
plt.text(df['Despesa_Real_Mi'].min()*1.1, df['Aproveitamento_Pct'].max()*1.01, 
         "BARATO E EFICIENTE\n(Sonho)", color='blue', fontsize=9, ha='center')
plt.text(df['Despesa_Real_Mi'].max()*0.9, df['Aproveitamento_Pct'].min()*0.98, 
         "CARO E INEFICIENTE\n(Pesadelo)", color='red', fontsize=9, ha='center')

# --- RÓTULOS NOS PONTOS ---
# Adiciona o nome do presidente e o Custo por Ponto ao lado da bolha
for i in range(df.shape[0]):
    plt.text(
        df.Despesa_Real_Mi[i]+1, 
        df.Aproveitamento_Pct[i]+0.2, 
        f"{df.Gestao[i]}\n(Custo/Pto: €{df.Custo_Ponto_Real_Euro[i]}M)", 
        fontsize=10, 
        fontweight='bold',
        color='black'
    )

# Títulos e Ajustes
plt.title('Matriz de Eficiência Financeira vs. Esportiva (2006-Presente)\nValores Ajustados pela Inflação (IPCA Euro)', fontsize=14, fontweight='bold')
plt.xlabel('Investimento Total Real (Milhões de Euros)', fontsize=12)
plt.ylabel('Aproveitamento de Pontos (%)', fontsize=12)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Gestão (Tamanho = Receita)")

plt.tight_layout()
plt.show()