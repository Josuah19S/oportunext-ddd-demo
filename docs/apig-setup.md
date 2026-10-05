# Configuración de ECS y Huawei Cloud APIG

Guía para desplegar los dos microservicios en una ECS y publicarlos a través de Huawei Cloud API Gateway (APIG). Estos pasos los ejecuta una persona desde la consola de Huawei Cloud; no están automatizados.

Placeholders usados en esta guía (reemplázalos por tus valores reales):

| Placeholder | Significado |
|---|---|
| `<ECS_EIP>` | IP elástica pública de la ECS |
| `<APIG-GROUP-DOMAIN>` | Dominio del API Group (dominio de depuración o propio) |
| `<APPCODE>` | AppCode generado en APIG |

---

## 1. ECS: levantar los backends

1. Instala Docker (con el plugin `docker compose`) en la ECS.
2. Copia el repositorio a la ECS (por ejemplo con `git clone` o `scp`).
3. Desde la raíz del repositorio:

   ```bash
   docker compose -f docker/docker-compose.yml up -d --build
   ```

4. En el **Security Group** de la ECS, abre los puertos TCP **8001** y **8002**.
   - Demo: origen `0.0.0.0/0`.
   - Ideal: solo las IPs de salida del gateway.
5. Prueba desde tu máquina:

   ```bash
   curl http://<ECS_EIP>:8001/volunteering
   curl http://<ECS_EIP>:8002/scholarships
   ```

   Cada llamada debe devolver un arreglo JSON de 4 elementos.

## 2. APIG: API Group y las 4 APIs

1. Crea un **API Group**.
2. Registra **4 APIs** con método `GET`, tipo de backend **HTTP** y **sin canal VPC**:

   | API pública | Backend |
   |---|---|
   | `/volunteering` | `http://<ECS_EIP>:8001/volunteering` |
   | `/volunteering/{id}` | `http://<ECS_EIP>:8001/volunteering/{id}` |
   | `/scholarships` | `http://<ECS_EIP>:8002/scholarships` |
   | `/scholarships/{id}` | `http://<ECS_EIP>:8002/scholarships/{id}` |

   En las rutas con `{id}`, define `id` como parámetro de ruta (Path) y mapea el mismo parámetro al backend.
3. Publica las 4 APIs en el entorno **RELEASE**.

## 3. Característica 1: autenticación con AppCode

1. En cada API, configura la seguridad como **App** con autenticación por **AppCode**.
2. Crea una **App**, genera su **AppCode** y autoriza la App en las 4 APIs.
3. Los clientes envían la cabecera:

   ```
   X-Apig-AppCode: <APPCODE>
   ```

## 4. Característica 2: throttling

1. Crea una **política de límite de tráfico** (request throttling). Valor de demo: **5 llamadas por minuto por API**.
2. Vincúlala a las 4 APIs.
3. Ten en cuenta que cada clic en **Recargar** del frontend consume 1 llamada por lista (2 en total, una en cada API de listado).

## 5. Característica 3: CORS

1. Crea un **plugin CORS** y vincúlalo a las APIs.
   - Orígenes permitidos: el dominio de Vercel (por ejemplo `https://<tu-proyecto>.vercel.app`) y `http://localhost:5500`. En la demo puede usarse `*`.
   - Métodos permitidos: `GET, OPTIONS`.
   - Cabeceras permitidas: `X-Apig-AppCode, Content-Type`.
2. Como el frontend envía una cabecera personalizada (`X-Apig-AppCode`), el navegador hace una petición **preflight** `OPTIONS`. Crea las APIs `OPTIONS` necesarias (las mismas rutas) con autenticación **None** y vincúlales también el plugin CORS.
3. **Verifica estos pasos en la documentación oficial de Huawei APIG**: las opciones de CORS cambian según el tipo de gateway (compartido o dedicado) y la versión.

Los backends no agregan cabeceras CORS a propósito: así se evitan cabeceras duplicadas.

## 6. Pruebas con curl

```bash
# Sin AppCode -> 401
curl -i https://<APIG-GROUP-DOMAIN>/volunteering

# Con AppCode -> 200
curl -i -H "X-Apig-AppCode: <APPCODE>" https://<APIG-GROUP-DOMAIN>/volunteering
curl -i -H "X-Apig-AppCode: <APPCODE>" https://<APIG-GROUP-DOMAIN>/scholarships/1

# Superar el límite -> 429 (6 llamadas seguidas con un límite de 5/min)
for i in 1 2 3 4 5 6; do
  curl -s -o /dev/null -w "%{http_code}\n" -H "X-Apig-AppCode: <APPCODE>" https://<APIG-GROUP-DOMAIN>/scholarships
done
```

## 7. Notas

- El gateway compartido tiene un **límite diario de llamadas** en su dominio de depuración.
- El tramo APIG → ECS va por **HTTP sin cifrar**. Es aceptable para la demo; en producción usa un canal VPC y HTTPS.
- El AppCode queda visible en el frontend (`frontend/config.js`). Esto es **solo para la demo**.
