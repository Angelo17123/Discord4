---
name: mcp-workflow
description: Metodología completa de desarrollo con MCP (Context7 + Fetch + Sentry). Incluye workflow de 12 pasos para Specification-Driven Development.
version: 1.0.0
author: Angelo
tags: [mcp, context7, fetch, sentry, workflow, methodology]
---

# MCP Workflow — Metodología de Desarrollo con Model Context Protocol

## Resumen

Este skill proporciona un framework completo para desarrollo de software usando los 3 servidores MCP: **Context7** (documentación), **Fetch** (contenido web), y **Sentry** (monitoreo de errores).

## Arquitectura MCP

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Context7   │     │   Fetch     │     │   Sentry    │
│  (Docs API) │     │  (Web API)  │     │ (Error API) │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                    │
       ▼                   ▼                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Documentatión│     │  Referencias│     │ Monitoreo   │
│ actualizada │     │   externas  │     │ producción  │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Las 4 Fases del Desarrollo

### FASE 1: FUNDACIÓN (Pasos 1-4)

**Objetivo**: Crear documentos de gobernanza y configurar agentes.

#### Paso 1: Blueprint del Proyecto
- Nombre, stack, versión
- Runtime, base de datos, hosting
- Arquitectura, patrón de estado, API
- Principios no negociables

#### Paso 2: Constitución del Código
- Linter: ESLint con config strict
- Formatter: Prettier (printWidth: 80, singleQuote: true)
- Tipos: TypeScript strict mode obligatorio
- Cobertura mínima: 80%
- Convenciones de commits

#### Paso 3: Configurar Agentes Especializados
- **Arquitecto**: Diseño de sistema (Context7 + Fetch)
- **Desarrollador**: Implementación (Context7 + Sentry)
- **QA**: Testing y verificación (Sentry + Fetch)
- **DevOps**: CI/CD y monitoreo (Sentry + Fetch)

#### Paso 4: Inicializar Proyecto con MCP
```bash
# Configurar Context7
npx ctx7 setup --cursor

# Verificar Fetch
npx @modelcontextprotocol/inspector uvx mcp-server-fetch

# Configurar Sentry
npx add-mcp https://mcp.sentry.dev/mcp
```

### FASE 2: ESPECIFICACIÓN (Pasos 5-8)

**Objetivo**: Definir QUÉ construir.

#### Paso 5: Especificaciones de Features
- Problema, solución propuesta
- Historias de usuario (COMO rol QUIERO acción PARA beneficio)
- Criterios de aceptación checklist
- Fuera de alcance

#### Paso 6: Plan Técnico
- Componentes afectados y nuevos
- Dependencias con versiones
- Contratos de API
- Modelo de datos

#### Paso 7: Tareas Atómicas
- Cada tarea: pequeña, asignable, testeable, rastreable
- Trazabilidad: SPEC > PLAN > TASK

#### Paso 8: Análisis Adversarial
- Casos edge
- Vulnerabilidades potenciales
- Brechas en especificación
- Acciones correctivas

### FASE 3: IMPLEMENTACIÓN (Pasos 9-11)

**Objetivo**: Ejecutar con puertas de calidad.

#### Paso 9: Checkpoint Humano (OBLIGATORIO)
Revisar antes de código:
- [ ] Blueprint del proyecto
- [ ] Constitución completa
- [ ] Especificaciones cubren requisitos
- [ ] Plan técnico coherente
- [ ] Tareas atómicas y rastreables
- [ ] Análisis adversarial integrado
- [ ] Configuración Sentry activa
- [ ] Context7 docs correctas

#### Paso 10: Descomposición Atómica de Tareas
Instrucciones ultra-específicas para cada tarea:
1. Archivo exacto a crear/modificar
2. Imports necesarios
3. Funciones a exportar
4. Lógica paso a paso
5. Manejo de errores
6. Verificación (lint, typecheck, tests)

#### Paso 11: Implementación Orquestada

**Flujo de implementación**:
```
1. CONSULTAR DOCS
   → context7_resolve-library-id
   → context7_query-docs

2. INVESTIGAR PATRONES
   → fetch_fetch_markdown
   → fetch_fetch_readable

3. VERIFICAR ERRORES EXISTENTES
   → sentry_find_projects
   → sentry_search_issues

4. IMPLEMENTAR CÓDIGO
   → Escribir código basado en docs reales

5. INSTRUMENTAR MONITOREO
   → Sentry.captureException()
   → Sentry.setContext()

6. TESTING
   → Escribir tests
   → Verificar cobertura

7. CODE REVIEW
   → Revisar guías
   → Verificar 0 errores nuevos en Sentry
```

### FASE 4: VERIFICACIÓN (Paso 12)

**Objetivo**: Validar que todo funciona.

#### Checklist Final
- [ ] ESLint sin warnings
- [ ] TypeScript strict sin errores
- [ ] npm audit sin vulnerabilidades
- [ ] Prettier formateado
- [ ] Tests unitarios ≥ 80% cobertura
- [ ] Tests integración cubriendo endpoints
- [ ] Inputs sanitizados
- [ ] No secrets en código
- [ ] CORS y rate limiting configurados
- [ ] Sentry SDK inicializado
- [ ] Errores de prueba en dashboard
- [ ] Source maps subidos

## Herramientas MCP — Referencia Rápida

### Context7
| Herramienta | Función |
|-------------|---------|
| `context7_resolve-library-id` | Resolver nombre de librería a ID |
| `context7_query-docs` | Obtener documentación actualizada |

### Fetch
| Herramienta | Función |
|-------------|---------|
| `fetch_fetch_markdown` | Convertir URL a Markdown |
| `fetch_fetch_readable` | Extraer contenido principal |
| `fetch_fetch_html` | Obtener HTML modificado |

### Sentry
| Herramienta | Función |
|-------------|---------|
| `sentry_find_organizations` | Listar organizaciones |
| `sentry_find_projects` | Listar proyectos |
| `sentry_search_issues` | Buscar issues agrupados |
| `sentry_search_events` | Buscar eventos individuales |
| `sentry_analyze_issue_with_seer` | Análisis de IA |
| `sentry_update_issue` | Actualizar status/asignación |
| `sentry_create_project` | Crear proyecto con DSN |

## Prompts de Ejemplo

### Consultar documentación
```
Usa Context7 para obtener la documentación actual de [librería] para [tarea específica]
```

### Investigar patrones externos
```
Usa Fetch para leer [URL de mejor práctica] y aplica las recomendaciones
```

### Verificar errores existentes
```
Revisa en Sentry si hay errores previos relacionados con [funcionalidad] y propón soluciones
```

### Análisis de error
```
Usa Seer para analizar el issue [URL] y genera un fix recomendado
```

## Mejores Prácticas

1. **Siempre consulta Context7 ANTES de implementar** — Nunca confíes en conocimiento desactualizado
2. **Usa Fetch para validar contra fuentes oficiales** — OWASP, MDN, docs oficiales
3. **Instrumenta con Sentry DESDE el primer commit** — No lo dejes para después
4. **Checkpoint humano es OBLIGATORIO** — La IA propone, el humano dispone
5. **Tareas atómicas = calidad** — Si una tarea toma > 2 horas, divídela
6. **Cada línea rastreable** — De tarea → plan → especificación
7. **Análisis adversarial salva proyectos** — Piensa en lo que puede fallar ANTES de que falle

## Notas de Configuración

El usuario tiene configurado:
- **Context7**: Remote con API key
- **Fetch**: npx mcp-fetch-server
- **Sentry**: Remote con OAuth

Verificar que estén activos antes de usar las herramientas.
