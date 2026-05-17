#import "@preview/bloated-neurips:0.5.0": neurips, paragraph, bibliography

#show: neurips.with(
  title: [<TITLE>],
  authors: (
    (name: "<Author 1>", affl: "<Affiliation 1>", email: "<a1@example.com>"),
    (name: "<Author 2>", affl: "<Affiliation 2>", email: "<a2@example.com>"),
  ),
  keywords: ("<keyword1>", "<keyword2>", "<keyword3>"),
  abstract: [
    <ABSTRACT — replace with content from paper/sections/abstract.typ once written>
  ],
  bibliography: bibliography("refs.bib"),
  accepted: false,
)

#include "sections/introduction.typ"
#include "sections/related_work.typ"
#include "sections/methodology.typ"
#include "sections/experiments.typ"
#include "sections/results.typ"
#include "sections/discussion.typ"
#include "sections/conclusion.typ"
#include "sections/broader_impact.typ"
