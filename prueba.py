from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import json
import argparse

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
        try:
            element3 = (By.XPATH, "/html/body/app-root/app-expel-listado-juicios/expel-sidenav/mat-sidenav-container/mat-sidenav-content/section/section")
            tarea3 = WebDriverWait(driver,10).until(EC.element_to_be_clickable(element3)) #uso dependiendo de la velocidad de conexion
            texto_informacion = driver.find_element(By.XPATH,"/html/body/app-root/app-expel-listado-juicios/expel-sidenav/mat-sidenav-container/mat-sidenav-content/section/section")
            texto_columnas = texto_informacion.text.split("\n")
            cons_no = int(len(texto_columnas)/5 -1)
            text_process = {}
                        
            for i in range(0,cons_no, 1):
                element4 = (By.XPATH,f"/html/body/app-root/app-expel-listado-juicios/expel-sidenav/mat-sidenav-container/mat-sidenav-content/section/section/div[2]/div[{i+1}]/div[5]/a/mat-icon")
                tarea4 = WebDriverWait(driver,20).until(EC.element_to_be_clickable(element4))
                tarea4.click()
                element5 = (By.XPATH,f"/html/body/app-root/app-expel-listado-movimientos/expel-sidenav/mat-sidenav-container/mat-sidenav-content/section/section/div/div[2]/div/div[2]/div/div[5]/a/mat-icon" )
                tarea5 = WebDriverWait(driver,20).until(EC.element_to_be_clickable(element5))
                tarea5.click()
                element6 = (By.XPATH,"/html/body/app-root/app-expel-listado-actuaciones/expel-sidenav/mat-sidenav-container/mat-sidenav-content/section/section[2]/header/section[1]/section[2]/div/button[1]/span[2]")
                tarea6 = WebDriverWait(driver,20).until(EC.element_to_be_clickable(element6))
                tarea6.click()
                text_info = driver.find_element(By.XPATH, "/html/body/app-root/app-expel-listado-actuaciones/expel-sidenav/mat-sidenav-container/mat-sidenav-content/section/expel-informacion-busqueda/header")
                texto_columnas_info = text_info.text.split("\n")[6:] 
                text_process[f"Datos generales {i+1}"] = texto_columnas_info
                text_details = driver.find_element(By.XPATH, "/html/body/app-root/app-expel-listado-actuaciones/expel-sidenav/mat-sidenav-container/mat-sidenav-content/section/section[2]/mat-accordion")
                texto_columnas_details = text_details.text.split("\n")
                text_process[f"Detalles {i+1}"] = texto_columnas_details
                element7 = (By.CSS_SELECTOR,"button.botones btn-regresar mdc-button mat-mdc-button mat-primary mat-mdc-button-base".replace(" ",".")) 
                tarea7 =WebDriverWait(driver,30).until(EC.element_to_be_clickable(element7))
                tarea7.click()
                tarea8 = WebDriverWait(driver,30).until(EC.element_to_be_clickable(element7))
                tarea8.click()
                            
        except: 
            texto_informacion = f"El Id{ids} no tiene información"
            text_process= texto_informacion.split("\n")
            
    except Exception as e:    
        print(f"el ID: {ids} no tiene informacion")
    finally: 
        driver.quit()
    return ids, text_process

def paralelizar_consultas(ids, max_workers=10):
    resultados = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(consulta_per_autor, id): id for id in ids}
        for future in as_completed(future_to_id):
            id = future_to_id[future]
            try:
                id, data = future.result()
                if data:
                    resultados.append((id, data))
                    print(f"consulta {id} realizada")
            except Exception as exc:
                print(f'Error en la consulta del ID {id}: {exc}')
    
    return resultados

def data_precessing(data):
    json_data = {}
    for i in range(0, len(data), 2):
        key = data[i].strip()
        value = data[i+1].strip() if i+1 < len(data) else ''
        json_data[key] = value

    return json_data
    
def add_data (data):
    titulos = ['Número de proceso',
                'Fecha ingreso',
                'Materia',
                'Tipo de acción',
                'Delito/Asunto',
                'Judicatura',
                'Tipo de Ingreso',
                'No. proceso vinculado',
                'Actor/Ofendido:',
                'Demandado/Procesado:']
    
    for resultado in data:
        interations = int(len(resultado[1])/2)
        for j in range(interations):
            for i in range(len(titulos) - 1):
                if titulos[i] in resultado[1][f"Datos generales {j+1}"] and titulos[i+1] in resultado[1][f"Datos generales {j+1}"]:
                    index_i = resultado[1][f"Datos generales {j+1}"].index(titulos[i])
                    index_i1 = resultado[1][f"Datos generales {j+1}"].index(titulos[i+1])
                    if abs(index_i1 - index_i) < 2:
                        resultado[1][f"Datos generales {j+1}"].insert(index_i1, " ")
        
    return data

def data2json(data):

    for resultado in data:
        interations = int(len(resultado[1])/2)
        for i in range (interations): 
                resultado[1][f"Datos generales {i+1}"] = data_precessing(resultado[1][f"Datos generales {i+1}"])

    return data
    

def run(consultas):

    print(print(f"Lista de ids: {consultas}"))

    resultados = paralelizar_consultas(consultas)

    resultados_ = add_data(resultados)

    resultados_finales = data2json(resultados_)

    with open("prueba3.json", "w", encoding='utf8') as json_file:
        json.dump(resultados_, json_file, ensure_ascii=False, indent=4)
    
if __name__=='__main__':

    #consultas = ["0968599020001", "0992339411001"]

    parser = argparse.ArgumentParser(description="Lista de Ids para consultar")
    parser.add_argument('--ids', type=str, nargs='+', help='Lista de Ids')
    args = parser.parse_args()

    run(args.ids)


