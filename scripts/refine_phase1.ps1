$File = "PHASE_1_PLAN.md"

if (!(Test-Path $File)) {
    Write-Host "ERROR: PHASE_1_PLAN.md not found."
    exit
}

$content = Get-Content $File -Raw

# --------------------------------------------------
# Add Project Snapshot
# --------------------------------------------------

if ($content -notmatch "Project Snapshot") {

$snapshot = @"

---

# Project Snapshot

| Property | Value |
|-----------|-------|
| Project | MedSave |
| Current Phase | Phase 1 - College Internal Selection |
| Current Status | Active Development |
| Current Version | v1.0 |
| Current Sprint | Phase 1 |
| Current Milestone | README |
| Overall Progress | 5% |
| Last Updated | 30 Jul 2026 |

"@

$content = $content.Replace(
"Duration: ~20–30 Days",
"Duration: ~20-30 Days`r`n$snapshot"
)

}

# --------------------------------------------------
# Add Success Metrics
# --------------------------------------------------

if ($content -notmatch "Success Metrics") {

$metrics = @"

## Success Metrics

Phase 1 is successful if:

- College selects MedSave.
- Demo runs without major failures.
- Repository looks professional.
- Judges understand the solution clearly.
- Team can confidently answer technical questions.

"@

$content = $content.Replace(
"Success means:

The college selects MedSave to represent it in SIH.",
"Success means:

The college selects MedSave to represent it in SIH.

$metrics"
)

}

# --------------------------------------------------
# Add Assumptions
# --------------------------------------------------

if ($content -notmatch "# Assumptions") {

$assumptions = @"

# Assumptions

- Internal SIH evaluation is expected within approximately 20-30 days.
- Existing deployed prototype remains the engineering foundation.
- Documentation evolves with development.
- Phase 2 starts only after successful college selection.

---

"@

$content = $content.Replace(
"# Change Log",
"$assumptions# Change Log"
)

}

# --------------------------------------------------
# Improve Resume Guide
# --------------------------------------------------

$oldResume = @"
Current Phase:

Phase 1

Current Milestone:

(To be updated)

Completed:

(To be updated)

Next Task:

(To be updated)

Latest Decisions:

(To be updated)
"@

$newResume = @"

| Item | Value |
|------|-------|
| Current Phase | Phase 1 |
| Current Milestone | README |
| Last Completed | Repository Audit |
| Next Task | Improve README |
| Next Milestone | Folder Structure |

"@

$content = $content.Replace($oldResume,$newResume)

# --------------------------------------------------
# Add Document Metadata
# --------------------------------------------------

if ($content -notmatch "Document Metadata") {

$metadata = @"

---

# Document Metadata

| Property | Value |
|-----------|-------|
| Owner | Team UGC |
| Maintained By | Project Team |
| Review Frequency | After every milestone |
| Last Reviewed | 30 Jul 2026 |
| Next Review | After README completion |

"@

$content = $content.Replace(
"# Final Note",
"$metadata# Final Note"
)

}

# --------------------------------------------------
# Save as UTF-8
# --------------------------------------------------

$content | Set-Content $File -Encoding utf8

Write-Host ""
Write-Host "==========================================="
Write-Host " Phase 1 document refined successfully"
Write-Host "==========================================="
Write-Host ""
Write-Host "Added:"
Write-Host " - Project Snapshot"
Write-Host " - Success Metrics"
Write-Host " - Assumptions"
Write-Host " - Improved Resume Guide"
Write-Host " - Document Metadata"
Write-Host ""