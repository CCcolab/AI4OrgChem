# Release Review and Tagging Checklist

[中文](RELEASE_CHECKLIST_zh-CN.md)

This checklist is a mandatory release gate. It applies to every new AI4OrgChem version.

## Non-negotiable tagging rule

**Do not create, move, or recreate a version tag until the complete release-level review has finished and every required gate below has passed.**

The reviewed release-candidate commit must remain unchanged between final approval and tag creation. If any file changes after approval, the review is no longer current: restart the affected checks, update the manifests, and approve the new commit before tagging.

## 1. Freeze the release candidate

- [ ] Define the intended version and release scope.
- [ ] Confirm that the candidate is on `main` and that the working tree is clean.
- [ ] Record the exact full commit SHA proposed for the release.
- [ ] Confirm that no internal workspace, raw run output, credentials, copyrighted source material, local path, or unrelated file is included.

## 2. Review scientific and documentary consistency

- [ ] Reconcile proposition verdicts, numerical anchors, evidence scope, limitations, and terminology across all public pages.
- [ ] Check the README files, review guides, evidence records, manuscript matrices, release notes, changelog, citation metadata, machine-readable records, and reproducibility guides.
- [ ] Confirm that English entry points route to English pages where an English counterpart exists, and Chinese entry points route to Chinese pages.
- [ ] Check all local links, headings, filenames, version strings, and displayed release statistics.
- [ ] Confirm that historical releases remain clearly distinguished from the current release.

## 3. Run release-level verification

- [ ] Refresh the file inventory and SHA-256 manifest only after all content edits are complete.
- [ ] Run the complete release validator, public-evidence validators, focused tests, and link audit.
- [ ] Review the generated diff and confirm that it contains only intended public changes.
- [ ] Push the candidate through a pull request and wait for all required GitHub CI and CodeQL checks to pass.
- [ ] Merge the reviewed pull request, fetch `main` again, and verify that the remote commit is exactly the reviewed commit.

## 4. Create the immutable release

- [ ] Only after Sections 1–3 pass, create the annotated version tag on the reviewed commit.
- [ ] Create the GitHub Release from that exact tag.
- [ ] Build and attach the complete curated archive and its checksum/manifest files from the tagged tree.
- [ ] Do not overwrite release assets or retarget the tag after publication. Corrections require a new commit and, when the frozen package must change, a new patch version.

## 5. Verify after tagging

- [ ] Perform a clean clone or archive extraction from the tag, not from a pre-existing working tree.
- [ ] Verify the full commit SHA, archive checksums, manifest, file inventory, validators, tests, and public links.
- [ ] Record the clean-clone verification result and the final release identifiers.
- [ ] Announce the release only after this post-tag verification succeeds.

## Required release record

The release record must identify the version, tag, full commit SHA, review date, reviewer/responsible author, CI result, asset checksums, clean-clone result, known limitations, and any failed or intentionally unexecuted checks.

