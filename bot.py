from botcity.web import WebBot, By
from webdriver_manager.chrome import ChromeDriverManager
import time

def main():
    bot = WebBot()
    bot.headless = False
    bot.driver_path = ChromeDriverManager().install()
    
    url = "https://consulta.tjrs.jus.br/consulta-processual/partes/processos-por-nome?parteSelecionadaNome=BALDASAR%20PEDRO%20ODIA&comarca=&tipoPesquisa=F&movimentados=0&parteSelecionadaCodParte1g=11580675230128598926398550751&parteSelecionadaCpfCnpj=543.1**.***-**&parteSelecionadaFrom=eproc"
    
    bot.browse(url)
    
    # Aguarda tabela carregar (syntax correta do BotCity)
    elemento = bot.find_element(".mat-mdc-row", By.CSS_SELECTOR, waiting_time=15000)
    
    if not elemento:
        print("Tabela não carregou!")
        bot.stop_browser()
        return
    
    # Pausa extra para renderização completa
    time.sleep(2)
    
    # Extrai dados
    processos = extrair_tabela(bot)
    
    for p in processos:
        print(p)
    
    bot.stop_browser()


def extrair_tabela(bot):
    """Extrai dados da tabela de processos."""
    processos = []
    
    linhas = bot.find_elements(".mat-mdc-row", By.CSS_SELECTOR)
    
    for linha in linhas:
        processo = {
            "numero": linha.find_element(By.CSS_SELECTOR, ".mat-column-numeroProcesso a").text.strip(),
            "parte": linha.find_element(By.CSS_SELECTOR, ".mat-column-parte p").text.strip(),
            "comarca": linha.find_element(By.CSS_SELECTOR, ".mat-column-comarca p").text.strip(),
            "classe_cnj": linha.find_element(By.CSS_SELECTOR, ".mat-column-classeCNJ p").text.strip(),
            "movimento": linha.find_element(By.CSS_SELECTOR, ".mat-column-situacao p").text.strip(),
            "data_ultimo_movimento": linha.find_element(By.CSS_SELECTOR, ".mat-column-dataUltimoMovimento p").text.strip(),
        }
        processos.append(processo)
    
    return processos


if __name__ == '__main__':
    main()