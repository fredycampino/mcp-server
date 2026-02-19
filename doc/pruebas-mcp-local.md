# Pruebas de herramientas `local-mcp`

Fecha de ejecucion: 2026-02-19

## Alcance

Herramientas probadas:
- `functions.mcp__local-mcp__list_files`
- `functions.mcp__local-mcp__read_file`
- `functions.mcp__local-mcp__create_file`
- `functions.mcp__local-mcp__overwrite_file`
- `functions.mcp__local-mcp__get_url`
- `functions.mcp__local-mcp__internet_research`

## Resultados

| ID | Herramienta | Prueba | Entrada | Resultado esperado | Resultado observado | Estado |
|---|---|---|---|---|---|---|
| T1 | `list_files` | Listado de raiz valida | `{"subpath":"0:"}` | `status=success` y listado | Devuelve `0:emails.txt`, `0:pgadmin.txt` | OK |
| T2 | `list_files` | Subpath inexistente | `{"subpath":"0:no-existe"}` | Error controlado o vacio | Devuelve lista vacia (sin error) | OK |
| T3 | `read_file` | Leer archivo existente | `{"filepath":"0:emails.txt"}` | Contenido y `status=success` | `status=success`, contenido vacio | OK |
| T4 | `read_file` | Leer archivo inexistente | `{"filepath":"0:no_existe_123.txt"}` | Error de no encontrado | `File not found or access denied` | OK |
| T5 | `create_file` | Crear archivo nuevo | `{"filepath":"0:codex_test_local_mcp.txt","content":"linea-1"}` | Archivo creado | `File created successfully` | OK |
| T6 | `create_file` | Crear archivo ya existente | mismo `filepath` de T5 | Error de duplicado | `File already exists` | OK |
| T7 | `overwrite_file` | Sobrescribir existente | `{"filepath":"0:codex_test_local_mcp.txt","content":"linea-2\\nlinea-3"}` | Contenido reemplazado | `File overwritten successfully` y lectura correcta | OK |
| T8 | `overwrite_file` | Sobrescribir inexistente | `{"filepath":"0:no_existe_123.txt","content":"x"}` | Error por no existir | Crea/actualiza archivo sin error | OK (comportamiento actual) |
| T9 | `get_url` | URL valida | `{"url":"https://example.com","max_chars":200}` | Texto plano de pagina | Error SSL: `CERTIFICATE_VERIFY_FAILED` | BLOQUEADO (entorno) |
| T10 | `get_url` | URL invalida | `{"url":"notaurl"}` | Error de validacion | Error: URL sin esquema | OK |
| T11 | `internet_research` | Query valida | `{"query":"Model Context Protocol","num_results":3}` | Resultados relevantes | `results: []` | BLOQUEADO/NO DATA (entorno) |
| T12 | `internet_research` | Query vacia | `{"query":""}` | Error de validacion | Error: `keywords is mandatory` | OK |
| T13 | `internet_research` | Query valida con fetch | `{"query":"OpenAI API docs","num_results":5,"fetch":true}` | Resultados y extractos | `results: []` | BLOQUEADO/NO DATA (entorno) |

## Notas

- En este entorno hay dos roots configurados: `0:/home/fede/develop/checkhere` y `1:/tmp`.
- `overwrite_file` se comporta como "upsert" (sobrescribe si existe y crea si no existe).
- Pruebas de red afectadas por restricciones de certificados/conectividad del entorno.

## Artefactos de prueba creados

- `0:codex_test_local_mcp.txt`
- `0:no_existe_123.txt`
