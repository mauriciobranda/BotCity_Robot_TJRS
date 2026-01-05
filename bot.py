from botcity.web import WebBot, By
from botcity.maestro import *
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
import os

BotMaestroSDK.RAISE_NOT_CONNECTED = False

def main():
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()
    
    print(f"Task ID: {execution.task_id}")
    print(f"Parâmetros: {execution.parameters}")
    
    bot = WebBot()
    bot.headless = True
    bot.driver_path = ChromeDriverManager().install()
    
    # Lê lista de consultas
    consultas = ler_consultas("consultas.csv")
    print(f"Total de pessoas a consultar: {len(consultas)}")
    
    todos_processos = []
    total_processados = 0
    total_falhas = 0
    
    for consulta in consultas:
        nome = consulta["nome"]
        url = consulta["url"]
        
        print(f"\n--- Consultando: {nome} ---")
        
        try:
            bot.browse(url)
            
            elemento = bot.find_element(".mat-mdc-row", By.CSS_SELECTOR, waiting_time=15000)
            
            if not elemento:
                print(f"Nenhum processo encontrado para {nome}")
                total_processados += 1
                continue
            
            time.sleep(2)
            
            processos = extrair_tabela(bot, nome)
            todos_processos.extend(processos)
            
            print(f"Encontrados {len(processos)} processos para {nome}")
            total_processados += 1
            
        except Exception as e:
            print(f"Erro ao consultar {nome}: {e}")
            total_falhas += 1
    
    bot.stop_browser()
    
    # Salva CSV com todos os resultados
    arquivo_saida = "processos_resultado.csv"
    salvar_csv(todos_processos, arquivo_saida)
    print(f"\nArquivo {arquivo_saida} gerado com {len(todos_processos)} processos")
    
    # Envia para o Maestro
    if os.path.exists(arquivo_saida):
        maestro.post_artifact(
            task_id=execution.task_id,
            artifact_name=arquivo_saida,
            filepath=arquivo_saida
        )
    
    maestro.finish_task(
        task_id=execution.task_id,
        status=AutomationTaskFinishStatus.SUCCESS,
        message=f"Extraídos {len(todos_processos)} processos de {total_processados} pessoas",
        total_items=len(consultas),
        processed_items=total_processados,
        failed_items=total_falhas
    )


def ler_consultas(arquivo):
    """Lê arquivo CSV com lista de consultas."""
    consultas = []
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if len(row) >= 3:
                consultas.append({
                    "nome": row[0].strip(),
                    "status": row[1].strip(),
                    "url": row[2].strip()
                })
    
    return consultas


def extrair_tabela(bot, nome_consultado):
    """Extrai dados da tabela de processos."""
    processos = []
    linhas = bot.find_elements(".mat-mdc-row", By.CSS_SELECTOR)
    
    for linha in linhas:
        try:
            processo = {
                "nome_consultado": nome_consultado,
                "numero": linha.find_element(By.CSS_SELECTOR, ".mat-column-numeroProcesso a").text.strip(),
                "parte": linha.find_element(By.CSS_SELECTOR, ".mat-column-parte p").text.strip(),
                "comarca": linha.find_element(By.CSS_SELECTOR, ".mat-column-comarca p").text.strip(),
                "classe_cnj": linha.find_element(By.CSS_SELECTOR, ".mat-column-classeCNJ p").text.strip(),
                "movimento": linha.find_element(By.CSS_SELECTOR, ".mat-column-situacao p").text.strip(),
                "data_ultimo_movimento": linha.find_element(By.CSS_SELECTOR, ".mat-column-dataUltimoMovimento p").text.strip(),
            }
            processos.append(processo)
        except Exception as e:
            print(f"Erro ao extrair linha: {e}")
            continue
    
    return processos


def salvar_csv(processos, arquivo):
    """Salva lista de processos em CSV."""
    if not processos:
        print("Nenhum processo para salvar")
        return
    
    with open(arquivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=processos[0].keys(), delimiter=';')
        writer.writeheader()
        writer.writerows(processos)


if __name__ == '__main__':
    main()