# Navegación con Graphify

Índice estructural del código (`graphify-out/graph.json`). Te dice **qué símbolos
existen y en qué archivo viven** antes de hacer búsquedas a ciegas.

> Requiere el CLI (`npm i -g graphify-ts`) y el runtime **Bun**
> (`curl -fsSL https://bun.sh/install | bash`).

## Primer uso (una vez por máquina)

```bash
npm i -g graphify-ts
graphify build .
```

## Comandos

### Construir / reconstruir el índice
```bash
graphify build .
# → "Indexed {files} files, {nodes} symbols, {edges} relationships"
```

### Buscar símbolos por nombre
```bash
graphify query graphify-out/graph.json <name>
```
Búsqueda sin distinguir mayúsculas; devuelve símbolos con su ubicación
(`archivo:línea`). Ejemplo:

```bash
graphify query graphify-out/graph.json analyze
# → AnalyzeResponse → backend/core/schemas.py:79
# → analyze → backend/api/router.py:148
# → analyzeImage → frontend/src/api/inspect.ts:11
```

### Actualizar tras editar archivos
```bash
graphify update graphify-out/graph.json <file1> [file2...]
# o, refresco masivo desde git diff:
graphify auto-update [dir]
```

> El índice **no se actualiza solo**; corre `update`/`build` cuando quieras
> re-consultarlo en la misma sesión.

## Cuándo usarlo

- **Antes de buscar código:** si `graphify-out/graph.json` existe, consulta
  primero el grafo en lugar de Glob/Grep. El grafo apunta directo al archivo del
  símbolo (valor principal: reemplazar búsqueda por palabra clave con lookup
  estructurado).
- **Después de editar:** si vas a re-consultar en la misma sesión, corre
  `graphify update <archivos-editados>` (o `graphify auto-update`).
- **Explorar código desconocido:** consulta un concepto para hallar puntos de
  entrada sin adivinar nombres de archivo.

## Salida

`graphify-out/graph.json` (se regenera; está en `.gitignore`):
```json
{
  "nodes": [{ "id": "main::app", "label": "App", "sourceFile": "main.py", "sourceLocation": "main.py:5" }],
  "edges": [{ "source": "file::main", "target": "main::app", "relation": "contains", "confidence": "EXTRACTED" }]
}
```

Relaciones de borde: `contains`, `method`, `imports`, `imports_from`,
`calls` (INFERIDA), `inherits`.

## Nota de PATH

Tras instalar Bun, añade `~/.bun/bin` al `PATH` (el instalador lo agrega a
`~/.zshrc`). En shells no interactivos puede necesitarse
`export PATH="$HOME/.bun/bin:$HOME/.npm-global/bin:$PATH"`.