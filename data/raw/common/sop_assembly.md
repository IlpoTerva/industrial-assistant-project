# Standard operating procedures — shop floor

Covers the recurring procedures operators run across the shop's work centers
(`work_center_master.csv`): the machining centers — Laser Cutting, Press Brake,
CNC Turning, CNC Machining Center — and the manual centers — Manual Welding,
Deburring & Finishing, Assembly, and Inspection & QC. These procedures exist so
that setup and downtime are handled consistently regardless of which operator or
shift is running a job. Work is organised as jobs (work orders) that route
through a sequence of operations; each operation has a budgeted setup time and a
per-unit run time (`part_routing.csv`).

## Start-of-shift checklist

1. Confirm the jobs queued for the shift against the work orders — part number,
   operation, batch quantity, and due date — and that the correct program /
   drawing revision is available for each.
2. Visually inspect the work center: guards and interlocks intact, work area
   clear, no damaged tooling or fixtures left from the previous shift.
3. For machining centers, confirm coolant level and check that the required
   tools are present and within their tool-life limits before starting.
4. Confirm raw material for the shift's jobs is kitted to the full batch
   quantity and matches the grade on the work order and material certificate.
5. Log the shift start and any open issues carried over on the shift board.

## End-of-shift handover

1. Record good units, scrap units, and any open faults not resolved during the
   shift for each job worked.
2. Leave a written note for the next shift on any recurring or unresolved issue
   (e.g. "CNC mill: E110 tool wear appearing on the gear-housing run after
   ~40 parts, offset reset once, watch dimensions").
3. Do not leave a work center mid-setup — either complete the setup or clearly
   flag it as in-progress, with the reason, for the incoming shift.

## Job setup / changeover procedure

Because the shop is high-mix and low-volume, setups are frequent and are the
largest single source of lost time. Standard setup times are budgeted per
operation; typical ranges are laser ~15-20 min, press brake ~20-25 min, CNC
turning ~20-40 min, CNC milling ~30-75 min (more for tight-tolerance parts),
and manual welding ~30-45 min. Exceeding the budgeted time logs an E410
(Changeover / Setup Delay).

1. Complete the current job's operation and clear the work center of the
   previous part and its offcuts/chips.
2. Swap fixtures, tooling, and (for cutting) the material per the fixture/tool
   map for the job. Stage the next job's fixtures and material during the
   current run where possible — this is the most effective way to cut setup
   time.
3. Load the correct program / recipe and confirm the revision matches the work
   order and drawing. Loading the wrong revision is a common cause of E140.
4. Set and verify tool offsets and the work coordinate before the first cut
   (machining), or confirm bend program and backgauge (press brake), or confirm
   weld parameters and jig (welding).
5. Run and inspect a first article before releasing the batch to full rate (see
   below). Skipping this is the leading cause of scrap that surfaces later as
   E520 (Dimensional NC at Inspection).
6. Log the setup start/end time.

## Tool setting & first-article inspection (FAI)

1. Set tool offsets / bend or weld parameters using the certified gauges or
   probing routine for the operation; do not manually override a failed probing
   result.
2. Machine or fabricate the first article, then inspect its critical features
   against the drawing before running the rest of the batch.
3. If the first article is out of tolerance, correct the offset/parameter and
   re-inspect — do not run the batch on a hope. If it fails twice, pull the
   operation and escalate rather than continuing on an uncorrected setup. (This
   is the correct response to E110 Tool Wear / Out of Tolerance surfacing at
   setup.)
4. On long runs of tight-tolerance parts, re-check a part periodically through
   the batch — tool wear and thermal drift move dimensions gradually, and the
   goal is to catch drift before it becomes scrap.
5. Record the first-article result and timestamp against the job.

## Emergency stop (E-stop) reset procedure

Applies to any E601 fault.

1. Do not reset the E-stop until the triggering cause is identified and the area
   is confirmed clear and safe.
2. If the cause was a person or object crossing a light curtain or opening a
   guard, confirm no one is inside the guarded zone before resetting.
3. If the cause is unclear, do not reset — call the shift lead before resuming.
4. Reset at the panel, confirm the machine re-homes correctly, and run one test
   cycle before returning to production.
5. Log the E-stop event with cause, even if work resumed normally — repeated
   E-stops at one work center across shifts indicate a guarding or process issue
   that needs investigation, not just a one-off reset.

## Escalation guidance

- **Tooling / mechanical faults (E101, E110, E120, E130, E160, E205)
  unresolved after 2 attempts:** escalate to maintenance; for repeat faults on
  the same program, escalate to the programmer.
- **Process faults (E140, E150):** confirm program revision and workholding
  before resuming; do not hand-edit production programs unless authorised.
- **Quality faults (E210, E305, E310, E405, E520):** quarantine affected parts
  and trace the cause back to the originating operation before continuing — do
  not pass non-conforming parts on a concession without sign-off.
- **Material faults (E505, E510):** escalate to the line lead before resuming —
  a wrong grade or a shortage often affects more than one job and is a common
  cause of late delivery.
- **Any safety fault (E601):** always logged; escalate to the shift lead if the
  cause is not immediately obvious.