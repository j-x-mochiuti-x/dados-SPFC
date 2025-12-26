import pandas as pd
import statsmodels.api as sm
import numpy as np

# 1. Carregar os dados
# Certifique-se que o separador é ; mesmo. Se der erro de colunas, tente sep=','
df = pd.read_csv("SPFC_JOGOS_COMPLETOS_CONSOLIDADO.csv", sep=';', encoding='utf-8-sig')

# 2. Criar a variável alvo (Target): 1 se ganhou, 0 se não
# Garantimos que seja inteiro (.astype(int))
df['Vitoria_Binaria'] = df['Status_Jogo'].apply(lambda x: 1 if x == 'Vitória' else 0).astype(int)

# 3. Preparar as Dummies (Gestão)
# CORREÇÃO AQUI: Adicionamos dtype=int para garantir que venha 0 e 1, não True/False
X = pd.get_dummies(df['Gestao'], prefix='Pres', dtype=int)

# Definindo Juvenal como Baseline (removendo a coluna dele manualmente)
# Se não encontrar 'Juvenal' exatamente, ele tenta achar algo parecido
cols_juvenal = [c for c in X.columns if 'Juvenal' in c]

if len(cols_juvenal) > 0:
    coluna_baseline = cols_juvenal[0]
    print(f"--- Removendo Baseline: {coluna_baseline} ---")
    X = X.drop(columns=[coluna_baseline])
else:
    print("AVISO: Coluna Juvenal não encontrada. O modelo usará outra base ou falhará na interpretação.")

# GARANTIA FINAL: Converter tudo para float (número decimal) para o statsmodels não reclamar
X = X.astype(float)

# Adicionando a constante (intercepto) - Obrigatório para Statsmodels
X = sm.add_constant(X)
y = df['Vitoria_Binaria']

# 4. Rodar a Regressão Logística
try:
    modelo = sm.Logit(y, X).fit()

    # 5. Calcular Odds Ratio (Razão de Chances) e Intervalos de Confiança
    params = modelo.params
    conf = modelo.conf_int()
    conf['Odds Ratio'] = params
    conf.columns = ['2.5%', '97.5%', 'Odds Ratio']

    # Transformar de Log-Odds para Odds (exponencial)
    odds_ratios = np.exp(conf)

    print("\n" + "="*40)
    print("   ANÁLISE FOCADA: GESTÃO CASARES")
    print("="*40)
    
    # Tenta encontrar a linha do Casares
    linhas_casares = [idx for idx in odds_ratios.index if 'Casares' in idx]
    
    if linhas_casares:
        print(odds_ratios.loc[linhas_casares])
        valor_odds = odds_ratios.loc[linhas_casares[0], 'Odds Ratio']
        print(f"\n---> O número mágico para seu texto é: {valor_odds:.4f}")
    else:
        print("Não encontrei a coluna 'Casares'. Verifique os nomes abaixo:")
        print(odds_ratios.index)


except Exception as e:
    print(f"\nERRO AO RODAR O MODELO: {e}")
    print("Verifique se os dados contêm valores nulos (NaN) ou infinitos.")

print("\n" + "="*40)
print("   PROVA REAL: P-VALORES (P-values)")
print("="*40)
print("Hipótese Nula (H0): Odds Ratio = 1 (Não há diferença para o Baseline)")
print("Regra: Se P-valor < 0.05, rejeitamos H0 (A diferença é real).\n")

# Pegando os p-valores do modelo
p_values = modelo.pvalues

# Juntando Odds Ratio com P-valor num quadro só para ficar bonito
resumo_final = pd.DataFrame({
    'Odds Ratio': params,
    'P-valor': p_values,
    'Significante (5%)?': p_values.apply(lambda x: 'SIM' if x < 0.05 else 'NÃO')
})

# Transformando log-odds em odds (apenas na coluna Odds Ratio)
resumo_final['Odds Ratio'] = np.exp(resumo_final['Odds Ratio'])

# Filtrando apenas Casares
if 'Pres_Julio Casares (2021-Presente)' in resumo_final.index:
    print(resumo_final.loc[['Pres_Julio Casares (2021-Presente)']])
else:
    print(resumo_final)