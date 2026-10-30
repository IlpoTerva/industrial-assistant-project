# Fault code reference

Reference guide for the fault codes logged by the shop-floor MES system
(`mes_faults.csv`). Operators can look up a code to understand the likely
cause, the recommended first action, and how urgently it needs attention.
Every fault is logged against the work center where it occurred (see
`work_center_master.csv`) and the job/operation that was running at the time.
Codes are grouped by category: tooling, mechanical, process, quality,
changeover, material, and safety. The same categories and codes appear in
`fault_code_master.csv`.

## Tooling faults

### E101 — Tool Breakage
**Category:** tooling · **Occurs at:** CNC Turning, CNC Machining Center · **Typical duration:** ~20-30 minutes · **Severity:** high
A cutting tool (insert, drill, endmill, tap) has broken during the cut,
usually detected by a load spike, an audible event, or a bad surface finish.
**Likely cause:** worn tooling run past its limit, wrong feeds/speeds for the
material, a hard spot in the stock, or chip recutting.
**Recommended operator action:** stop the spindle, retract, and clear any
broken tool fragments before restarting — do not resume the cut on top of a
broken insert. Replace the tool, reset the tool offset, and inspect the last
part machined for damage. If breakage recurs on the same operation, flag the
NC program's feeds/speeds to the programmer rather than just swapping tools.

### E110 — Tool Wear / Out of Tolerance
**Category:** tooling · **Occurs at:** CNC Turning, CNC Machining Center · **Typical duration:** ~15-25 minutes · **Severity:** high
Measured features have drifted toward or past the tolerance band because a
tool has worn — this is a quality issue, not only a downtime one.
**Likely cause:** normal wear over a long run, or a tool left in service past
its expected life. Tight-tolerance parts (e.g. the Precision Spindle, Pipe
Flange, Hydraulic Manifold) show this first.
**Recommended operator action:** quarantine parts made since the last good
inspection, index or replace the tool, re-set the offset, and run a
first-article check per `sop_assembly.md` before releasing the batch to full
rate. Record where in the run the drift started so tool-life limits can be
tightened.

## Mechanical faults

### E120 — Spindle Overload
**Category:** mechanical · **Occurs at:** CNC Machining Center · **Typical duration:** ~25-35 minutes · **Severity:** high
The spindle drew more load than allowed and the control faulted out to protect
the motor and bearings.
**Likely cause:** too aggressive a depth/width of cut, a dull tool, or
insufficient chip clearance in a pocket.
**Recommended operator action:** clear the alarm, let the spindle cool if the
control indicates a thermal trip, and inspect the tool and part. Do not simply
override and re-run at the same parameters — reduce the cut or replace the tool
first. Repeated overloads on one program are a programming escalation.

### E130 — Axis Alarm / Crash
**Category:** mechanical · **Occurs at:** CNC Turning, CNC Machining Center · **Typical duration:** ~30-50 minutes · **Severity:** high
A servo/axis alarm fired, often following a collision or an unexpected
position error.
**Likely cause:** a wrong offset or work coordinate, a fixture the tool path
didn't account for, or a rapid move into stock.
**Recommended operator action:** do not clear and re-run blind. Inspect the
machine, tool, and fixture for damage, re-home the axes, and re-verify offsets
and the work coordinate before restarting. A crash always requires a
dimensional check of the affected part and, if severe, a technician to check
axis alignment.

### E160 — Coolant System Fault
**Category:** mechanical · **Occurs at:** CNC Turning, CNC Machining Center · **Typical duration:** ~12-20 minutes · **Severity:** medium
Coolant flow, pressure, or level dropped out of range.
**Likely cause:** low tank level, a clogged filter or nozzle, or a pump fault.
**Recommended operator action:** stop cutting — running dry ruins tools and
finish. Top up or unclog as appropriate; if pressure does not recover, escalate
to maintenance. Note that low coolant also worsens thermal drift on
tight-tolerance work.

### E205 — Laser Optics / Nozzle Fault
**Category:** mechanical · **Occurs at:** Laser Cutting · **Typical duration:** ~22-34 minutes · **Severity:** high
The laser reported degraded cut quality or a nozzle/optics condition — dross,
incomplete cuts, or a beam alignment warning.
**Likely cause:** a dirty or damaged nozzle, spatter on the protective lens, or
focus/alignment drift.
**Recommended operator action:** follow the lockout steps, inspect and clean or
replace the nozzle and protective lens, and run the machine's beam-alignment
check. Verify a test cut before returning to the job. Do not keep cutting
production parts with visible dross.

## Process faults

### E140 — NC Program / CAM Error
**Category:** process · **Occurs at:** any machining center · **Typical duration:** ~18-28 minutes · **Severity:** medium
The loaded NC program faulted, stopped unexpectedly, or produced a feature that
doesn't match the drawing.
**Likely cause:** wrong program revision loaded, a post-processor issue, or a
tool/offset the program assumed but the station doesn't have set.
**Recommended operator action:** stop and confirm the program revision matches
the current job's drawing/work order before continuing. If the program itself
is wrong, escalate to the programmer — do not hand-edit production code at the
machine unless you are authorised to.

### E150 — Fixture / Workholding Error
**Category:** process · **Occurs at:** any machining center · **Typical duration:** ~15-22 minutes · **Severity:** high
A part shifted, wasn't seated, or wasn't clamped correctly in the fixture,
vice, or chuck.
**Likely cause:** chips under the part, insufficient clamping, or the wrong
fixture for the job.
**Recommended operator action:** stop immediately — a loose part is both a
scrap and a safety risk. Clean the fixture, re-seat and re-clamp per the
fixture map in `sop_assembly.md`, and inspect the last part. Confirm the
fixture matches the job before resuming.

## Quality faults

### E210 — Bend Angle Out of Spec
**Category:** quality · **Occurs at:** Press Brake · **Typical duration:** ~12-20 minutes · **Severity:** medium
A bend came out outside the angle or flange-length tolerance.
**Likely cause:** wrong material thickness/grade assumptions, springback not
compensated, or the wrong tooling/backgauge setting.
**Recommended operator action:** quarantine the affected parts, re-check the
material grade and thickness against the job, and adjust the bend program or
tooling. Run and measure a first article before continuing. Persistent
springback issues on one material should be logged for the programmer.

### E305 — Weld Porosity / Defect
**Category:** quality · **Occurs at:** Manual Welding · **Typical duration:** ~18-30 minutes · **Severity:** high
Visual or inspection check found porosity, undercut, or incomplete fusion in a
weld.
**Likely cause:** contaminated or damp material, poor shielding gas coverage
(draughts, wrong flow), or incorrect parameters/technique.
**Recommended operator action:** stop, identify the cause before re-welding —
clean the joint, check gas flow and that the work area isn't draughty, and
confirm parameters. Rework or quarantine affected weldments and record the
defect type. Repeated porosity on a shift may indicate a gas-supply issue to
escalate.

### E310 — Weld Distortion / Rework
**Category:** quality · **Occurs at:** Manual Welding · **Typical duration:** ~24-38 minutes · **Severity:** high
Heat input distorted the part out of tolerance, requiring straightening or
rework.
**Likely cause:** welding sequence not balanced, too much heat input, or
missing tack/fixturing to restrain the part.
**Recommended operator action:** rework per the weld procedure — use the
specified sequence and clamping/jig, and stagger the heat input. For recurring
distortion on a weldment (e.g. the Welded Sub-Frame), flag the fixturing and
sequence to the shift lead rather than straightening every part after the fact.

### E405 — Burr / Surface Finish Reject
**Category:** quality · **Occurs at:** Deburring & Finishing · **Typical duration:** ~8-16 minutes · **Severity:** medium
A part failed the finishing check for remaining burrs, sharp edges, or surface
marks.
**Likely cause:** upstream machining/cutting left heavy burrs, worn deburring
media/tools, or a step skipped under time pressure.
**Recommended operator action:** re-deburr to the edge-break spec on the
drawing. If burrs are consistently heavy, the cause is usually upstream (dull
cutting tool at the mill/lathe or laser cut parameters) — flag it there rather
than absorbing extra finishing time every batch.

### E520 — Dimensional NC at Inspection
**Category:** quality · **Occurs at:** Inspection & QC · **Typical duration:** ~14-24 minutes · **Severity:** high
Final inspection found one or more features non-conforming (out of tolerance).
**Likely cause:** upstream tool wear (E110), a fixture shift (E150), thermal
drift on tight-tolerance work, or an incorrect program.
**Recommended operator action:** quarantine the batch, record which feature and
how far out, and trace it back to the operation that produced it — inspection
is where the problem surfaces, not usually where it was caused. Do not ship or
pass parts on a concession without sign-off. Feed the finding back to the
originating work center so the run can be corrected.

## Changeover faults

### E410 — Changeover / Setup Delay
**Category:** changeover · **Occurs at:** any work center · **Typical duration:** ~30-40 minutes · **Severity:** medium
Setting up for a new job took longer than the standard setup time budgeted for
that operation. In a high-mix low-volume shop this is the single largest source
of lost time, because setups are frequent and batches are small.
**Likely cause:** missing or unstaged fixtures/tooling, an unclear work order,
material not kitted, or a first-time part/operation combination the operator
hasn't run before.
**Recommended operator action:** work the setup checklist in `sop_assembly.md`
in order rather than from memory, and stage the next job's tooling, program,
and material during the current run where possible. Log why the setup ran long
— recurring long setups on one work center are the highest-value target for
improvement.

## Material faults

### E505 — Wrong Material / Grade Loaded
**Category:** material · **Occurs at:** any work center · **Typical duration:** ~10-18 minutes · **Severity:** high
The material staged or loaded doesn't match the grade/spec on the job (e.g.
S355 mild steel where 304 stainless was called for).
**Likely cause:** a picking error at the material store, unlabeled offcuts, or a
mixed bundle.
**Recommended operator action:** stop and quarantine anything already
processed — wrong grade cannot be corrected downstream and is a scrap/traceability
issue. Verify the grade against the job and the material certificate before
resuming, and flag the store so the mispick doesn't reach other jobs.

### E510 — Material / Stock Shortage
**Category:** material · **Occurs at:** any work center · **Typical duration:** ~15-25 minutes · **Severity:** medium
The job ran short of raw material or a required consumable before the batch was
complete.
**Likely cause:** stock not kitted to the full batch quantity, higher-than-expected
scrap eating into the material, or an upstream supply gap.
**Recommended operator action:** flag the line/shift lead — a shortage mid-job
often means the whole job waits for material, which is a common cause of late
delivery. Do not part-build and leave; record the shortage against the job so
the delay is traceable.

## Safety faults

### E601 — Emergency Stop Triggered
**Category:** safety · **Occurs at:** any work center · **Typical duration:** ~8-14 minutes · **Severity:** high
An E-stop button or light curtain/guard interlock was triggered.
**Likely cause:** a person or object entered a guarded zone, or the button was
pressed deliberately in response to an unsafe condition.
**Recommended operator action:** follow the E-stop reset procedure in
`sop_assembly.md` exactly — confirm the cause is cleared and the area is safe
before resetting. Every E-stop event must be logged with a cause, even if work
resumes normally; repeated E-stops at one work center indicate a guarding or
process problem to investigate.