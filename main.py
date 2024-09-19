import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd


def ler_planilha():
    diretorio = os.path.dirname(os.path.abspath(__file__))
    planilha = os.path.join(diretorio, "sheet/lista_cnpj.xlsx")
    return pd.read_excel(planilha)

def acessar_url_caixa(driver):
    driver.get("https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf")


def limpar_cnpj(cnpj):
    return re.sub(r'\D', '', cnpj)

def preencher_inscricao(driver, cnpj):
    time.sleep(3)
    inscricao = driver.find_element(By.ID, "mainForm:txtInscricao1")
    inscricao.send_keys(cnpj)  # Preencher com o CNPJ do empregador

# TODO: Verificar lib para quebra de captcha
def quebra_captcha():
    pass

def main():

    driver = webdriver.Chrome()

    df = ler_planilha()

    for cnpj in df['CNPJ']:
        try:
            acessar_url_caixa(driver)
            preencher_inscricao(driver, limpar_cnpj(cnpj))
            time.sleep(10)
            driver.quit()
        finally:
            driver.quit()

if __name__ == "__main__":
    main()
