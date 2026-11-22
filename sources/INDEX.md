# Índice de fuentes

Todo el material de fuentes vive en `sources/`. Las fuentes son entradas en bruto: lo que lees, ves o escuchas y que alimenta lo que piensas y escribes. Son distintas de tus proyectos de escritura, que son salidas.

## Estructura

```
sources/
├── shared/          ← cross-project sources (papers, books, courses, talks)
│   ├── papers-own/  ← your own published papers (for voice reference + citation)
│   ├── papers-external/  ← reference papers
│   ├── video-and-audio/  ← course recordings, talks, podcasts
│   └── blog-and-writings/  ← your blog posts, essays, manifestos
└── [project-slug]/  ← sources scoped to a single project
```

## Cómo añadir una fuente

Usa la skill `/add-source`. Se encarga de:
- **YouTube / vídeo:** extracción de la transcripción → procesamiento → ubicación
- **PDF:** extracción de metadatos → extracción del texto → ubicación
- **Audio:** transcripción con mlx-whisper → procesamiento → ubicación
- **Artículo web:** descarga → limpieza → ubicación
- **Texto / pegado:** ubicación directa

Cada fuente recibe un `README.md` que documenta qué es, de dónde viene y para qué sirve.

## Fuentes indexadas actualmente

*(ninguna todavía: se van acumulando a medida que trabajas)*
