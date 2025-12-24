import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
from io import StringIO

# --- CONFIGURAÇÃO ---
# URL base sem o número da página
BASE_URL = "https://www.transfermarkt.com.br/fc-sao-paulo/alletransfers/verein/585/ajax/yw1/page/{}"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

lista_final_dfs = []

print("--- INICIANDO COLETA DE TRANSFERÊNCIAS (HISTÓRICO COMPLETO) ---\n")

# Vamos percorrer 10 páginas (geralmente suficiente para ir até 1929)
# Se o script parar antes de 1929, aumente esse número no range(1, 11)
for pagina in range(1, 11):
    url = BASE_URL.format(pagina)
    print(f"Processando Página {pagina}...")
    
    try:
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # O Transfermarkt organiza assim: Um Cabeçalho (H2) seguido de uma Tabela (div responsive-table)
            # Vamos encontrar todos os boxes de tabelas
            tabelas_html = soup.find_all("div", class_="responsive-table")
            
            if not tabelas_html:
                print(" -> Nenhuma tabela encontrada nesta página. Fim da paginação.")
                break
                
            for tabela_div in tabelas_html:
                # Tenta encontrar o título logo acima da tabela (Ex: "Entradas 20/21" ou "Saídas 20/21")
                # As vezes o título está num 'div' anterior ou num 'h2' dentro de um box anterior
                # O método mais seguro no Transfermarkt é pegar o 'table-header' anterior
                
                # Procura o box pai para achar o cabeçalho correspondente
                box_pai = tabela_div.find_previous("div", class_="box")
                header_text = "Desconhecido"
                
                if box_pai:
                    header_element = box_pai.find("h2")
                    if header_element:
                        header_text = header_element.get_text(strip=True)
                
                # Converte o HTML da tabela para DataFrame
                html_io = StringIO(str(tabela_div))
                dfs = pd.read_html(html_io)
                
                if dfs:
                    df_temp = dfs[0]
                    
                    # Adiciona a coluna vital: CONTEXTO (Ex: "Entradas 23/24")
                    # Sem isso não saberíamos o ano nem se foi compra ou venda
                    df_temp['CONTEXTO_TEMPORADA'] = header_text
                    
                    lista_final_dfs.append(df_temp)
            
            print(f" -> {len(tabelas_html)} tabelas coletadas nesta página.")
            
        else:
            print(f" -> Erro na página {pagina}: Status {response.status_code}")
            
    except Exception as e:
        print(f" -> Erro técnico na página {pagina}: {e}")
    
    # Pausa para não ser bloqueado
    time.sleep(3)

# --- CONSOLIDAÇÃO ---
if lista_final_dfs:
    print("\nConsolidando histórico...")
    df_bruto = pd.concat(lista_final_dfs, ignore_index=True)
    
    nome_arquivo = "sao_paulo_transferencias_bruto.csv"
    df_bruto.to_csv(nome_arquivo, sep=';', index=False, encoding='utf-8-sig')
    
    print(f"\nSUCESSO! Arquivo salvo: {nome_arquivo}")
    print(f"Total de registros de transferências: {len(df_bruto)}")
    print("Dica: A coluna 'CONTEXTO_TEMPORADA' conterá algo como 'Entradas 14/15'. Usaremos isso para filtrar.")
else:
    print("\nFalha: Nada foi coletado.")