
# Description

> Help me overcome my fear of... baths? No that ain't right...

----

# 1. Overview 

El servicio implementa:

- Un cifrado Feistel custom de 96 bits
    
- Un key schedule basado en LCG
    
- Un cifrado AES-ECB que protege la flag
    
- Un oracle de cifrado accesible al usuario
    

El objetivo es recuperar la flag cifrada en AES explotando debilidades en el diseño criptográfico del sistema.

---

# 2. Análisis del Código

## 📌 2.1 Generación de Clave

![[Pasted image 20260303211213.png]]

La clave principal:

- Tamaño: **96 bits**
- Se usa para:
    - El cifrado Feistel
    - Derivar la clave AES
        
> ⚠ Problema: **reutilización de clave entre primitivas criptográficas**

---

## 📌 2.2 Derivación de la Clave AES

![[Pasted image 20260303211318.png]]

Aquí ocurre algo crítico:

![[Pasted image 20260303211350.png]]

Esto produce:

```
AES_key = key || key[:4]
```

Es decir:

- La clave AES depende directamente del `key` del Feistel.
- Si recuperamos el `key` del Feistel → recuperamos la clave AES.
    
> ⚠ **Impacto directo:** romper Feistel rompe AES.

---

# 3. Oracle de Cifrado

El servicio permite cifrar mensajes arbitrarios:

![[Pasted image 20260303211516.png]]

Esto convierte al servicio en un:

>  **Chosen-Plaintext Oracle**

Podemos enviar cualquier mensaje y observar su cifrado.

---

# 4. Análisis del Feistel

## 📌 4.1 Estructura

![[Pasted image 20260303211737.png]]

Parámetros:

- Block size: 96 bits
- Half size: 48 bits
- Rounds: 11

Cada ronda usa:
```
F(ri ⊕ round_key_i)
```

---

## 📌 4.2 Key Schedule (LCG Débil)

![[Pasted image 20260303211807.png]]

LCG definido como:

![[Pasted image 20260303211846.png]]

Donde:

- `a = key[0]`
- `c = 1`
- `x0 = key[1]`
- `m = 2^48 - 1`
    

⚠ **PROBLEMAS CRÍTICOS:**

1. Módulo potencia de 2
2. Incremento fijo c = 1
3. LCG no criptográficamente seguro
4. Parámetros directamente derivados de la clave
    
Esto hace el key schedule:
- Lineal
- Predecible
- Recuperable

---

# 5. Vulnerabilidades Identificadas

## 🔥 Vulnerabilidad #1 — Reutilización de Clave

La clave Feistel y la clave AES están relacionadas.

Impacto:

```
Recuperar key → Recuperar AES key → Desencriptar flag
```

---

## 🔥 Vulnerabilidad #2 — LCG como Key Schedule

Los LCG con módulo $2ⁿ$ tienen propiedades explotables:

- Los bits menos significativos siguen patrones deterministas
- Es posible reconstruir parámetros con suficientes salidas
- Son lineales
    
No es adecuado para criptografía.

---

## 🔥 Vulnerabilidad #3 — Oracle de Cifrado

El usuario puede:

- Elegir plaintext arbitrario
- Obtener ciphertext correspondiente
    
Esto permite:

- Ataques diferenciales
- Análisis estadístico
- Reconstrucción de round keys
---

## 🔥 Vulnerabilidad #4 — AES en modo ECB

![[Pasted image 20260303213916.png]]

ECB:
- No tiene IV
- Es determinista
- No proporciona seguridad semántica
    
Aunque aquí el problema principal es la clave.

---

# 6.  Explotación

## 🐱‍💻 Paso 1 — Usar el Oracle

Enviar bloques controlados:

- $L = 0$, $R = 0$
- Variaciones bit a bit
- Diferencias controladas

Observar:
$C1 ⊕ C2$
para deducir información interna.

---

## 🐱‍💻 Paso 2 — Recuperar Round Keys

Cada ronda usa:

$ri ⊕ x_i$

Donde:

$x_{n+1} = a·x_n + 1 (\text{mod} 2^48)$

Con suficientes observaciones:

- Se pueden recuperar los valores $x_i$
- Luego resolver el sistema lineal para obtener:
    - `a`
    - `x0`
---

## 🐱‍💻 Paso 3 — Reconstruir la Clave

Recordemos:

![[Pasted image 20260303213404.png]]

La clave original se divide en dos mitades de 48 bits:

```
key = key0 || key1
```
Y:
* `a = key0 `
* `x0 = key1`

Recuperando `a` y `x0` → reconstruimos `key`.

---

## 🐱‍💻 Paso 4 — Derivar Clave AES

![[Pasted image 20260303213943.png]]

---

## 🐱‍💻 Paso 5 — Desencriptar Flag

```
cipher = AES.new(aes_key, AES.MODE_ECB)  
flag = cipher.decrypt(base64_decoded_flag)
```

Y remover `padding PKCS#7`.

---

# 7. Ataque

El sistema falla por:

- Uso de PRNG lineal
- Reutilización de clave
- Exposición de oracle
- Diseño criptográfico casero
    

En criptografía:

> No basta con que algo “parezca” complejo.  
> Debe ser matemáticamente resistente.

Aquí el diseño es estructuralmente débil.

---

# 8. Mitigaciones

Para evitar este ataque:

1. ❌ No usar LCG como key schedule
2. ❌ No reutilizar clave entre primitivas
3. ❌ No exponer oracle sin autenticación
4. ❌ No usar ECB
5. ✔ Usar KDF segura (HKDF)
6. ✔ Usar AES-GCM o ChaCha20-Poly1305
---

# 9 Matemática del Ataque 

En esta sección vamos a describir **formalmente y matemáticamente** cómo aprovechar la debilidad del key–schedule basado en LCG para recuperar la clave.

---

## 🧮 9.1 Definición del LCG utilizado

El generador congruencial lineal (LCG, Linear Congruential Generator) está definido por:

$xn+1=(a⋅xn+c)  mx_{n+1} = (a \cdot x_n + c) \bmod mxn+1​=(a⋅xn​+c)modm$

En el código el LCG se crea así:

![[Pasted image 20260303215532.png]]

- $a = \text{key}_0$
- $c=1$
- $x_0 = \text{key}_1​$
- $m = 2^{48} - 1$
    
Es decir,

$x_{n+1} = (a\cdot x_n + 1) \bmod 2^{48}$

---

## 🔍 9.2 Propiedad lineal fundamental

Un LCG con módulo potencia de $2$ y $c=1$ tiene una forma **totalmente determinística** que puede ser invertida o reconstruida con suficientes salidas.

Si observas dos salidas consecutivas:

$x_{n+1} = a \cdot x_n + 1$
$x_{n+2} = a \cdot x_{n+1} + 1$

Sustituyendo la primera en la segunda:

$x_{n+2} = a^2 \cdot x_n + a + 1$

Conociendo suficientes (tres o más) valores del LCG puedes montar un sistema de ecuaciones sobre módulos $2^{48}$.

---

## 🧠 9.3 Recuperación de parámetros del LCG

### 📌 Objetivo

Usando $x_{n}$, $x_{n+1}​$ y $x_{n+2}$​, resolvemos para obtener $a$ y $x_0$​:

De la definición:

$x_{n+1} - 1 = a\cdot x_n \Rightarrow x_{n+1} - x_{n} \equiv a\cdot x_n - x_n$

También:

$x_{n+2} - 1 = a\cdot x_{n+1}$

Multiplicando y despejando:

$(x_{n+2}-1) - a\cdot(x_{n+1}-1) = 1$

Esto nos da el siguiente sistema:

$x_{n+1} = a\cdot x_n + 1$
$x_{n+2} = a\cdot x_{n+1} + 1$

Restando:

$x_{n+2​}−x_{n+1}​ = a \cdot (x_{n+1} ​− x_{n}​)$


Donde $(x)^{-1}$  es la inversa multiplicativa módulo $2^{48}$.

---

## 📐 9.4 Generación de ecuaciones para resolver `a`

La clave está en obtener la secuencia de valores del LCG a partir del oracle Feistel:

Cada ronda usa el output de LCG mas un half-block:

$F_i = \text{roundFunction}(R_i \oplus x_i)$

Dado que Feistel es reversible en análisis diferencial, usando distintos mensajes con todos los bits fijos excepto uno, puedes aislar:

$F(R_i \oplus x_i) \rightarrow x_i​$

Esto es un proceso de **recuperación bit-a-bit**.

---

## 📈 9.5 Variables clave del sistema

Denotemos:

- $k=$ clave Feistel de 96 bits → bloque dividido en $(k_0,k_1)$
    
- $k_0 = a$, $k_1 = x_0$
    

Una vez que recuperamos algunos valores xix_ixi​ secuenciales, podemos resolver:

$a \equiv \frac{x_{n+2} - x_{n+1}}{x_{n+1} - x_n} \mod 2^{48}$

Y luego:

$x_0 = \text{inversa LCG de } x_n​$

---

## 🧩 9.6 Contra el cifrado Feistel lineal

Una red Feistel tiene la propiedad:

$L_{i+1}​=R_i$​ 
$R_{i+1} = L_i \oplus F(R_i \oplus x_i)$

Dado que cada $L_i$,$R_i$​ son controlables desde el oracle, y el round function $F$ es conocida (S-box con rotación), uno puede escribir:

$C_i = \text{cipher}(P_i,k)$

y con suficientes $i$, montar un sistema de ecuaciones que relaciona plaintexts a la próxima ronda, permitiendo reconstrucción iterativa de $x_i$.

---

## 📌 9.7 Ecuaciones finales para recuperación

Después de obtener suficiente número de pares (plaintext → ciphertext), puedes construir tres ecuaciones discretas:

$(x_1,x_2,x_3) \Rightarrow a$

Seguido de:

$k_1 = x_0$ y $k_0 = a$

Con esto reconstruimos la **llave completa de 96 bits**.

---

## 🧪 9.8 Relación matemática con AES

Una vez recuperados $k_0$ y $k_1$​:

![[Pasted image 20260303221733.png]]

Matemáticamente:

$\text{AES\_key} = k_0||k_1||(k_0\_bits[:4\;bytes])$

Esto significa que recuperar la clave de 96 bits da automáticamente la clave de 128 bits de AES.
# 10. Conclusión

El reto demuestra cómo:

- Un PRNG débil
- Una mala derivación de clave
- Un oracle accesible
    
pueden comprometer completamente un sistema criptográfico.

> Recuperando el estado del LCG fue posible reconstruir la clave Feistel, derivar la clave AES y finalmente descifrar la flag.

