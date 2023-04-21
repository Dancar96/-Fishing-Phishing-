##########################################################################################################################################
#                                                                                                                                        #
#                                                                                                                                        #
#                              Extracción de parámetros de la url para su posterior análisis                                             #
#                                                                                                                                        #
#                         (Algunas de estas funciones han sido creadas apoyandome en la documentación                                    #
#                                              de la creación del dataframe original)                                                    #
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

'''
def accesibilidad_URL(url):
    pagina = None
    try:
        pagina = requests.get(url, timeout=5) # Intenta acceder a la URL proporcionada a través de requests y asigna la respuesta a 'page'
    except:
        parseo = urlparse(url)
        url = parseo.scheme+'://'+parseo.netloc # Crea una nueva URL sin "www"
        if not parseo.netloc.startswith('www'): 
            url = parseo.scheme+'://www.'+parseo.netloc
            try:
                pagina = requests.get(url, timeout=5) # Intenta acceder a la nueva URL creada a través de requests
            except:
                pagina = None
                pass
    if pagina and pagina.status_code == 200 and pagina.content not in ["b''", "b' '"]: #Si accede y el contenido no es una cadena vacía
        return True, url, pagina
    else:
        return False, None, None
    
'''
Lo siguiente que vamos a hacer, es extraer el dominio de la URL y guardarlo en una variable, lo utilizaremos más adelante.

'''
def sacar_dominio(url):
    o = urllib.parse.urlsplit(url)
    dominio = o.hostname
    subdominio = tldextract.extract(url).domain
    tlp = o.path
    return dominio, subdominio, tlp


'''
Lo siguiente será extraer todos los datos posibles de la página web mediante escrapeo.

Esta función esta extraida de la documentación de los creadores del dataframe original para la extracción de los datos necesarios.
Con esta función crearemos una serie de diccionarios con diferentes elementos que serán necesarios para las funciones que crearemos después.

'''
def extraccion_datos_URL(hostname, content, domain, Href, Link, Anchor, Media, Form, CSS, Favicon, IFrame, Title, Text):
    Null_format = ["", "#", "#nothing", "#doesnotexist", "#null", "#void", "#whatever",
               "#content", "javascript::void(0)", "javascript::void(0);", "javascript::;", "javascript"]

    soup = BeautifulSoup(content, 'html.parser', from_encoding='iso-8859-1')

    # Recolectar todos los href externos e internos de la URL
    for href in soup.find_all('a', href=True):
        dots = [x.start(0) for x in re.finditer('\.', href['href'])]
        if hostname in href['href'] or domain in href['href'] or len(dots) == 1 or not href['href'].startswith('http'):
            if "#" in href['href'] or "javascript" in href['href'].lower() or "mailto" in href['href'].lower():
                 Anchor['unsafe'].append(href['href']) 
            if not href['href'].startswith('http'):
                if not href['href'].startswith('/'):
                    Href['internals'].append(hostname+'/'+href['href']) 
                elif href['href'] in Null_format:
                    Href['null'].append(href['href'])  
                else:
                    Href['internals'].append(hostname+href['href'])   
        else:
            Href['externals'].append(href['href'])
            Anchor['safe'].append(href['href'])

    # Recolectar todas las etiquetas de src de los medios
    for img in soup.find_all('img', src=True):
        dots = [x.start(0) for x in re.finditer('\.', img['src'])]
        if hostname in img['src'] or domain in img['src'] or len(dots) == 1 or not img['src'].startswith('http'):
            if not img['src'].startswith('http'):
                if not img['src'].startswith('/'):
                    Media['internals'].append(hostname+'/'+img['src']) 
                elif img['src'] in Null_format:
                    Media['null'].append(img['src'])  
                else:
                    Media['internals'].append(hostname+img['src'])   
        else:
            Media['externals'].append(img['src'])
           
    
    for audio in soup.find_all('audio', src=True):
        dots = [x.start(0) for x in re.finditer('\.', audio['src'])]
        if hostname in audio['src'] or domain in audio['src'] or len(dots) == 1 or not audio['src'].startswith('http'):
             if not audio['src'].startswith('http'):
                if not audio['src'].startswith('/'):
                    Media['internals'].append(hostname+'/'+audio['src']) 
                elif audio['src'] in Null_format:
                    Media['null'].append(audio['src'])  
                else:
                    Media['internals'].append(hostname+audio['src'])   
        else:
            Media['externals'].append(audio['src'])
            
    for embed in soup.find_all('embed', src=True):
        dots = [x.start(0) for x in re.finditer('\.', embed['src'])]
        if hostname in embed['src'] or domain in embed['src'] or len(dots) == 1 or not embed['src'].startswith('http'):
             if not embed['src'].startswith('http'):
                if not embed['src'].startswith('/'):
                    Media['internals'].append(hostname+'/'+embed['src']) 
                elif embed['src'] in Null_format:
                    Media['null'].append(embed['src'])  
                else:
                    Media['internals'].append(hostname+embed['src'])   
        else:
            Media['externals'].append(embed['src'])
           
    for i_frame in soup.find_all('iframe', src=True):
        dots = [x.start(0) for x in re.finditer('\.', i_frame['src'])]
        if hostname in i_frame['src'] or domain in i_frame['src'] or len(dots) == 1 or not i_frame['src'].startswith('http'):
            if not i_frame['src'].startswith('http'):
                if not i_frame['src'].startswith('/'):
                    Media['internals'].append(hostname+'/'+i_frame['src']) 
                elif i_frame['src'] in Null_format:
                    Media['null'].append(i_frame['src'])  
                else:
                    Media['internals'].append(hostname+i_frame['src'])   
        else: 
            Media['externals'].append(i_frame['src'])
           

    # Recopilar todos las etiquetas links
    for link in soup.findAll('link', href=True):
        dots = [x.start(0) for x in re.finditer('\.', link['href'])]
        if hostname in link['href'] or domain in link['href'] or len(dots) == 1 or not link['href'].startswith('http'):
            if not link['href'].startswith('http'):
                if not link['href'].startswith('/'):
                    Link['internals'].append(hostname+'/'+link['href']) 
                elif link['href'] in Null_format:
                    Link['null'].append(link['href'])  
                else:
                    Link['internals'].append(hostname+link['href'])   
        else:
            Link['externals'].append(link['href'])

    for script in soup.find_all('script', src=True):
        dots = [x.start(0) for x in re.finditer('\.', script['src'])]
        if hostname in script['src'] or domain in script['src'] or len(dots) == 1 or not script['src'].startswith('http'):
            if not script['src'].startswith('http'):
                if not script['src'].startswith('/'):
                    Link['internals'].append(hostname+'/'+script['src']) 
                elif script['src'] in Null_format:
                    Link['null'].append(script['src'])  
                else:
                    Link['internals'].append(hostname+script['src'])   
        else:
            Link['externals'].append(link['href'])
           
            
    # Recopilar todos las etiquetas CSS
    for link in soup.find_all('link', rel='stylesheet'):
        dots = [x.start(0) for x in re.finditer('\.', link['href'])]
        if hostname in link['href'] or domain in link['href'] or len(dots) == 1 or not link['href'].startswith('http'):
            if not link['href'].startswith('http'):
                if not link['href'].startswith('/'):
                    CSS['internals'].append(hostname+'/'+link['href']) 
                elif link['href'] in Null_format:
                    CSS['null'].append(link['href'])  
                else:
                    CSS['internals'].append(hostname+link['href'])   
        else:
            CSS['externals'].append(link['href'])
    
    for style in soup.find_all('style', type='text/css'):
        try: 
            start = str(style[0]).index('@import url(')
            end = str(style[0]).index(')')
            css = str(style[0])[start+12:end]
            dots = [x.start(0) for x in re.finditer('\.', css)]
            if hostname in css or domain in css or len(dots) == 1 or not css.startswith('http'):
                if not css.startswith('http'):
                    if not css.startswith('/'):
                        CSS['internals'].append(hostname+'/'+css) 
                    elif css in Null_format:
                        CSS['null'].append(css)  
                    else:
                        CSS['internals'].append(hostname+css)   
            else: 
                CSS['externals'].append(css)
        except:
            continue
            
    # Recopilar todos las acciones Form
    for form in soup.findAll('form', action=True):
        dots = [x.start(0) for x in re.finditer('\.', form['action'])]
        if hostname in form['action'] or domain in form['action'] or len(dots) == 1 or not form['action'].startswith('http'):
            if not form['action'].startswith('http'):
                if not form['action'].startswith('/'):
                    Form['internals'].append(hostname+'/'+form['action']) 
                elif form['action'] in Null_format or form['action'] == 'about:blank':
                    Form['null'].append(form['action'])  
                else:
                    Form['internals'].append(hostname+form['action'])   
        else:
            Form['externals'].append(form['action'])
            

    # Recopilar todos loas etiquetas link
    for head in soup.find_all('head'):
        for head.link in soup.find_all('link', href=True):
            dots = [x.start(0) for x in re.finditer('\.', head.link['href'])]
            if hostname in head.link['href'] or len(dots) == 1 or domain in head.link['href'] or not head.link['href'].startswith('http'):
                if not head.link['href'].startswith('http'):
                    if not head.link['href'].startswith('/'):
                        Favicon['internals'].append(hostname+'/'+head.link['href']) 
                    elif head.link['href'] in Null_format:
                        Favicon['null'].append(head.link['href'])  
                    else:
                        Favicon['internals'].append(hostname+head.link['href'])   
            else:
                Favicon['externals'].append(head.link['href'])
                
        for head.link in soup.findAll('link', {'href': True, 'rel':True}):
            isicon = False
            if isinstance(head.link['rel'], list):
                for e_rel in head.link['rel']:
                    if (e_rel.endswith('icon')):
                        isicon = True
            else:
                if (head.link['rel'].endswith('icon')):
                    isicon = True
       
            if isicon:
                 dots = [x.start(0) for x in re.finditer('\.', head.link['href'])]
                 if hostname in head.link['href'] or len(dots) == 1 or domain in head.link['href'] or not head.link['href'].startswith('http'):
                     if not head.link['href'].startswith('http'):
                        if not head.link['href'].startswith('/'):
                            Favicon['internals'].append(hostname+'/'+head.link['href']) 
                        elif head.link['href'] in Null_format:
                            Favicon['null'].append(head.link['href'])  
                        else:
                            Favicon['internals'].append(hostname+head.link['href'])   
                 else:
                     Favicon['externals'].append(head.link['href'])
                     
                    
    # Recopilar todas las iFrame
    for i_frame in soup.find_all('iframe', width=True, height=True, frameborder=True):
        if i_frame['width'] == "0" and i_frame['height'] == "0" and i_frame['frameborder'] == "0":
            IFrame['invisible'].append(i_frame)
        else:
            IFrame['visible'].append(i_frame)
    for i_frame in soup.find_all('iframe', width=True, height=True, border=True):
        if i_frame['width'] == "0" and i_frame['height'] == "0" and i_frame['border'] == "0":
            IFrame['invisible'].append(i_frame)
        else:
            IFrame['visible'].append(i_frame)
    for i_frame in soup.find_all('iframe', width=True, height=True, style=True):
        if i_frame['width'] == "0" and i_frame['height'] == "0" and i_frame['style'] == "border:none;":
            IFrame['invisible'].append(i_frame)
        else:
            IFrame['visible'].append(i_frame)
          
    # Titulo de la página
    try:
        Title = soup.title.string
    except:
        pass
    
    # Recoger contenido del texto
    Text = soup.get_text()
    
    return Href, Link, Anchor, Media, Form, CSS, Favicon, IFrame, Title, Text


'''
Ahora toca definir las funciones según el orden de las columnas de nuestro dataframe.

Vamos a empezar con una función que nos indique si la página web aparece en el índice de Google, (google_index).

'''
def google_index(url):

    servicio = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servicio)

    google = 'https://www.google.com/webhp?hl=es&sa=X&ved=0ahUKEwjR1qmah6f-AhU8VqQEHQKCCAcQPAgJ'
    driver.get(google) # Escrapeo a google para ver si existe la pagina en google  

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
'Page_rank': Ranking de la página web.

'''
def page_rank(dominio):
    url = 'https://www.alexa.com/siteinfo/' + dominio # Escrapeo a la web de Alexa
    try:
        request = requests.get(url)
        soup = BeautifulSoup(request.text, 'html.parser')
        rank = soup.find('div', {'class': 'rank-global'}).find('strong').get_text()
        if rank:
            return int(rank.replace(',', ''))
        else:
            return 0
    except:
        return -1


'''
'Nb_hyperlinks': Número de hipervínculos en la página web.

'''
def nb_hyperlinks(Href, Link, Media, Form, CSS, Favicon): # Diccionarios con los tipos de enlaces internos y externos
    return len(Href['internals']) + len(Href['externals']) +\
            len(Link['internals']) + len(Link['externals']) +\
            len(Media['internals']) + len(Media['externals']) +\
            len(Form['internals']) + len(Form['externals']) +\
            len(CSS['internals']) + len(CSS['externals']) +\
            len(Favicon['internals']) + len(Favicon['externals'])


# Redirecciones totales (Nos servirán para otros parámetro próximos como los hipervinculos externos)

def redirecciones_totales(Href, Link, Media, Form, CSS, Favicon):
    return nb_hyperlinks(Href, Link, Media, Form, CSS, Favicon)

'''
'Traffic_web': Tráfico de la página web.

'''
def traffic_web(url):
        try: #Escrapeo a la API de Alexa y devuelve el rango como un entero
            rank = BeautifulSoup(urllib.request.urlopen("http://data.alexa.com/data?cli=10&dat=s&url=" + url).read(), "xml").find("REACH")['RANK'] 
        except:
            return 0
        return int(rank)


'''
'Nb_www': Indica si la URL contiene "www" en el nombre de host.

'''
def check_www(words_raw):
        count = 0
        for word in words_raw:
            if not word.find('www') == -1:
                count += 1
        return count


'''
'Domain_age': Antigüedad del dominio.

'''

def domain_age(dominio):
    try:
        w = whois.whois(dominio)
        creation_date = w.creation_date
        if type(creation_date) is list:
            creation_date = creation_date[0]
        age = (datetime.datetime.now() - creation_date).days
        return age
    except:
        return -1
    

'''
'Ratio_extHyperlinks': Proporción de hipervínculos externos en la página web.

'''
# Aprovechando la función de las redirecciones totales hayamos las externas
def redirecciones_externas(Href, Link, Media, Form, CSS, Favicon):
    return len(Href['externals']) + len(Link['externals']) + len(Media['externals']) +\
           len(Form['externals']) + len(CSS['externals']) + len(Favicon['externals'])

def external_hyperlinks(Href, Link, Media, Form, CSS, Favicon):
    total = redirecciones_totales(Href, Link, Media, Form, CSS, Favicon)
    if total == 0:
        return 0
    else :
        return redirecciones_externas(Href, Link, Media, Form, CSS, Favicon)/total



'''
'Longest_word_path': Longitud de la palabra más larga en la ruta de la URL sin caracteres especiales.

'''
def longest_word_length(words_raw_path):
    if len(words_raw_path) ==0:
        return 0
    return max(len(word) for word in words_raw_path)


'''
'Phish_hints': Indica si la URL contiene palabras clave asociadas con phishing.

'''
# Según la documentación del dataframe, estas son las palabras que se usaron para extraer estos datos
HINTS = ['wp', 'login', 'includes', 'admin', 'content', 'site', 'images', 'js', 'alibaba', 'css', 'myaccount', 'dropbox', 'themes', 'plugins', 'signin', 'view']
def phish_hints(url_path):
    count = 0
    for hint in HINTS:
        count += url_path.lower().count(hint)
    return count


'''
'Ratio_intHyperlinks': Proporción de hipervínculos internos en la página web.

'''
# Aprovechando la función de las redirecciones totales hayamos las externas
def redirecciones_internas(Href, Link, Media, Form, CSS, Favicon):
    return len(Href['internals']) + len(Link['internals']) + len(Media['internals']) +\
           len(Form['internals']) + len(CSS['internals']) + len(Favicon['internals'])

def internal_hyperlinks(Href, Link, Media, Form, CSS, Favicon):
    total = redirecciones_totales(Href, Link, Media, Form, CSS, Favicon)
    if total == 0:
        return 0
    else :
        return redirecciones_internas(Href, Link, Media, Form, CSS, Favicon)/total
    

'''
'Safe_anchor': Porcentaje de enlaces inseguros en la página web.

'''
def safe_anchor(Anchor): # El diccionario Anchor contiene los elementos 'rel' seguros e inseguros
    total = len(Anchor['safe']) +  len(Anchor['unsafe'])
    unsafe = len(Anchor['unsafe'])
    try:
        percentile = unsafe / float(total) * 100
    except:
        return 0
    return percentile 


'''
'Ratio_digits_url': Proporción de dígitos en la URL.

'''
def count_digits(line):
    return len(re.sub("[^0-9]", "", line)) # La expresión regular con la función '.sub' sustituye los caracteres que no son números por un string vacío


'''
'Longest_words_raw': Longitud de la palabra más larga en la URL sin caracteres especiales.

'''
def longest_word_length(words_raw):
    if len(words_raw) ==0:
        return 0
    return max(len(word) for word in words_raw) 


'''
'Length_hostname': Longitud del nombre de host en la URL.

'''
def url_length(hostname):
    return len(hostname) 


'''
'Links_in_tags': Indica si hay enlaces en las etiquetas HTML de la página web.

'''
def links_in_tags(Link): # El diccionario Link contiene los links internos y externos
    total = len(Link['internals']) +  len(Link['externals'])
    internals = len(Link['internals'])
    try:
        percentile = internals / float(total) * 100
    except:
        return 0
    return percentile


'''
'Avg_word_path': Longitud promedio de las palabras en la ruta de la URL sin caracteres especiales.

'''
def average_word_length(words_raw_path):
    if len(words_raw_path) ==0:
        return 0
    return sum(len(word) for word in words_raw_path) / len(words_raw_path)


'''
'Length_words_raw': Longitud de la URL sin caracteres especiales.

'''
def length_word_raw(words_raw):
    return len(words_raw)


'''
'Char_repeat': Indica si hay caracteres repetidos en la URL.

'''
def char_repeat(words_raw):
    def iguales(items):
        return all(x == items[0] for x in items) #mira si son todos los caracteres iguales
    repeat = {'2': 0, '3': 0, '4': 0, '5': 0}
    part = [2, 3, 4, 5]
    for word in words_raw:
        for char_repeat_count in part:
            for i in range(len(word) - char_repeat_count + 1):
                sub_word = word[i:i + char_repeat_count]
                if iguales(sub_word):
                    repeat[str(char_repeat_count)] = repeat[str(char_repeat_count)] + 1
    return sum(list(repeat.values()))


'''
'Domain_registration_length': Longitud del registro del dominio.

'''
def domain_registration_length(dominio, subdominio, tlp):
    longitud_dominio = len(dominio + subdominio + tlp)
    return longitud_dominio


'''
'Ratio_extRedirection': Proporción de redirecciones externas en la página web.

'''
def num_enlacesExt(Href, Link, Media, Form, CSS, Favicon):
    count = 0
    for link in Href['externals']:
        try:
            r = requests.get(link)
            if len(r.history) > 0:
                count+=1
        except:
            continue
    for link in Link['externals']:
        try:
            r = requests.get(link)
            if len(r.history) > 0:
                count+=1
        except:
            continue
    for link in Media['externals']:
        try:
            r = requests.get(link)
            if len(r.history) > 0:
                count+=1
        except:
            continue
    for link in Media['externals']:
        try:
            r = requests.get(link)
            if len(r.history) > 0:
                count+=1
        except:
            continue 
    for link in Form['externals']:
        try:
            r = requests.get(link)
            if len(r.history) > 0:
                count+=1
        except:
            continue    
    for link in CSS['externals']:
        try:
            r = requests.get(link)
            if len(r.history) > 0:
                count+=1
        except:
            continue    
    for link in Favicon['externals']:
        try:
            r = requests.get(link)
            if len(r.history) > 0:
                count+=1
        except:
            continue    
    return count

def external_redirection(Href, Link, Media, Form, CSS, Favicon):
    externals = redirecciones_externas(Href, Link, Media, Form, CSS, Favicon)
    if (externals>0):
        return num_enlacesExt(Href, Link, Media, Form, CSS, Favicon)/externals
    return 0


'''
'Shortest_word_host': Longitud de la palabra más corta en el nombre de host de la URL sin caracteres especiales.

'''
def shortest_word_length(words_raw_host):
    if len(words_raw_host) ==0:
        return 0
    return min(len(word) for word in words_raw_host)


'''
'Ratio_digits_host': Proporción de dígitos en el nombre de host de la URL.

'''
def ratio_digits(hostname):
    return len(re.sub("[^0-9]", "", hostname))/len(hostname)


'''
'Nb_slash': Número de barras diagonales en la URL.

'''
def count_slash(full_url):
    return full_url.count('/')


'''
'Shortest_word_path': Longitud de la palabra más corta en la ruta de la URL sin caracteres especiales.

'''
def shortest_word_length(words_raw_path):
    if len(words_raw_path) ==0:
        return 0
    return min(len(word) for word in words_raw_path)


'''
'Domain_in_title': Indica si el nombre de dominio está incluido en el título de la página web.

'''
def domain_in_title(domain, title):
    if domain.lower() in title.lower(): 
        return 0
    return 1


'''
'Nb_dots': Número de puntos en la URL.

'''
def count_dots(hostname):
    return hostname.count('.')


'''
'Nb_hyphens': número de guiones en la URL.

'''
def count_hyphens(base_url):
    return base_url.count('-')


'''
'Avg_words_raw': Longitud promedio de las palabras en la URL sin caracteres especiales.

'''
def average_word_length(words_raw):
    if len(words_raw) ==0:
        return 0
    return sum(len(word) for word in words_raw) / len(words_raw)


'''
Esta será la función que utilizaremos para extraer todos los parámetros y convertirlos en una lista del mismo orden que las 
filas y columnas del dataframe de nuestro modelo.

'''
def extraccion_parametros(url):
    
    def extraccion_palabras(domain, subdomain, path):
        w_domain = re.split("\-|\.|\/|\?|\=|\@|\&|\%|\:|\_", domain.lower())
        w_subdomain = re.split("\-|\.|\/|\?|\=|\@|\&|\%|\:|\_", subdomain.lower())   
        w_path = re.split("\-|\.|\/|\?|\=|\@|\&|\%|\:|\_", path.lower())
        raw_words = w_domain + w_path + w_subdomain
        w_host = w_domain + w_subdomain
        raw_words = list(filter(None,raw_words))
        return raw_words, list(filter(None,w_host)), list(filter(None,w_path))

    
    Href = {'internals':[], 'externals':[], 'null':[]}
    Link = {'internals':[], 'externals':[], 'null':[]}
    Anchor = {'safe':[], 'unsafe':[], 'null':[]}
    Media = {'internals':[], 'externals':[], 'null':[]}
    Form = {'internals':[], 'externals':[], 'null':[]}
    CSS = {'internals':[], 'externals':[], 'null':[]}
    Favicon = {'internals':[], 'externals':[], 'null':[]}
    IFrame = {'visible':[], 'invisible':[], 'null':[]}
    Title =''
    Text= ''
    state, iurl, page = accesibilidad_URL(url)
    if state:
        content = page.content
        hostname, domain, path = sacar_dominio(url)
        extracted_domain = tldextract.extract(url)
        domain = extracted_domain.domain+'.'+extracted_domain.suffix
        subdomain = extracted_domain.subdomain
        tmp = url[url.find(extracted_domain.suffix):len(url)]
        pth = tmp.partition("/")
        path = pth[1] + pth[2]
        words_raw, words_raw_host, words_raw_path= extraccion_palabras(extracted_domain.domain, subdomain, pth[2])
        tld = extracted_domain.suffix
        parsed = urlparse(url)
        scheme = parsed.scheme
        
        Href, Link, Anchor, Media, Form, CSS, Favicon, IFrame, Title, Text = extraccion_datos_URL(hostname, content, domain, Href, Link, Anchor, Media, Form, CSS, Favicon, IFrame, Title, Text)

        row = [google_index(url),
               page_rank(domain),
               nb_hyperlinks(Href, Link, Media, Form, CSS, Favicon),
               traffic_web(url),
               check_www(words_raw),
               domain_age(domain),
               external_hyperlinks(Href, Link, Media, Form, CSS, Favicon),
               longest_word_length(words_raw_path),
               phish_hints(url),
               internal_hyperlinks(Href, Link, Media, Form, CSS, Favicon),
               safe_anchor(Anchor),
               count_digits(domain),
               longest_word_length(words_raw),
               url_length(hostname),
               links_in_tags(Link),
               average_word_length(words_raw_path),
               length_word_raw(words_raw),
               char_repeat(words_raw),
               domain_registration_length(url),
               external_redirection(Href, Link, Media, Form, CSS, Favicon),
               shortest_word_length(words_raw_host),
               ratio_digits(hostname),
               count_slash(url),
               shortest_word_length(words_raw_path),
               domain_in_title(extracted_domain.domain, Title),
               count_dots(hostname),
               count_hyphens(url),
               average_word_length(words_raw)]
        return row
    return None


'''
Haremos una función que preprocese la fila creada.

'''
def preprocesar_fila(fila):
    fila = fila.fillna(0) # Eliminar valores faltantes
    # Seleccionar columnas de tipo object
    cols = fila.select_dtypes(include=['object']).index
    # Convertir columnas de tipo object a int
    for col in cols:
        fila[col] = int(fila[col])
    return fila
