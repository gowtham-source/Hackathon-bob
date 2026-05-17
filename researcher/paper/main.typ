// NeurIPS 2026 Paper - Vanilla Typst Layout
// Compatible with Typst 0.14.2

#set page(
  paper: "us-letter",
  margin: (x: 0.75in, y: 1in),
  numbering: "1",
  footer: context [
    #align(left)[#text(size: 7pt, fill: rgb("#999999"))[#counter(page).display("1")]]
    #place(right + horizon)[
      #text(size: 6.5pt, fill: rgb("#999999"), style: "italic")[
        Rough draft · Entirely AI-generated · Not for submission
      ]
    ]
  ],
)

#set text(
  font: "New Computer Modern",
  size: 10pt,
)

#set par(
  justify: true,
  leading: 0.55em,
)

#set heading(numbering: "1.")

// Title
#align(center)[
  #text(size: 14pt, weight: "bold")[
    MMRL++: Parameter-Efficient Multi-Modal Representation Learning \ via Shared-Residual Alignment
  ]
  
  #v(0.5em)
  
  #text(size: 11pt)[
    Anonymous Authors \
    Anonymous Institution \
    #link("mailto:anonymous@example.com")
  ]
  
  #v(0.5em)
]

// Abstract
#align(center)[
  #block(width: 90%)[
    #text(weight: "bold")[Abstract]
    
    #include "sections/abstract.typ"
  ]
]

#v(1em)

// Main content
#include "sections/introduction.typ"
#include "sections/related_work.typ"
#include "sections/methodology.typ"
#include "sections/experiments.typ"
#include "sections/results.typ"
#include "sections/discussion.typ"
#include "sections/conclusion.typ"

// Broader Impact (required for NeurIPS)
#include "sections/broader_impact.typ"

// References
#pagebreak()
#bibliography("refs.bib", title: "References", style: "ieee")