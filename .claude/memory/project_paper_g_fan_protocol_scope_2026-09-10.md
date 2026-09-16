# Paper G fan acquisition protocol — 2026-09-10

PRIVATE / INTERNAL. `public_evidence_eligible: false`.

- Decision:not_trigger; dynamic-truth preflight stopped as unqualified.
  Overall goal remains unachieved. Previous turn:progress. No new candidate,
  cycle, forecast, theorem, card or execution authority.
- Formal:`papers/proposal/ecomd_paper_g_fan_protocol_scope_2026-09-10.md`.
  Contract:`research/paper_g/fan_protocol_scope_20260910.yaml`.
  Manifest:`research/paper_g/fan_protocol_source_manifest_20260910.json`.
- Same repo commit07e7a98617715e6f911ae6368fd2669aca68f023. Five program
  files read for schema/interfaces only; no import/compile/execution.
  One installation document and five directory pages also cached.
- Pressure parsers define sensor timestamps and32pressure channels. Java
  writer defines timestamp/pressure lines in numbered text files. Do not
  claim no timestamps. Source syntax is not historical acquisition proof.
- Functionality.java reads command-row duration in milliseconds, updates
  the command vector then waits. Duration is not measured execution time,
  settling or hardware RPM; thread sleep is not measured sampling rate.
- Loader filters Distancia(cm), extracts Ventilador/Velocidad prefixes,
  applies common PERM_24 and random80/20 split to static arrays. This does
  not prove original CSV lacks timing/run fields or contains leakage.
- Run→command→execution→packet→calibration/conversion→CSV row chain remains
  incomplete. Released velocity conversion specification not located in
  bounded selected files; not proved absent/incorrect. No independent
  velocity calibration or dynamic replay qualified.
- STOP adjacent UI/code crawling for this dynamic-truth lead. Retain static
  response possibility only. Revisit with an actual acquisition/calibration
  manifest or independent same-target measurement, not another generic
  mixing/sensor-bias method. No new diagnostics added.
- Four source records,seven locators,one audit:
  graph293/274/1436,evidence991,triggers139/qualified0;
  search21cycles/133raw/0cards unchanged. No Paper D outcomes used.
- Eleven source/docs/metadata caches; five scientific source files read,
  zero executed. CSV headers/rows,pressure logs,command tapes,models and
  outcomes untouched. No hardware,GPU,outreach or publication. Receipt:
  `logs/private/paper_g_fan_protocol_20260910_verification.md`.
