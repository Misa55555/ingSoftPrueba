REGLAS Y EXPLICACION

EXPLICACION:
1. Unicamente se hace push a la rama main en caso de que una seccion (vista) sea valida por todo el grupo, en caso contrario no podra realizarse un push.
2. La rama "test" sigue el mismo orden que la rama "main" con la diferencia que ahi se probaran los cambios realizados en las demas ramas
3. a partir de la rama "test" se crearan ramas que saldran de esa misma, esas ramas seran para manejar: soluciones,cambios,agregados,eliminar etc con respecto al PRODUCT BACKLOG
4. No subir nada que no corresponda al PRODUCT BACKLOG

   estructura de ejemplo
 1.     main/
 2.       ---test/
 3.          ---/STOCK
 4.            ---/"solucion problema de agregado de stock"

    ES IMPORTANTE ENTENDER QUE UNA VEZ QUE TENGAMOS "solucion problema de agregado de stock" se pushea a STOCK, cuando STOCK se encuentre listo y no necesite mas cambios, se manda a TEST
    Luego de confirmar que en TEST anda correctamente se pasara a "MAIN" (si el grupo lo considera)


REGLAS:
1. No agregar codigo que no corresponda a los backlog
2. usar la misma sintaxis en todo el codigo
3. usar atributos,clases,nombres en general que se entiendan para el que vaya a leer
4. intentar documentar todo lo posible
5. Los push de ramas no se debe de hacer, lo que deberian de hacer es: CREAR UNA RAMA en la VISTA que quieren modificar y apartir de ahi trabajar de forma local, una vez terminado
   el cambio lo mandan a la rama (vista que modificaron) y ahi realizan un push de los cambios (REPITO, no hacer PUSH DE RAMAS)



GRACIAS 
