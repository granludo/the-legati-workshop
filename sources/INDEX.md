# Índex de fonts

Tot el material de fonts viu a `sources/`. Les fonts són entrades en brut: coses que llegeixes, mires o escoltes i que alimenten el teu pensament i la teva escriptura. Són diferents dels teus projectes d'escriptura, que en són les sortides.

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

## Com afegir una font

Fes servir la skill `/add-source`. S'encarrega de:
- **YouTube / vídeo:** extracció de la transcripció → processament → col·locació
- **PDF:** extracció de metadades → extracció del text → col·locació
- **Àudio:** transcripció amb mlx-whisper → processament → col·locació
- **Article web:** descàrrega → neteja → col·locació
- **Text / enganxat:** col·locació directa

Cada font té un `README.md` que documenta què és, d'on ve i per a què serveix.

## Fonts indexades actualment

*(encara cap: s'aniran acumulant a mesura que treballis)*
