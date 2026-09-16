# Paper G: fan-array acquisition and archive correspondence

PRIVATE / INTERNAL. `public_evidence_eligible: false`.
Started2026-09-10T03:21:21Z. Previous goal turn: progress.

**Decision: not a qualified re-entry trigger.** Source code documents
timestamps, pressure fields and timed command sequences. It does not yet
establish that a given released CSV row is linked to a particular executed
command, sensor packet, calibration record and experimental run. The
bounded follow-up therefore stops the use of this release as ready-made
dynamic intervention truth. It remains a potential static-response resource.
This is a capability decision, not a finding of experimental/model failure.

The repository connection is learned flow responses and constraint
generalization. The closed numerical-teacher route, its two contribution
blockers and the overall unachieved Paper G goal are unchanged. No Paper D
outcome or implementation history is used.

## Fixed source scope

All selected JavaFAWT files are at commit
`07e7a98617715e6f911ae6368fd2669aca68f023`. Five source programs were
downloaded and read only in the relevant interface/schema sections; none
was imported, compiled or executed. One installation document and five
GitHub directory pages were also read. The previous data revision remains
`e9b35064bda6d15ed9a0dd3229fd34612fbd4c94`.

The [installation document](https://github.com/UPNAdrone/JavaFAWT/blob/07e7a98617715e6f911ae6368fd2669aca68f023/documentation/private/docs/installation.md)
describes starting the Java application. It is not a run-level acquisition
protocol. Directory metadata were used only to locate the files below.

| Selected source | Documented interface or transformation | What it does not certify here |
| --- | --- | --- |
| `read_plot.py`, `parse_packet` | Two timestamp words, 32 unsigned sensor channels, channel-to-pressure scaling | Actual archived packet sequence, instrument calibration, command correspondence |
| `PressureSensor.java`, parser and writer | UTC timestamp interpretation; timestamp and pressure lines written to numbered text files | Dataset-row lineage, actual sampling frequency, executed-command acknowledgement |
| `Functionality.java`, `run` | First command-row value used as a millisecond wait after an update call; remaining values fill the command vector | Measured RPM, physical settling, actual execution time or clock synchronization |
| `ControlFrame.java`, selected import/call | Connects the interface to `representation.PressureSensor` | Which program revision generated the public dataset |
| `unified_training.py`, `load_and_prepare_data` | Distance filter, fan/velocity column prefixes, common physical permutation and a random 80/20 split of extracted arrays | Whole-run grouping, dynamic replay or absence of unused metadata in the original CSV |

Exact source links are in the companion manifest. Source definitions are
evidence of intended interface semantics, not proof of historical execution
or validation of hardware behavior.

## The important distinction is archive correspondence

The [loader](https://github.com/UPNAdrone/JavaFAWT/blob/07e7a98617715e6f911ae6368fd2669aca68f023/inverse_control/unified_training.py)
uses `Distancia (cm)`, column names beginning `Ventilador` and `Velocidad`,
and `PERM_24` for both inputs and outputs. Its returned training/test arrays
are static command/velocity pairs. This confirms the documented regression
task. It does not prove that the original CSV has no timestamp or run ID,
nor does it prove train/test leakage. Those questions require a qualified
schema and acquisition lineage, not speculation from a loader's selection.

The [sensor writer](https://github.com/UPNAdrone/JavaFAWT/blob/07e7a98617715e6f911ae6368fd2669aca68f023/software/serverCode/src/main/java/representation/PressureSensor.java)
does retain time information in its defined output. Thus a blanket claim
that the platform has no timestamps would be wrong. A sleep call is not a
measurement of sampling frequency or fan settling. The source cannot alone
certify which raw log, command file, clock offset and conversion version
produced each public CSV row.

The pressure-to-velocity transformation for the released dataset was not
located in the bounded set of inspected files. That is an unqualified
provenance link, not proof that the transformation is absent or incorrect.
The inspected pressure parser does not provide independent velocity
calibration. No formula, zero-offset correction or uncertainty model is
imputed to the released velocity values.

The minimum required correspondence remains:

`run ID -> command sequence/version -> actual execution event -> sensor
packet/time -> calibration/conversion version -> public row ID`.

Only parts of this chain are described by the selected source interfaces.
No public outcome file, CSV header, CSV row, raw pressure log, command tape,
model checkpoint or result archive was accessed. A metadata-only dataset
schema query did not return a usable schema; no conclusion about the data
contents follows from that access result.

## Consequences for the research decision

The supported target remains static downstream sensor-label prediction at
a declared distance. Dynamic causal response, policy value, energy balance,
independent velocity error and replay from matched physical initial states
remain unqualified. Actual velocity and transformed pressure labels are not
independent measurement lineages merely because both file names exist.

For any future dynamic asset, all commands, shared airflow, ambient state,
initial/settled state and sensor windows must be retained. Independent units
should be established from the acquisition protocol before a confirmation
partition is chosen. We do not replace that missing protocol with random
rows or an invented historical assignment. Existing static spatial/mixing
baselines from the source remain direct parents of generic method pitches.

No recorded contribution blocker is removed. There is no new theorem,
counterexample, candidate, search cycle, forecast, machine card or execution
authority. This bounded JavaFAWT dynamic-truth preflight is now closed as
unqualified under current evidence. Do not continue crawling adjacent UI
files, retuning static predictors or converting metadata gaps into a paper.
Revisit only if an actual run-to-row acquisition/calibration manifest or
independent same-target measurement becomes available, or another qualified
asset removes the relevant blocker. That condition concerns this asset;
it does not declare the entire Paper G objective impossible.

## Private provenance and verification

Five read-only source programs, one installation document and five directory
pages are pinned and hashed. Root LICENSE/README wording and dataset-card
rights remain as recorded in the prior preflight; no expanded rights or
execution permission are inferred. Parsing/transport implementation details
are not audited as scientific claims and must not motivate a publication.
No internal bug, access error or development history is used as evidence.

The contract freezes estimands, assignment/interference, lifecycle/replay,
rights/release, untouched confirmation, independent replication, cost and
stop rules. No independent experiment or untouched confirmation exists in
this record. Verification checks source identity and bookkeeping only.
