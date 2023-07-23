---
layout: post
title: Burp Suite Extension&#58; WAF Bypadd
tags: burp suite, waf, web, pentest
---


## Introducción

Los Firewalls de Aplicación (WAF, por Web Application Firewall), sirven como primera línea de defensa para muchas aplicaciones, filtrando y monitorizando tráfico HTTP, bloqueando ataques antes de que lleguen a la aplicación web.

A fin de evitar consumir excesivos recursos, y no introducir retrasos en el proceso de las peticiones, es habitual que estos firewalls limiten su análisis a una fracción de la petición, normalmente los primeros 8-16Kb. 

## Evasión de contramedidas

Conociendo esta limitación, una opción que podemos tomar es insertar contenido inocuo al inicio del cuerpo de la petición, y desplazar la carga útil o payload malicioso a una zona que no será analizada por el WAF.

Podemos utilizar la pestaña Repeater de Burp, y modificar la petición hasta que veamos que deja de se rechazada por el WAF y comienza a ser procesada por la aplicación, que puede o no ser vulnerable. Esta aproximación es manual y lenta, pero sobre todo no nos permite utilizar el escaneo activo de Burp.

## Extensión: WAF Bypadd

Con esta premisa, desarrollamos una extensión que pueda interceptar las peticiones que pasan por Burp, las modifique sobre la maarcha añadiendo una cantidad de datos configurable al inicio de las mismas. Por ejemplo, la siguiente petición:

![Original](/files/waf_bypadd/unmodified.png)

Se convierte en:

![Modificada](/files/waf_bypadd/modified.png)

<small>Nota: Con el objetivo de que las capturas de pantalla sean legibles, este ejemplo utiliza un entorno de pruebas donde sólo se analizan los primeros 128 bytes de la petición. En condiciones normales habría que determinar de forma manual la cantidad de datos a insertar.</small>

La pestaña de configuración permite indicar qué tipo de peticiones queremos interceptar, así como el tamaño de los datos a insertar en el inicio:

![Configuración](/files/waf_bypadd/config.png)

La aplicación soporta, de momento, 4 tipos de petición, en función de su cabecera Content-Type:
* application/x-www-form-urlencoded
* multipart/form-data
* application/json
* application/xml

En todos los casos, se intenta incrementar el tamaño de la petición sin alterar su contenido legítimo o su integridad.

## Demo con Burp Scanner

Utilizando un script vulnerable a SQLi y un WAF simulado que detecta contenido malicioso en los primeros 128 bytes, probamos el Burp Scanner con y sin la extensión activa.

En condiciones normales, Burp no detecta nada:
![Original](/files/waf_bypadd/scanner1.png)

Tras activar la extensión, los payloads que utiliza Burp llegan a la aplicación vulnerable detrás del WAF:
![Con WAF Bypadd](/files/waf_bypadd/scanner2.png)

![SQLi](/files/waf_bypadd/scanner3.png)


## Descarga e instalación

Vamos a intentar que sea incluida en la tienda de extensiones de Burp Suite pero, de momento, la única opción es descargar la extensión y añadirla manualmente a Burp.

```sh
$ git clone https://github.com/julianjm/waf_bypadd
```

En Burp, vamos a la pestaña Extensions, Installed. Pusamos Add, cambiamos el tipo de extensión a Python e indicamos la ruta al fichero `waf_bypadd.py`

![Instalar](/files/waf_bypadd/addtoburp.png) 

## Contribuir

Hay todavía mucho que mejorar:
* Insertar datos dinámicos que impidan ser detectados fácilmente.
* Función para calcular automáticamente la ventana de análisis del WAF
* Controlar mejor el scope, o qué peticiones son interceptadas.
* Más tipos de peticiones?

Se agradece feedback, pull-requests, etc en el [repositorio en Github](https://github.com/julianjm/waf_bypadd)

## Contacto

* Autor: Julian J. M.
* Email: julianjm@gmail.com
* Github: https://github.com/julianjm
* Twitter: [@julianjm512](https://twitter.com/julianjm512)