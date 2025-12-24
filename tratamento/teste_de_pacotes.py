import sys
import os

print("--- DIAGNÓSTICO DE AMBIENTE ---")
print(f"1. O Python que está rodando este script é:\n   {sys.executable}")

try:
    import html5lib
    print(f"\n2. Sucesso! O pacote 'html5lib' foi encontrado.")
    print(f"   Versão instalada: {html5lib.__version__}")
    print(f"   Localização: {os.path.dirname(html5lib.__file__)}")
except ImportError:
    print("\n2. ERRO: O pacote 'html5lib' NÃO foi encontrado neste ambiente.")
    print("   Isso confirma que você instalou em um local diferente de onde o script roda.")

try:
    import lxml
    print(f"\n3. Verificando 'lxml': Encontrado (Versão {lxml.__version__})")
except ImportError:
    print("\n3. Verificando 'lxml': Não encontrado.")