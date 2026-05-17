#import "@preview/charged-ieee:0.1.3": ieee

#show: ieee.with(
  title: [<TITLE>],
  abstract: [
    <ABSTRACT>
  ],
  authors: (
    (
      name: "<Author 1>",
      department: [<Department>],
      organization: [<Institution>],
      location: [<City>, <Country>],
      email: "<email>",
    ),
  ),
  index-terms: ("<term1>", "<term2>", "<term3>"),
  bibliography: bibliography("refs.bib"),
  paper-type: "conference",
)

#include "sections/introduction.typ"
#include "sections/related_work.typ"
#include "sections/methodology.typ"
#include "sections/experiments.typ"
#include "sections/results.typ"
#include "sections/discussion.typ"
#include "sections/conclusion.typ"
