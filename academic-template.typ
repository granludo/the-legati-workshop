// Academic template mimicking Latin Modern / LaTeX look
// Using Palatino (closest available) + Menlo for code

#set page(
  paper: "us-letter",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 3cm, right: 3cm),
  numbering: "1",
  number-align: center,
)

#set text(
  font: "Palatino",
  size: 11pt,
  lang: "ca",
)

#set par(
  justify: true,
  leading: 0.65em,
  first-line-indent: 0pt,
  spacing: 0.9em,
)

#set heading(numbering: none)

#show heading.where(level: 1): it => {
  set text(size: 16pt, weight: "bold", font: "Palatino")
  v(0.5em)
  it.body
  v(0.3em)
}

#show heading.where(level: 2): it => {
  set text(size: 13pt, weight: "bold", font: "Palatino")
  v(0.4em)
  it.body
  v(0.2em)
}

#show heading.where(level: 3): it => {
  set text(size: 11pt, weight: "bold", font: "Palatino")
  v(0.3em)
  it.body
  v(0.15em)
}

#show raw.where(block: true): it => {
  set text(font: "Menlo", size: 9pt)
  block(
    fill: luma(245),
    inset: 10pt,
    radius: 2pt,
    width: 100%,
    it,
  )
}

#show raw.where(block: false): it => {
  set text(font: "Menlo", size: 9.5pt)
  it
}

#show quote: it => {
  pad(left: 2em, right: 2em,
    text(style: "italic", it.body)
  )
}

#show table: it => {
  set text(size: 10pt)
  it
}

#set table(
  stroke: 0.5pt + luma(150),
  inset: 6pt,
)
