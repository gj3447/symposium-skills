# Changelog

> SYMPOSIUM/SKILLS 변천사. [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) 형식.
> Conventional Commits 1.0.0 자동 분류. git-cliff 자동 생성 — 직접 편집 금지.
>
> 학문 grounding: PROM 16 (`PROM_16_SKILL_VERSIONING_REPORT.md`) — Lehman SCM 8 laws / SemVer 2.0.0 / Adams-McIntosh SANER 2016 / SLSA v1.0.
> KG: `lesson-prom16-skill-versioning-academic-2026-04-29` (16/16 ResearchFinding, 10 seeds).

## [Unreleased]

### Added

- *(versioning)* Adopt Keep a Changelog 1.1.0 + git-cliff auto-regen (PROM 16 F1) ([`014bc98`](#014bc98b6c33a578918f7511fe90aad8a7267593))
- *(versioning)* SKILL.md ## History + SemVer migration + KG :SkillVersion (PROM 16 F2-F4) ([`aba6319`](#aba63196aee83c16e02627692b65f9543622d980))
- *(versioning)* Apt phase skills ## History (PROM 16 F7) + Architecture Principles KG scaffolding ([`ffbb331`](#ffbb3313c430a88b9e342d019f7678a84edff486))
- *(apt-cleanup)* New skill — Phase 6 Cleanup Gate materialization (PROM 16 F8) ([`5d124c2`](#5d124c25b600eac87e7a56a7b3b2e64d684d7cb2))
- *(apt-st)* V27.0.0 — Exhaustive Cover Scope (8 ST decision areas + SCW gate hook) ([`f17e885`](#f17e885d2cf4f92f63cf466d097313ad2cfb7d39))
- *(a6)* SKILL.md slot resolver PoC — bin/resolve_slot.py (L1 tier) ([`27a85ee`](#27a85eeee7be8d56141eacc99ebad5c48ea80293))
- *(longinus)* Sha256 verification daemon PoC — bin/longinus_sha256_daemon.py ([`826be29`](#826be29b3339a7da3b2711baa79c35dc537bd7a8))
- *(longinus)* Status-aware verify (DIRECTORY_SKIP / ORPHAN_REFERENCE) ([`b2fd9fb`](#b2fd9fb2ead49524d6974d8e2401878ec9aaebf7))
- *(a6)* L2 build step validator — bin/skill-resolve-check.sh ([`e7264ec`](#e7264ecbfc42550b1933e17a999424b3d166bd56))
- *(taliban)* Mathematical lens stratified sampler — bin/taliban_mathematical_sampler.py ([`2620c42`](#2620c42ffb9fce1fe63dde6d75ad11773d888047))
- *(a6)* L2 inline pre-build invariant in skill-build-manifest.py ([`5cb569c`](#5cb569c3b6c824e9444306af8cdaaba99072d8bf))
- *(longinus)* Launchd plist for sha256 daemon (1h verify schedule) ([`533f7e7`](#533f7e731f5f4563b0ac3760c07294dd94a93a5c))

### Fixed

- *(longinus)* Multi-FS_BASE fallback + status classifier (91.2% coverage) ([`c2b0894`](#c2b0894d976373283750c8b9ce46082bd4a29af7))
- *(taliban)* Bind sampler to real KG :Lens codes ([`f8effb2`](#f8effb21b89414ed8e8b9036bc177a7aaf2ce4dc))

### Changed

- *(apt)* Progressive Disclosure split — SKILL.md 1804 → 381 lines + 8 references/ (PROM 16 F6.1) ([`79fd860`](#79fd860fba8088866e3eac08c418548767da368d))

### Miscellaneous

- *(cleanup)* Archive legacy SKILL.md .bak files (PROM 16 F6 prep) ([`f0fd863`](#f0fd8634862be7bc5a9d7b0c24f0913ebc4c6a7e))
- *(skill-versions)* KG iter 1-4 closure snapshot — v27.1.0 + HR1-18 + Lakatos test ([`050e101`](#050e1011826fadb257686380dfc6400c87dad6ab))
- *(manifest)* Refresh index.json — v27.1.0 versions + new merkle (post-iter1-4) ([`27b08ea`](#27b08ea8e2402d117caa566887c8450de57cd6bb))
- *(longinus)* Bump query LIMIT 1000 → 5000 (cross-canon scale) ([`d0ecc48`](#d0ecc486079c58a34fede878297748bd755f6e35))

## [26.0.2] - 2026-04-26

### Changed

- *(helpers)* Path-agnostic via __file__/SCRIPT_DIR (Q7) + remove workflow sudo ln hack ([`dccafc1`](#dccafc14fc5eb71d4bf4f497f34f7be4adec13ac))

## [26.0.1] - 2026-04-26

### Added

- *(manifest+discovery)* Merkle_root + .well-known/skills/index.json ([`697fdae`](#697fdae7912afdd0cd9b5721a927a28a21e5ce33))
- *(channel)* Introduce channel field + CHANNELS.md policy (Plan-6 phase 1) ([`224d379`](#224d3790c393900c7e57af15e1bf4db3f429c619))
- *(supply-chain)* SBOM + in-toto attestation + OCI skeleton (Plan-3 phase 2 lite + Plan-4 phase 1 lite) ([`9376bc9`](#9376bc99ab34798ccfc694b5ca07c5745557f50d))
- *(supply-chain+marketplace)* GH Actions skill-supply-chain.yml + .claude-plugin/marketplace.json (Plan-3 phase 3 prep + Plan-symposium-skill-lab-v1 Phase D prep) ([`bba9283`](#bba9283ad18e9bdeca01976f0ba71e35c3edcf29))
- *(discovery)* AGENTS.md cross-tool index + .agents/skills/ symlink shim (Phase D) ([`2ca6d68`](#2ca6d68ada33c478756f6d8d553f654f8a2dfbb8))

### Fixed

- *(manifest)* Rebuild after pre-commit hook test cleanup ([`065b2ac`](#065b2ac3c476cf0116b2bc391a4922fed8053ed7))
- *(manifest)* Deterministic generatedAt = HEAD commit time ([`c2ce74e`](#c2ce74ebba541ce3a2d76cd467ff2abe405aeff9))
- *(manifest)* Correct git_tree_sha via rev-parse HEAD:<path> ([`f655c2d`](#f655c2dbd1ac28ca81433ed1de10fcedd27eac47))
- *(ci)* Add bin/ to git + workflow path injection (CI activation pre-fix) ([`d053308`](#d0533089dacac31041ba13b1e6caab00f8d9f16c))

### Miscellaneous

- *(skills)* Add MANIFEST.json v1 (metadata + git_tree_sha per skill) ([`6d4f6cf`](#6d4f6cf830e987712293625f518da7c0afa5ff4c))
- *(governance)* Add CODEOWNERS placeholder (Plan-3 phase 1) ([`606bfad`](#606bfad9d4c4ad5c412a1a31a125a4f671b08a17))
- *(manifest)* Rebuild after kg_ref drift (Plan-5 phase 2) ([`4b9a3f7`](#4b9a3f7e3c262da1a1f1bd2e382bd412a6dd697f))
- *(artifacts)* Refresh MANIFEST/SBOM/attestation/index for HEAD=2ca6d68 ([`c528c97`](#c528c9785c7f5deaf57ba08788d43aa950ddb190))

## [26.0.0] - 2026-04-26

### Added

- *(skills)* Add kg_ref frontmatter field to all 27 SKILL.md (Phase C2) ([`6da81af`](#6da81afddeb759ab7fd8bc4f554bd5f6bc0ab08d))

### Miscellaneous

- Initialize skill repo (rollback infra for ActionPlan plan-claude-agent-skills-2026-04-26) ([`ce92391`](#ce9239105a13bff3cff3db737374272f6d5571d7))

<!-- generated by git-cliff -->
