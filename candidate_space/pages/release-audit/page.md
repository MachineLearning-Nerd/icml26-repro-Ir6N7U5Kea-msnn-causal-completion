# Evaluator-blind release audit

The reviewer used only a fresh candidate directory and the evaluator rubric.
No repository state, OpenResearch logs, dashboard paths, experiment
descriptions, or hints about evidence locations were supplied.

## Pass 1

Starting from `README.md`, the reviewer followed `pages/index.md`, every route
in `logbook.json`, and every local Markdown link recursively. It opened 80
files; the exact ordered list is in
[pass-1-opened-files.txt](pass-1-opened-files.txt). Automated traversal found
zero missing files, unknown routes, root escapes, or unreachable claim pages.

The content review located the current fixed verifier and all six claim
contracts. It found one release-readiness gap: several claim pages linked
environment files whose original formal-run provenance was valid but did not
identify the latest evidence-freeze run inline. That made “current” provenance
unnecessarily ambiguous even though the science was present.

## Fix after Pass 1

Claims 1–6 now state the current freeze run ID, full Git SHA, allocation,
container-visible CPU count, seed declaration, component runtime, and
cumulative wall time either inline and in the linked environment or, for the
exact symbolic certificates, explicitly state that no stochastic seed exists.
The current verifier remains above the historical baseline in navigation.

## Pass 2

The candidate was rebuilt from the protected judged revision plus only the
allowlisted text overlay. The recursive traversal was repeated after the
provenance fix and after adding this audit page. The pass again found zero
missing links, unknown routes, or root escapes. For every claim, the reviewer
could locate:

- the exact source statement, assumptions, domain, and quantifiers;
- decisive numerical or symbolic evidence inline;
- executable generator/verifier source;
- fixed command and pinned environment;
- downloadable strict raw JSON;
- independent checker source and output;
- a control that fails for its intended reason;
- limitations, Git SHA, seeds, allocation, and runtime;
- a fail-closed VERIFIED or FALSIFIED verdict.

The complete visibility matrix is on the
[canonical index](../index.md#visibility-matrix). No conclusion remained
unverifiable from the candidate. The old executive summary was opened only to
confirm that it remains byte-identical and is visibly labeled **Historical
rejected baseline** in current navigation; it was not used as evidence.
