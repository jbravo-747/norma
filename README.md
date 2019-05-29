# Norma: La abogada de las víctimas

El repositorio contiene la información técnica relacionada al proyecto "Norma: La abogada de las víctimas".

## Estructura de archivos


* BD: contiene una copia de la base de datos utilizada por OPIT.
* odoo: contiene el código utilizado por el framework Odoo.
* web: contiene el código de la página web pública.

## ODOO
Debes tener una instancia funcionando de odoo para poder instalar esta plataforma.
El contenido de la carpeta odoo debe colocarse en una ubicación visible para el path de Odoo.

Inicia sesión como odoo y en la terminal navega hacia el directorio de este proyecto y corre:
´´´
pip3 install -r ./requerimientos-pip.txt


Lo anterior puede realizarse colocando los archivos en la ubicación que utiliza Odoo por default o enviando un parámetro adicional al archivo que inicializa el servidor.

## WEB

Los archivos deben colocarse en una ubicación donde pueda ser leído y ejecutado por un servidor web tradicional.
