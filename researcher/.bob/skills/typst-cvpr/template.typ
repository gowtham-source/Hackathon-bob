#import "@preview/blind-cvpr:0.1.0": cvpr, paper-id

#show: cvpr.with(
  title: [<TITLE>],
  paper-id: "0000",
  authors: (
    (name: "Anonymous", affl: "Anonymous Institution"),
  ),
  abstract: [
    <ABSTRACT>
  ],
  bibliography: bibliography("refs.bib", style: "ieee"),
  anonymous: true,
)

#include "sections/introduction.typ"
#include "sections/related_work.typ"
#include "sections/methodology.typ"
#include "sections/experiments.typ"
#include "sections/results.typ"
#include "sections/discussion.typ"
#include "sections/conclusion.typ"
