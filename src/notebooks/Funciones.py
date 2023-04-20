##########################################################################################################################################
#                                                                                                                                        #
#                                                                                                                                        #
#                              Extracción de parámetros de la url para su posterior análisis                                             #
#                                                                                                                                        #
#                                                                                                                                        #
##########################################################################################################################################

'''
Vamos a crear una función que, mediante diferentes funciones, extraiga todos los parámetros que necesitamos en el orden de las columnas
del dataframe del que hemos 'enseñado' al modelo para realizar la predicción.

En primer lugar, vamos a importar todas las bibliotecas necesarias:

'''
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import whois
import time
import re
import urllib
import tldextract
import json
import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from urllib.parse import urlparse

'''
Lo primero que vamos a tener que comprobar es si la url es accesible o no.

Esta función comprueba si una URL dada es accesible y devuelve una tupla de tres elementos: 
el primero es un valor booleano que indica si la URL es accesible o no, el segundo elemento es la URL que se comprobó y el tercer elemento,
es la página web recuperada como respuesta de la solicitud HTTP. Usamos "requests" para hacer la solicitud HTTP a la URL. 
Si la solicitud se completa con éxito, el código de estado HTTP de la respuesta es verificado. Si el código es 200 y 
el contenido de la página no está vacío, la función devuelve True, la URL y la página web. Si la solicitud HTTP falla, 
la función intenta resolver la URL eliminando cualquier subdominio (es decir, la "www" al principio de la URL) 
y vuelve a intentar la solicitud. Si aún falla, la función devuelve False y dos valores nulos para el segundo y tercer elemento de la tupla.

'''
def accesibilidad_URL(url):
    pagina = None
    try:
        pagina = requests.get(url, timeout=5)   
    except:
        parseo = urlparse(url)
        url = parseo.scheme+'://'+parseo.netloc
        if not parseo.netloc.startswith('www'):
            url = parseo.scheme+'://www.'+parseo.netloc
            try:
                pagina = requests.get(url, timeout=5)
            except:
                pagina = None
                pass
    if pagina and pagina.status_code == 200 and pagina.content not in ["b''", "b' '"]:
        return True, url, pagina
    else:
        return False, None, None
    
'''
Lo siguiente que vamos a hacer, es extraer el dominio de la URL y guardarlo en una variable, lo utilizaremos más adelante.

Esta función obtiene información sobre el dominio de una URL dada y devuelve una tupla de tres elementos: el nombre de host (hostname), 
el subdominio y la ruta (path). La función utiliza la biblioteca de Python "urllib" para analizar la URL en sus componentes. 
El método "urlsplit" divide la URL en componentes como el protocolo, el nombre de host, la ruta, los parámetros y la consulta. 
La variable "o" guarda estos componentes. Luego, se utiliza la biblioteca "tldextract" para extraer el dominio de nivel superior (TLD) 
de la URL y obtener el nombre de dominio (domain) y el subdominio (subdomain). El resultado se devuelve como una tupla, 
donde el primer elemento es el nombre de host, el segundo es el nombre de dominio y el tercer elemento es la ruta.
En el código que se muestra, la función "get_domain" se llama con una URL específica y el resultado se almacena en la variable "x". 
Luego, se crea la variable "dominio" al concatenar el primer y segundo elemento de la tupla "x", que corresponde al nombre de host 
y al nombre de dominio, respectivamente. Finalmente, se imprime el resultado utilizando la cadena de formato f-string y los valores 
de las variables "x". Se muestra el nombre del dominio, el subdominio y el TLD por separado.

'''
def sacar_dominio(url):
    o = urllib.parse.urlsplit(url)
    return o.hostname, tldextract.extract(url).domain, o.path

x = sacar_dominio('url')

dominio = ''.join(x)

print(f'Dominio: {x[0]}, Subdominio: {x[1]}, Top-Level Domain: {x[2]}')

dominio = x[0]
subdominio = x[1]

'''
Una vez hemos realizado amos a ir definiendo las funciones según el orden de las columnas de nuestro dataframe.

Vamos a empezar con una función que nos indique si la página web NO aparece en el índice de Google, (non_google_index).

Este es un script de Python que utiliza Selenium y ChromeDriver para determinar si una URL dada está indexada en Google. La función "non_google_index" toma una URL como entrada y devuelve un número que indica si la URL está indexada en Google o no.
Primero, se instala ChromeDriver y se inicia un servicio. Luego, se inicializa un objeto "webdriver" para controlar el navegador Chrome. La URL de Google se carga en el navegador.
Después, se encuentra el botón "Aceptar" en la página y se hace clic en él. Se espera unos segundos para que la página se cargue completamente.
Luego, se encuentra el cuadro de búsqueda de Google en la página y se escribe la consulta de búsqueda "site:URL" en él, donde "URL" es la URL de entrada. Esto busca todas las páginas indexadas por Google que pertenecen al sitio web especificado por la URL.
Se espera unos segundos más para que se carguen los resultados de búsqueda y se hace clic en el botón de búsqueda (tecla ENTER).
A continuación, se espera unos segundos para que la página de resultados de búsqueda se cargue completamente. Se busca el primer resultado de la búsqueda que aparece en la página y se extrae el texto de la URL.
Si la URL buscada coincide exactamente con la URL extraída del primer resultado de búsqueda de Google, significa que la URL está indexada en Google y la función devuelve 0. Si no hay coincidencia, significa que la URL no está indexada en Google y la función devuelve 1.

'''

def non_google_index(url):

    servicio = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servicio)

    google = 'https://www.google.com/webhp?hl=es&sa=X&ved=0ahUKEwjR1qmah6f-AhU8VqQEHQKCCAcQPAgJ'
    driver.get(google)

    aceptar = driver.find_element(By.ID, "L2AGLb")
    aceptar.click()
    time.sleep(5)
    buscar = driver.find_element(By.ID, 'APjFqb')
    buscar.send_keys(f'site:{url}')
    time.sleep(5)
    buscar.send_keys(Keys.ENTER)
    time.sleep(5)
    try:
        url_1 = driver.find_element(By.CLASS_NAME, "qLRx3b.tjvcx.GvPZzd.cHaqb")
        url_text = url_1.text
    except:
        url_text = '0'
    url_text = url_text[:(len(url) + 1)]
    if url == url_text:
        google_index = 0
    else:
        google_index = 1
    return google_index

'''
Este es un código de Python muy sencillo que define una función llamada "domain_registration_length". 
La función toma una cadena como argumento (que se espera que sea un nombre de dominio) y devuelve la longitud de la cadena 
(es decir, el número de caracteres que contiene). En este caso, la función simplemente asigna la longitud de la cadena "domain" 
a una variable llamada "longitud_dominio" utilizando la función len(), y luego devuelve esta variable. Es decir, esta función 
devuelve el número de caracteres del nombre de dominio proporcionado como entrada. Este código por sí solo no proporciona información 
útil sobre el registro del dominio, sino que solo se enfoca en la longitud del nombre del dominio.

'''

def domain_registration_length(dominio):
    longitud_dominio = len(dominio)
    return longitud_dominio

'''
Este es un código de Python que utiliza BeautifulSoup y urllib para obtener el ranking de tráfico de un sitio web proporcionado como 
entrada. La función "web_traffic" toma una URL como argumento y devuelve el ranking de tráfico del sitio web como un número entero.
El código utiliza la biblioteca BeautifulSoup para analizar el XML devuelto por la API de Alexa, que proporciona datos de tráfico del sitio 
web. La URL se concatena con la URL de la API de Alexa y se utiliza urllib para abrir una conexión y leer el contenido devuelto por la API.
Luego, se utiliza BeautifulSoup para buscar el elemento "REACH" en el archivo XML y extraer el valor de "RANK" como una cadena. 
Si no se encuentra el elemento "REACH", se devuelve 0. Finalmente, el valor de "RANK" se convierte a un número entero y se devuelve como 
el ranking de tráfico del sitio web. Cabe señalar que Alexa es una fuente de datos de tráfico de sitios web muy popular, pero sus datos 
pueden no ser 100% precisos o actualizados en todo momento. Además, este código solo devuelve el ranking de tráfico del sitio web, 
no proporciona información detallada sobre su tráfico.

'''

def web_traffic(url):
        try:
            rank = BeautifulSoup(urllib.request.urlopen("http://data.alexa.com/data?cli=10&dat=s&url=" + url).read(), "xml").find("REACH")['RANK']
        except:
            return 0
        return int(rank)

'''
Este es un código de Python que define una función llamada "safe_anchor". La función toma un diccionario como entrada, que se espera 
que tenga dos claves llamadas "safe" y "unsafe", y devuelve el porcentaje de enlaces inseguros en la lista de enlaces proporcionada en 
el diccionario. La función primero calcula la longitud total de las listas "safe" y "unsafe" utilizando la función len(). Luego, calcula 
la longitud de la lista "unsafe" y almacena el valor en una variable llamada "unsafe". Luego, la función intenta calcular el porcentaje 
de enlaces inseguros dividiendo la longitud de la lista "unsafe" por la longitud total de ambas listas y multiplicando el resultado por 100. 
Si la longitud total de ambas listas es cero o no se puede dividir, la función devuelve 0.
Finalmente, la función devuelve el porcentaje de enlaces inseguros calculado como un número de punto flotante.

'''

def safe_anchor(Anchor):
    total = len(Anchor['safe']) +  len(Anchor['unsafe'])
    unsafe = len(Anchor['unsafe'])
    try:
        percentile = unsafe / float(total) * 100
    except:
        return 0
    return percentile

'''
Este es un código de Python que define una función llamada "check_www". La función toma una lista de cadenas de texto como entrada 
(que se espera que contenga palabras) y cuenta cuántas de estas palabras contienen la subcadena "www". 
La función utiliza un bucle "for" para iterar sobre cada palabra en la lista de entrada. Luego, utiliza el método "find" de Python para 
buscar la subcadena "www" en cada palabra. Si la subcadena no se encuentra en la palabra, el método "find" devuelve -1. Por lo tanto, 
si la condición "not word.find('www') == -1" es verdadera, significa que la palabra contiene la subcadena "www".
En cada iteración del bucle "for" donde se encuentra una palabra que contiene "www", se incrementa la variable "count" en 1.
Finalmente, la función devuelve el número total de palabras en la lista de entrada que contienen la subcadena "www" como un número entero.

'''

def check_www(words_raw):
        count = 0
        for word in words_raw:
            if not word.find('www') == -1:
                count += 1
        return count

'''


'''