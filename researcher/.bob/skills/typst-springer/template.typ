#import "@preview/springer-spaniel:0.1.0": article

#show: article.with(
  title: [<TITLE>],
  authors: (
    (name: "<Author 1>", affiliation: "<Institution 1>", email: "<a1@example.com>"),
  ),
  abstract: [
    <ABSTRACT>
  ],
  keywords: ("<keyword1>", "<keyword2>", "<keyword3>"),
  bibliography: bibliography("refs.bib", style: "springer-basic"),
)

#include "sections/introduction.typ"
#include "sections/related_work.typ"
#include "sections/methodology.typ"
#include "sections/experiments.typ"
#include "sections/results.typ"
#include "sections/discussion.typ"
#include "sections/conclusion.typ"
