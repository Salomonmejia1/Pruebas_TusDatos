from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import time


#Iniciando consultas
consultas = ["0968599020001"]#, "1265336646464"]
def consulta_per_autor(ids):  
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    #options.add_argument('--headless')  # Ejecutar en modo headless (sin ventana gráfica)

    s = Service(r"chromedriver-win32\chromedriver.exe")
    driver = webdriver.Chrome(service=s, options=options) 

    # inicializando el navegador
    driver.get("https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros")
        
    try:
        element1 = (By.ID,'mat-input-1')
        element2 = (By.CSS_SELECTOR, "button.boton-buscar mdc-button mdc-button--raised mat-mdc-raised-button mat-accent mat-mdc-button-base".replace(" ","."))

        tarea1 = WebDriverWait(driver, 5)\
                    .until(EC.visibility_of_element_located(element1))
        tarea1.send_keys(str(ids))
        tarea2 = WebDriverWait(driver,5).until(EC.element_to_be_clickable(element2))
        tarea2.click()
        element3 = (By.XPATH, "/html/body/app-root/app-expel-listado-juicios/expel-sidenav/mat-sidenav-container/mat-sidenav-content/section/section")
        tarea3 = WebDriverWait(driver,10).until(EC.element_to_be_clickable(element3))
        texto_informacion = driver.find_element(By.XPATH,"/html/body/app-root/app-expel-listado-juicios/expel-sidenav/mat-sidenav-container/mat-sidenav-content/section/section")
        texto_informacion = texto_informacion.text
        texto_columnas = texto_informacion.split("\n")
        print(texto_columnas)
        input("Presiona Enter para cerrar el navegador...")
        print(f"consulta {ids} realizada")
    except Exception as e:    
        print(f"no se pudo hacer la consulta{ids}")
    finally: 
        driver.quit()
    return ids

def paralelizar_consultas(ids, max_workers=5):
    resultados = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(consulta_per_autor, id): id for id in ids}
        print(future_to_id)
        for future in as_completed(future_to_id):
            id = future_to_id[future]
            print(future)
            try:
                id, data = future.result()
                if data:
                    resultados.append((id, data))
            except Exception as exc:
                print(f'Error en la consulta del ID {id}: {exc}')
    
    return resultados


resultados = paralelizar_consultas(consultas)



input("Presiona Enter para cerrar el navegador...")

