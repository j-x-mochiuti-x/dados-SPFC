import pandas as pd

# Carrega o arquivo (Lembre-se do sep=';' pois salvamos assim)
df = pd.read_csv("spfc_financeiro_FINAL_MILHOES.csv", sep=';')

print("=== 1. ESTRUTURA DOS DADOS (INFO) ===")
df.info()

print("\n=== 2. RESUMO ESTATÍSTICO (DESCRIBE) ===")
# O describe só calcula estatísticas de colunas numéricas.
# Se a coluna 'Valor_Milhoes' não aparecer aqui, é porque ela ainda é texto (erro).
print(df.describe())