import re
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

from PIL import Image
import pytesseract
import cv2
import numpy as np

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

def quebra_captcha():
    # Carrega a imagem em escala de cinza
    img = cv2.imread('captcha.png', cv2.IMREAD_GRAYSCALE)

    # Pré-processamento
    # Binarização (adapta o limiar automaticamente)
    thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Remoção de ruído (filtro mediana)
    denoised = cv2.medianBlur(thresh, 1)

    # TODO: Preciso ajustar configurações e realizar mais testes
    # Dilatação (engrossa as linhas)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    dilated = cv2.dilate(denoised, kernel, iterations=1)

    # Salvar a imagem pré-processada para visualizar (opcional)
    cv2.imwrite('captcha_processed.png', dilated)

    # Reconhecimento de texto
    texto = pytesseract.image_to_string(dilated, config='--psm 7')

    print("Resolução do CAPTCHA:", texto)

def main():

    driver = webdriver.Chrome()
    driver.implicitly_wait(5)

    df = ler_planilha()

    for cnpj in df['CNPJ']:
        try:
            acessar_url_caixa(driver)
            preencher_inscricao(driver, limpar_cnpj(cnpj))
            quebra_captcha()
            driver.quit()
        finally:
            driver.quit()

if __name__ == "__main__":
    main()
