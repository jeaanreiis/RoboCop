import re
import os
import time
import requests

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
    inscricao = driver.find_element(By.ID, "mainForm:txtInscricao1")
    inscricao.send_keys(cnpj)  # Preencher com o CNPJ do empregador

def preencher_captcha(driver, texto):
    captcha = driver.find_element(By.ID, "mainForm:txtCaptcha")
    captcha.clear()
    time.sleep(2)
    captcha.send_keys(texto) 

def pega_captcha(driver):

    # Identifica o elemento do CAPTCHA
    captcha = driver.find_element(By.ID, "captchaImg_N2")

    # Salva a imagem do CAPTCHA
    captcha.screenshot('captcha.png')

    print("Captcha carregado!")

def quebra_captcha():
    time.sleep(2)

    # Carrega a imagem em escala de cinza
    img = cv2.imread('captcha.png', cv2.IMREAD_GRAYSCALE)

    # Pré-processamento
    # Binarização (adapta o limiar automaticamente)
    thresh = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Remoção de ruído (filtro mediana)
    denoised = cv2.medianBlur(thresh, 1)

    # Dilatação (engrossa as linhas)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    dilated = cv2.dilate(denoised, kernel, iterations=1)

    # Salvar a imagem pré-processada para visualizar (opcional)
    cv2.imwrite('captcha_processado.png', dilated)

    # Reconhecimento de texto
    texto = pytesseract.image_to_string(dilated, config='--psm 7')

    print("Resolução do CAPTCHA:", texto)
    return texto.strip()  # Retorna o texto do CAPTCHA limpo

def consultar_cnpj(driver):
    driver.find_element(By.ID, "mainForm:btnConsultar").click()

def valida_captcha(driver):
    time.sleep(5)
    msg = driver.find_element(By.CLASS_NAME, "feedback-text")
    if "Inválido" in msg.text:
        atualizar_captcha(driver)
        time.sleep(2)
        pega_captcha(driver)
        texto = quebra_captcha()
        preencher_captcha(driver, texto)
        consultar_cnpj(driver)
        valida_captcha(driver)

        print("O CAPTCHA não foi resolvido!")
def atualizar_captcha(driver):
    novo_captcha = driver.find_element(By.ID, "mainForm:j_id61")
    novo_captcha.click()

def consulta_historico(driver):
    historico = driver.find_element(By.ID, "mainForm:j_id51")
    historico.click()

def visualizar_doc(driver):
    btn_visualizar = driver.find_element(By.ID, "mainForm:btnVisualizar")
    btn_visualizar.click()

def imprimir(driver):
    btn_imprimir = driver.find_element(By.ID, "mainForm:btImprimir4")
    btn_imprimir.click()

def baixar_pdf(driver):
    # TODO: Criar function para baixar pdf via request cookies
    pass

def main():

    driver = webdriver.Chrome()
    driver.implicitly_wait(5)

    df = ler_planilha()

    for cnpj in df['CNPJ']:
        try:
            acessar_url_caixa(driver)
            preencher_inscricao(driver, limpar_cnpj(cnpj))
            pega_captcha(driver)  # Captura o CAPTCHA
            preencher_captcha(driver, quebra_captcha())  # Preenche o CAPTCHA
            consultar_cnpj(driver)  # Consulta o CNPJ
            valida_captcha(driver) 
            consulta_historico(driver)
            visualizar_doc(driver)
            imprimir(driver)
            time.sleep(5)
        finally:
            driver.quit()

if __name__ == "__main__":
    main()
