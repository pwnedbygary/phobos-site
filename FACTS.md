# Fact sheet

Every claim the site makes, and where it comes from. Sources are the repository at master `062dd53e2` (22 Oct 2026),
cited as `file:line`, except where a citation names master `7986aef5b` (22 Oct, 23:51 EDT), and LICENSE, whose line
numbers are all at master `ac0ad694c` (23 Oct, 04:15 EDT), each checked there; its pull requests (`#n`) and releases
as GitHub lists them (`gh pr view`, `gh release view`); git itself; and, marked **(notes)**, the project's
coordination notes (the owner's decisions and other private notes), which aren't public. Dates are US Eastern, as the
repository's own docs give them. "Derived" means computed from the named sources. The development log and the
releases come from `gh` when `tools/fetch.py` runs, and are committed; every build, the Pages workflow's included, uses
them as committed, so they're correct as of `data/devlog.json`'s `fetched` time.

Data refetched at 04:17:23 EDT on 23 Oct 2026 (2026-10-23T08:17:23Z), once #302 had merged (04:15:58 EDT): 190
merged pull requests (#1 on 24 Sep to #302 on 23 Oct), 10 releases, 7 of them tagged, v2.4.0 the latest; #294, #300
and #303 open drafts. The owner's choices of
21 Oct ~17:21-17:52 and ~18:27 **(notes)**: the host is a new repository, pwnedbygary/phobos-site, on GitHub Pages at
https://pwnedbygary.github.io/phobos-site/; his two quotes may appear lightly tidied (capitals and spelling only),
still signed by him; LICENSE gains the missing notices in a pull request of its own (#296, merged on 22 Oct at 00:10
EDT) before the site deploys. And of ~23:05 **(notes)**: the site's source is published with its pages, which a
workflow builds. And of 23 Oct ~11:03 **(notes)**: the site's own text rewritten in his voice, about a third shorter,
each reworded line making the claim it made before or a smaller one; the rows below describe the new wording. The site
speaks as him in the first person: "my Retroid Pocket 6" (or "my RP6") is the device every on-device measurement,
screenshot and recording here comes from, and "my PSP-1000" the PSP of the measurement rounds and the captures, both
called the owner's before, and "I timed" (16 Oct) is his running those rounds on it **(notes)**. His two quotes are
signed "Gary" (his choice of 23 Oct ~13:44 **(notes)**). And of ~11:15 **(notes)**: the one-liner (data/site.json
`description`) and the development log's titles in his voice too, and a swear now and then, as he writes.

## Hero

| Claim | Source |
|---|---|
| A multi-system emulator built on ares | README.md:5 ("forked from ares") |
| An Android app made for handhelds and controllers | #51 "Hardware buttons drive the menus: D-pad and stick move a visible focus, L1/R1 switch tabs"; docs/implementation-plan.md:404 |
| Plus a desktop program for Linux, Windows and macOS (the same in the meta description; it and the lead keep the controller to the app) | README.md:116-121; #97's body: "The desktop UI is a working placeholder; matching the Android UI is the follow-up." |
| 34 systems | The app's Library header counts the systems the core lists (android/.../ui/LibraryScreen.kt:108); the core lists 35 (android/app/src/main/cpp/PhobosJNI.cpp:19-56, `enumerateSystems` at :59) and the Library merges ZX Spectrum 128 into ZX Spectrum (android/.../ui/MainViewModel.kt:1467-1474): 34. The RP6's own screenshot shows "34 systems" (media rp6-library) |
| Including the PSP, whose core is built from scratch (one of the 34: data/systems.json lists 27 verified, the PSP experimental and 6 untried) | README.md:5, 66-69 |
| The one-liner (the pages' meta, Open Graph and Twitter descriptions): a multi-system emulator built on ares, with a PSP core built from scratch; an app for Android ARM64 handhelds, made for controllers, plus a desktop program for Linux, Windows and macOS | As for the rows above and the "What it is" rows below; in his voice since 23 Oct ~11:15 **(notes)**, the claims of the line he picked on 22 Oct |
| Download v2.4.0, latest release, 16 Oct 2026 | `gh release list`: v2.4.0 isLatest, published 2026-10-16T13:22:00Z (09:22 EDT); filled in from data/releases.json |
| Nightly builds, one for every push to master | README.md:11-12, 190 |
| 266 PSP games in the test library | README.md:44; docs/psp-compatibility.md ("Games tested: 266") |
| 4 platforms | README.md:14 (APKs, AppImage, macOS app, Phobos.exe); release v2.4.0's assets |
| 190 pull requests merged since 24 Sep 2026 | Derived: the count of data/devlog.json (`gh pr list --state merged`, fetched 04:17 EDT on 23 Oct), first merged 2026-09-24 (#1) |
| New in 2.0: a PSP core built from scratch | README.md:5 ("new in 2.0"), 11 (v2.0.0 "the first with the PlayStation Portable"); "built from scratch" as above |

## What it is

| Claim | Source |
|---|---|
| ares, an emulator that puts accuracy first | README.md:5 |
| Keeps ares's cores and adds fast ARM64 paths, Vulkan, custom GPU drivers and a UI you drive with a controller | README.md:5, 7; #51 |
| The platforms' cards: Android ARM64, Linux, Windows and macOS | README.md:5, 13, 116 |
| Phobos's own code is GPL-3.0-or-later | README.md:271; LICENSE:1-22; #98 |
| Modern (ARMv8.2-A, FP16, dot product) and Legacy (any 64-bit ARM), Android 8.0+ | README.md:13 |
| Updates itself from GitHub (the highlights' Builds card) | README.md:12, 190 |
| Linux AppImage with a zsync file, for smaller (delta) updates | README.md:192; v2.4.0's assets (`Phobos-2.4.0-x86_64.AppImage`, `.zsync`) |
| Windows: Phobos.exe in a zip | README.md:14; v2.4.0's asset `Phobos-2.4.0-windows-x64.zip` |
| macOS: universal app, MoltenVK bundled | README.md:116-117; scripts/package-macos-app.sh:2, 14 |
| Tagged releases since v2.0.0 have all four; nightly builds are Android only | `gh release view`: v1.0.0 and v1.1.0 carry only their two APKs; v2.0.0 to v2.4.0 also the AppImage (with zsync), the macOS zip and the Windows zip; `gh release view nightly-216052` (two APKs, ffmpeg tarball, update.json) |
| 27 verified, PSP experimental, 6 not yet tried with a game (the legend's counts, which build.py counts from data/systems.json) | README.md:22-48 (the three groups of the systems table) |
| Each system's group and status | README.md:22-48; names from PhobosJNI.cpp:19-56 |

## Highlights

| Claim | Source |
|---|---|
| PSP core written in ares's style from documentation, tests and real-PSP measurements; no code from other PSP emulators; PPSSPP read only as a reference | README.md:65-69 |
| No firmware needed; the PSP's system software emulated at a high level | README.md:71-76 |
| The CPU's recompiler for ARM64 and x86-64, an interpreter behind it | README.md:77 (the Allegrex's, built on sljit) |
| Three renderers, Vulkan up to 10x the PSP's 480x272 | README.md:80-87 (Vulkan (accurate) "at the PSP's 480x272 or up to 10x over (PSP Resolution)"; Vulkan (fast) "also transforms and lights 3D on the GPU"); the software renderer draws at 480x272, as for the gallery below |
| ISO, CSO, ZSO, DAX, JSO, CHD opened as they are (read in place); versioned save states | README.md:91, 96-97 |
| 197 of 266 reach a menu or gameplay within a minute (run of 11 Oct) | README.md:290; docs/progress.md:8 |
| 13 days from first code (3 Oct) to v2.4.0 (16 Oct), its fifth release | docs/progress.md:7 |
| PSP timing the default since 19 Oct; "Fast" the opt-in | #269 (merged 2026-10-19T05:35Z, 01:35 EDT); docs/psp-core.md part 106 (heading at :16937) |
| The GE takes *about* as long as the PSP-1000 took | Derived: the fit's median miss is 5.0% (docs/psp-core.md:17065) and frames are judged within 15% (:19883) |
| Fitted to 3,373 display lists timed on the owner's PSP-1000, median miss 5.0% (the stats) | docs/psp-core.md:17065 ("3,373 lists 5.0% at the median"); rounds 6, 8, 9, 10 at :16937 |
| Later rounds measured the CPU's effect on the GE (#279, #291) | docs/psp-core.md parts 113 (:19183) and 115 (:19767) |
| All eight judged scenes within 15% by their whole frame since 21 Oct | docs/psp-core.md:19883 ("Frames judged: 8, all within 15%"); table :19872-19881; #291 merged 2026-10-21T17:08Z |
| Each change to the timing is run against all 266 games before it merges | docs/handoff.md:261 (#291, "266 games each in Software and Vulkan"), :751 (#277), :1139 (#271), :936 (#269, "his library check with the PSP's timing"), :918 (#279); docs/progress.md:267 (merges wait for a fresh library check) |
| The deviation chart's eight values, shown to two decimals: −0.87, −1.66, −12.69, −11.82, −10.38, +9.95, +9.61 and −5.80% | docs/psp-core.md:19874-19881, the "This branch / Against the PSP" column (−0.873, −1.661, −12.686, −11.825, −10.382, +9.952, +9.612, −5.801); two decimals so Activision Hits' menu shows +9.95%, under the owner's +10% limit for it (:19771-19773) rather than on it |
| GE thread in the core since 18 and 20 Oct (#272, #277); results identical to inline | #272 (merged 2026-10-18T08:08Z), #277 (2026-10-20T08:35Z); docs/handoff.md:1164 ("exact"), :647-657 |
| Killzone 149M to 74M host instructions a frame with it on | docs/handoff.md:663 |
| Off by default; "PSP Graphics Overlap" built, and will be offered once On beats Off on the RP6 | docs/handoff.md:657-658 ("is built and not offered till On beats Off on the RP6") |
| N64: blocks linked, dispatcher trips 10.1 to 0.6 million a second | #10 title; docs/progress.md:62 |
| RSP multiply-accumulates as inline NEON | #15, #16 titles; README.md:132 |
| 256 render contexts (the timeline's "more RDP contexts"); a Mario Tennis scene from 82 to 5 late frames (the story) | #17 title (its scene: the "Mario Tennis showcase"); docs/progress.md:62 |
| Upscaling 1x-4x, 64DD, Rumble and Controller Paks, Turnip via the GPU Driver Manager | README.md:141, 150-156, 147 |
| N64 on the RP6's stock Qualcomm driver since 21 Oct; black picture before | #292 (merged 2026-10-21T13:27Z) title; docs/handoff.md:298-396 |
| Before/after pictures | media rp6-n64-ocarina-before (nightly-215987) and rp6-n64-ocarina (#292's APK 215990), 21 Oct 08:2x, see MEDIA.md |
| 18 of 22 slow games at full speed at 1x (15 Oct nightly; 7 with v2.3.0) | docs/progress.md:9 |
| 232 of 266 at 59+ fps at 5x (2400x1360), two-minute runs, mostly logos, intros, menus | docs/progress.md:10, 160 |
| 6 Oct: the software renderer on several threads, Peace Walker 10.6 to 60 fps | docs/progress.md:98 |
| N64 median 59.9 fps on the stock driver in all four games checked | docs/handoff.md:377-378 ("59.9 fps median in all eight runs") |
| D-pad and stick focus, shoulder buttons switch tabs | #51; docs/implementation-plan.md:404 |
| Touch controls with a layout per system | README.md:161 |
| 37 themes and their names; glass, retrowave neon, XMB-style backdrop | README.md:184 |
| Performance overlay; remapping per game, console or all | README.md:186, 160 |
| Screenshot film-strip card and folder | #273 title (merged 2026-10-18T06:55Z) |
| Settings → About updates from either channel | README.md:12 |
| Nightly pre-release for every push to master (the hero), Modern and Legacy (the Android card) | README.md:11-12, 190; nightly assets |
| Tagged releases carry the desktop program | README.md:14, 192 |
| Builds numbered from git history, locally and on CI | README.md:194 |

## Gallery

Every picture and clip: MEDIA.md (file, game, frame, build, date, how it was made). Clip and still captions: the game
titles are the discs' or the test library's names. "At 4x" (the gallery's intro and "In motion") and "all of them
real 4x": every PSP still and clip there, and the reel at the top, was measured. On a still's lossless frame, about
25% of its colour edges fall on the 4-pixel grid (chance; a frame drawn at 480x272 and shown 4 times larger puts all
of them there) and 86.8-99.4% of its 4x4 blocks have detail inside; on the masters, every frame a clip or the reel
uses has 24.9-30.2% of its luma edges on the grid. MEDIA.md gives each one's numbers and the note on the method.
On 23 Oct these replaced stills and clips from the same runner that measured at native size (the owner's report of
23 Oct ~11:25 **(notes)**). "Full throttle, right into a wall" (WipEout): the scene holds Cross from frame 1
(MEDIA.md's row for clip-wipeout), and the clip ends at the wall. "The compatibility report says how far each one
gets": docs/psp-compatibility.md. The imagery itself (commercial games' frames and logos) is the owner's choice of
21 Oct ~19:07 **(notes)**: every picture public.

"On my Retroid Pocket 6", the device's screen recordings: MEDIA.md's rows and notes for clip-rp6-colin-mcrae,
clip-rp6-mario-tennis and clip-rp6-themes (the device, nightly 216022, each piece and window, the GPU driver, the
commands and the sha256s). "Turnip" in one caption: MEDIA.md's note on the driver (Turnip, StevenMXZ
v27.0.0-R1, the app's active driver from 00:44:30). "Drawn at native resolution by the Software (exact) renderer"
(Colin McRae's caption; native is the PSP's 480x272): MEDIA.md's row and note for clip-rp6-colin-mcrae, the app's pause menu in the same run
of the game (piece 9 at 119.45 s, about 00:53:24) showing PSP Renderer set to Software (exact) and no "Restart to Apply"
row, which android/.../ui/EmulationMenu.kt:454-483 adds once the settings a game takes as it starts differ from those
it started with; the software renderer always draws at Native, 480x272: android/.../util/PspVideo.kt:62-67 and :76.
Both files are the same at the nightly's commit, 8c2b1dde (git). "Picking themes with the controller": #51 ("Hardware
buttons drive the menus: D-pad and stick move a visible focus") and the clip, in which the focus outline moves from row
to row and card to card. Which clips: the owner's choices of 22 Oct ~01:10 **(notes)**, Colin McRae for the PSP and the
second recording for the N64.

## Story

| Claim | Source |
|---|---|
| ares's line began on 14 October 2004: bsnes, then higan, then ares | README.md:5 ("began development on October 14th, 2004 as a descendant of higan and bsnes"); ares's own README:5-6 (the same); the order: Wikipedia, "Higan (emulator)" (fetched 21 Oct 2026: "Development of the emulator began with the name bsnes on October 14, 2004", and ares "a fork of higan") |
| Trades some speed for clear code | README.md:7 |
| Near and the ares team; "none of it would exist without" them and the projects credited | LICENSE:28 ("ares team, Near et al"); Phobos is "forked from ares" (README.md:5) |
| "It started off as a desktop to Android port of ares" | The owner's own words, 21 Oct 2026 ~17:13 **(notes)**, tidied in capitals only, as he allowed (~18:27, **(notes)**); signed "Gary", his choice of 23 Oct ~13:44 **(notes)** |
| Forked at ares's commit of 25 July 2026 | docs/handoff.md:7911 (fork point `cdabe5c5a`); `git log -1 cdabe5c5a`: 2026-07-25 19:12 +0100 |
| 27 July: 64-bit native Android app and native Vulkan for the N64, the same day | docs/progress.md:35, 57 (git history before 13 Sep 2026 isn't in git; the docs are the source) |
| ares's desktop front end swapped for the Android app in Phobos | docs/handoff.md:7914 (desktop-ui, hiro and ruby removed) |
| Kotlin and Jetpack Compose | README.md:5, 259 |
| ARM64 work on the N64 recompilers and Vulkan renderer | README.md:5 |
| v1.0.0 on 20 Aug 2026: Neo Geo, GPU Driver Manager, PC Engine, SuperGrafx (the last two in the timeline) | `gh release view v1.0.0` (2026-08-20T19:47Z); docs/progress.md:59 |
| 15 Sep: measurements for speed claims, independent review before merging | docs/progress.md:60; docs/development-process.md:9-48 |
| 24 Sep: first pull request, a fix for Neo Geo CD's garbled menu text (#1, the timeline) | #1 (merged 2026-09-24T19:19Z; its title names the DMA's byte order); docs/progress.md:61 |
| The N64 figures (#10 and #17 in the story; #15, #16 and #18, "less power", in the timeline) | #10, #15-#18 titles (#18: 4.76 to 4.15 W); docs/progress.md:62 |
| 37 themes (#9), performance overlay (#5), glass dock (#20) | #9, #5, #20 titles; docs/progress.md:63 |
| v1.1.0 on 28 Sep; in the timeline, #1-#25 and frontends that start games (#25) | `gh release view v1.1.0` (2026-09-29T01:07Z = 28 Sep 21:07 EDT; its notes list #1-#25); #25 title |
| 28 Sep: in-app updates (#26, the timeline) | #26 (merged 2026-09-29T02:34Z = 28 Sep 22:34 EDT); docs/progress.md:65 |
| 29 Sep: a PSP core to rival PPSSPP in compatibility and speed | docs/progress.md:66 |
| 30 Sep: buttons drive the menus (#51, the timeline) | #51 (merged 30 Sep); docs/implementation-plan.md:404 |
| PPSSPP couldn't be adopted: it is under the GPL, and the console firmware ares compiles in can't be; clean room | docs/progress.md:76 ("PPSSPP can't be adopted: it is GPL-2.0-or-later, and the firmware ares compiles in can't be under the GPL.") |
| 3 Oct: the CPU core (interpreter and recompiler) and a first measurement on a real PSP (the timeline) | docs/progress.md:77-80 |
| 5 Oct: PSP SDK samples in the app on the RP6 at 60 fps; Lumines and SF III 3rd Strike title screens | docs/progress.md:92, 94 |
| 6 Oct: first 3D games in play, first at full speed on the device, all 266 games through the runner (#154) | docs/progress.md:96, 98, 100; #154 (merged into the PSP stack's branch 2026-10-07T04:15Z = 7 Oct 00:15 EDT; the first run was on 6 Oct, docs/progress.md:43) |
| 7 Oct: hardware renderer on Vulkan | docs/progress.md:109 |
| One game of 266 left black; v2.0.0 on 11 Oct, Experimental; 194 of 266 at a menu or gameplay | docs/progress.md:119; `gh release view v2.0.0` (2026-10-11T10:02Z) |
| v2.1.0 to v2.4.0 on 12, 13, 14 and 16 Oct (the timeline) | `gh release list` (12, 13, 14, 16 Oct); docs/progress.md:243-246 |
| 16 Oct: the owner timed games' display lists on his PSP-1000; 4 to 12 times the model | docs/progress.md:156, 163; who ran it **(notes)** |
| 19 Oct: measured timing the default (#269) | #269 |
| The "before" chart's values | docs/progress/data.json:335-336 |
| "Has since merged back to desktop in an attempt to port it back to allow for easier controller navigation/use, as well as a sleek, modern UI." | The owner's own words, 21 Oct 2026 ~17:13 **(notes)**, the sentence's second half; "Has" capitalised to open the quote, as he allowed (~18:27, **(notes)**); signed "Gary", his choice of 23 Oct ~13:44 **(notes)** |
| 3 Oct: desktop builds for Linux, macOS and Windows, CI for every pull request (#97) | #97 (merged 2026-10-03T18:00Z); README.md:116-118 |
| PSP joined the desktop program on 6 Oct | docs/progress.md:99; git `c5418b698` (2026-10-06, "Desktop: PSP games") |
| Desktop builds on every tagged release from v2.0.0 | `gh release view v2.0.0` ... `v2.4.0` assets |
| Desktop is pretty plain for now, in SDL's debug font (its pictures show the library and pause menu) | README.md:119-121 |
| The library and menus answer a gamepad | desktop/Input.cpp:16-24, :42 (SDL gamepad buttons mapped); desktop/main.cpp:650-651 ("the controller open[s] the menu"); the library's footer "Enter/A Play, F3/Y Games folder, F5/X Rescan" (media desktop-library) |
| 20 Oct: #290 fixes the N64 recompiler on x86-64 (the timeline) | docs/handoff.md:402-408 (ares compiles its code with `-fwrapv -fno-strict-aliasing`, which Phobos's CMakeLists.txt never included; without them GCC compiled VMOV's and VMULQ's reads wrong); #290 (merged 2026-10-20T21:47Z) |
| #294, still open, brings hotkeys and a Hotkeys page to the desktop | `gh pr view 294` (open draft, opened 2026-10-21T21:07Z; its body: "a Hotkeys page in the pause menu: keyboard keys, pad buttons, triggers, stick directions and mouse buttons") |
| Today: merged count since 24 Sep, release count "in all", latest release and its date | Derived from data/devlog.json and data/releases.json at build time; the count is every tagged release, v1.0.0 of 20 Aug included, so the sentence keeps "since 24 September" to the merges |
| Today: the GE runs *close to* real PSP timing | As for the highlights' "about as long as" above |

## Timeline

Each entry restates a claim above; the extra ones:

| Claim | Source |
|---|---|
| 14 Oct 2004: the line ares descends from begins: bsnes, then higan, then ares | As for the story's first chapter above |
| 5 Oct: the PSP SDK's samples on the RP6; on the host, Lumines's and Street Fighter III 3rd Strike's title screens | docs/progress.md:92 (samples in the app on the RP6), :94 ("On the host, Lumines reached its title screen, and Street Fighter III 3rd Strike's port its own at 60 fps") |
| 6 Oct: #154, the runner's first pass (it merged into the PSP stack just after midnight, so the log shows 7 Oct) | `gh pr list --state merged --json number,baseRefName,mergedAt`: #154 into `cursor/psp-test-data-2b67` at 2026-10-07T04:15:58Z |
| 13 Oct v2.2.0 ("first speedups for the slow games, and fewer Vulkan stalls"), 14 Oct v2.3.0 ("system fonts" for sceFont) | `gh release list`; docs/progress.md:244-245 ("The slow games' first rounds, Vulkan without waiting for its own pixels"; "Savedata, sceFont, God Eater 2, ...") |
| 14 Oct: the runner built for Android, a commit measured on the RP6 before it merges (#255) | #255 title; docs/progress.md:145 |
| 15-16 Oct: whole library at 5x, no crashes, 232 averaged 59+ | docs/progress.md:160 |
| 16 Oct v2.4.0 summary | docs/progress.md:243 |
| 11 Oct: v2.0.0 merged as a stack of about 100 pull requests (#208) | docs/progress.md:118 ("About 100 pull requests, #100 to #209, as one"); the recount, from `gh pr list --state all --json number,headRefName,baseRefName,state`: 96 in the chain from #207 down to #100 (each one's base branch the next one's head), plus #154, #158, #165 and #179 merged into its branches; #208's body says 95 ("95 pull requests (#100–#207 except #103)") |
| 12 Oct: the PSP's system dialogs (#221) | #221 title; docs/progress.md:128 |
| 18 Oct: GE thread (#272), screenshots (#273); 19 Oct #269 (the GE takes about the time a PSP-1000 took); 20 Oct #277, #290; 21 Oct #292, #291 | the pull requests' titles and merge times; "about" as for the highlights above |

## Development log

| Claim | Source |
|---|---|
| Every merged pull request with its number, merge time and link | data/devlog.json (`gh pr list --state merged --limit 1000 --json number,title,mergedAt,url`), oldest first, fetched 04:17 EDT on 23 Oct |
| Each one's title, in plain English | data/devlog-titles.json: GitHub's title (devlog.json) said again in the owner's voice, the same claim or a smaller one, with nothing from outside that pull request (#297's games from its body: Need for Speed: Shift, Burnout Dominator and Legends, Midnight Club: L.A. Remix); ten keep GitHub's words. A merged pull request with no entry would show GitHub's title, and build.py lists any; a key that isn't a merged pull request, or an empty title, or one with a line break, fails the build. The page says the titles are reworded and that each number links to the pull request, where GitHub's full title is. The pull request titles quoted elsewhere in this file are GitHub's, which the page no longer shows word for word |
| Work went straight to master before 24 Sep | git: first-parent commits from 13 Sep 2026; #1 merged 24 Sep |
| The PSP core's stack, about 100 pull requests numbered between #100 and #207, reached master together through #208; GitHub lists most as closed | docs/progress.md:118 and the recount, as for the timeline's 11 Oct entry above (96 in the chain, plus #154, #158, #165 and #179; #208's body says 95); 96 of the 100 are closed, and `gh pr list --state merged` holds only 7 of #100-#209 |
| Five merged into other branches first and show with those dates: #154, #158, #165 and #179 into the PSP stack, #275 reaching master through #281 | `gh pr list --state merged --json number,baseRefName,mergedAt`: #154 `cursor/psp-test-data-2b67`, #158 `cursor/psp-ge-features-2b67`, #165 `cursor/psp-ge-curves-2b67`, #179 `cursor/psp-gpu-hw4-2b67`, #275 `pgd-comment-base`; #281's title ("... (#275, into master)") |
| Releases table: the tagged releases; nightlies on the releases page | data/releases.json (`gh release list`), its tagged releases only; nightlies are replaced by each push to master (only the 3 newest were listed at 04:17 on 23 Oct: nightly-216049, nightly-216052 and nightly-216055), so the page links to the releases page for them |

## Roadmap

The roadmap's items are the owner's choice of 21 Oct ~19:07 **(notes)**, worded in his voice on 23 Oct. Its first item, the polling
skip's widening, merged on 22 Oct at 22:51 EDT (#297, "PSP kernel: the polling skip widened to the EA games' and
Midnight Club's loops (part 116)", GitHub's title, which the development log shows reworded; `gh pr view 297`:
2026-10-23T02:51:01Z) and left it, as finished work does: the
roadmap is "What we're working on and what's next" (data/roadmap.json `intro_md`), and the development log
lists #297.

| Claim | Source |
|---|---|
| A loop skip for Dante's Inferno: it skips the loop where the game sits waiting for its next frame, and lands once review and frame-by-frame exactness checks pass | **(notes)** the owner's decisions of 21 Oct |
| Hotkeys, the owner's pull request #294 (open): combos of any length, three bindings, slow motion, frame advance | `gh pr view 294` (author pwnedbygary, open draft, read 23 Oct) |
| GE thread's Auto with handover both ways; keeps a game synchronous where the threads would take turns | docs/handoff.md:758, 1211 |
| Live switching of the PSP's resolution and renderer; it waited for the GE thread and timing work, which has now merged | **(notes)** the owner's decision of 17 Oct 14:15 (wait until the GE thread, #272 and its second PR, and the GE timing, #266-#271, have merged); merged: #266 and #267 on 17 Oct, #268, #270, #271 and #272 on 18 Oct, #269 on 19 Oct, #277 on 20 Oct (`gh pr list --state merged`) |
| Vulkan (accurate) faster | **(notes)** |

## Credits and licences

| Claim | Source |
|---|---|
| ares (ISC), sljit (BSD 2-clause), libchdr (BSD 3-clause), paraLLEl-RDP (MIT, modified), volk (MIT), Vulkan-Headers (Apache 2.0 or MIT), sse2neon (MIT), libadrenotools (BSD 2-clause), FFmpeg (LGPL 2.1), ymfm (BSD 3-clause), MAME portions (BSD 3-clause), C-BIOS (BSD-style); the "And" paragraph's first list; the app's fonts (SIL OFL 1.1) | LICENSE's notices (ares :25-41, sljit :43-70, libchdr :72-100, the rest in their own blocks); README.md:203 for MAME's scope |
| Systematic console icons, BAXY Square, via RomM, MIT: the Library's console art, recoloured for each theme | LICENSE:3830-3845 ("Systematic console icons ... By BAXY Square ... Phobos recolors them at runtime", "MIT License", "Copyright (c) BAXY Square"); "via RomM": LICENSE:3834-3835 ("Obtained via RomM ..., which renamed and reformatted them") |
| The ZX Spectrum ROMs, Amstrad's, redistributed with its permission | LICENSE:3876-3880 ("Amstrad have kindly given their permission for the redistribution of their copyrighted material but retain that copyright") |
| Khronos's OpenGL and EGL headers, MIT-style | LICENSE:392-415 and :418-441 (the Khronos "Materials" permission notice, worded as MIT's); no compiled source includes them (docs/handoff.md:113-115), but LICENSE carries their notices, which is why the credits name them and leave off VMA and librashader, whose notices it doesn't carry |
| SDL 3.2.30 (zlib), by Sam Lantinga and contributors | LICENSE:3126-3145 ("SDL 3.2.30 (linked into the desktop program: Linux, Windows and macOS)", "Copyright (C) 1997-2025 Sam Lantinga", then the zlib license's text) and :3312-3334 (its files by other authors, under the same text); CMakeLists.txt:16-18 (release-3.2.30) |
| HIDAPI (BSD-style), by Alan Ott, Signal 11 Software, and the libusb/hidapi team: inside SDL's joystick code, on Linux, Windows and macOS | LICENSE:3149-3191: "HIDAPI (in SDL 3.2.30, src/hidapi: Linux, Windows and macOS)"; "SDL's joystick code compiles in its copy of HIDAPI: the hidraw backend on Linux ..., the Windows one ... and the macOS one" (:3152-3154); the lines its three files carry, "Alan Ott", "Signal 11 Software", "libusb/hidapi Team" (:3156-3159); "Phobos uses it under the BSD-style one" and "Copyright (c) 2010, Alan Ott, Signal 11 Software" (:3163-3166) |
| Inside SDL 3.2.30: yuv2rgb | LICENSE:3195-3227: "yuv2rgb (in SDL 3.2.30, src/video/yuv2rgb: Linux, Windows and macOS)", "SDL's conversions between YUV and RGB pixel formats" (:3198); Adrien Descamps's (:3201), under the BSD 3-clause text that follows (:3204-3227) |
| Inside SDL 3.2.30: stb_image's JPEG decoder | LICENSE:3231-3275: "stb_image 2.30 (in SDL 3.2.30, src/video/stb_image.h, its JPEG decoder: Linux, Windows and macOS)", "SDL decodes MJPEG frames with it" (:3234); Sean Barrett's (:3241), under the MIT License or in the public domain, whichever one prefers (:3238-3274) |
| Inside SDL 3.2.30: SDL_rotate | LICENSE:3279-3308: "SDL_rotate (in SDL 3.2.30, src/render/software/SDL_rotate.c, from SDL_gfx: Linux, Windows and macOS)", "The software renderer rotates textures with it" (:3281); Andreas Schiffler's (:3287), under the zlib license's text (:3289-3306) |
| Inside SDL 3.2.30, on Linux: the X11 EDID parser | LICENSE:3338-3360: "EDID parser (in SDL 3.2.30, src/video/x11/edid-parse.c and edid.h: Linux)", "SDL's X11 code reads displays' EDID with it" (:3340); Red Hat's (:3342), under an MIT-style permission notice (:3344-3360) |
| Inside SDL 3.2.30, on Linux: the X11 XSETTINGS client | LICENSE:3364-3388: "XSETTINGS client (in SDL 3.2.30, src/video/x11/xsettings-client.c and xsettings-client.h: Linux)", "SDL's X11 code reads the desktop's settings with it" (:3366); Red Hat's and Igalia's (:3368-3369; "Author: Owen Taylor, Red Hat, Inc.", :3388), under a permission notice of its own (:3371-3386) |
| Inside SDL 3.2.30, on Linux: imKStoUCS | LICENSE:3392-3418: "imKStoUCS (in SDL 3.2.30, src/events/imKStoUCS.c and imKStoUCS.h: Linux)", "SDL's X11 and Wayland code maps keysyms to Unicode with it" (:3394); Jamey Sharp's and Josh Triplett's, Red Hat's and Oracle's (:3396-3398), under an MIT-style permission notice (:3401-3418) |
| Inside SDL 3.2.30, on Linux: code from xdg-user-dirs | LICENSE:3422-3448: "xdg-user-dirs (in SDL 3.2.30, src/filesystem/unix/SDL_sysfilesystem.c: Linux)", "SDL's two xdg_user_dir_lookup functions are copied from its xdg-user-dir-lookup.c and adapted" (:3425-3426); Red Hat's (:3428), under the MIT-style text that follows (:3430-3448) |
| Inside SDL 3.2.30, on Linux: the Wayland protocols | LICENSE:3452-3567: "Wayland protocols (in SDL 3.2.30, its wayland-protocols folder: Linux)", "SDL generates its Wayland code from these 22 protocol files" (:3455); each file's copyright lines (:3461-3521), 21 of the files under one MIT-style permission notice (:3523-3540) and text-input-unstable-v3.xml under its own (:3542-3567) |
| Inside SDL 3.2.30, on Linux: PipeWire's SPA header code | LICENSE:3571-3606: "PipeWire's SPA headers (in SDL 3.2.30's PipeWire audio and camera drivers: Linux)", whose static inline functions compile into the Linux program (:3574-3578); Wim Taymans's and Red Hat's (:3583-3587), under the MIT text that follows (:3589-3606) |
| MoltenVK (Apache 2.0), by The Brenwill Workshop Ltd., for the Khronos Group; bundled in the macOS app | LICENSE:3610-3614 ("MoltenVK 1.4.2 (libMoltenVK.dylib, in the macOS app's Contents/Frameworks)", "Copyright (c) 2015-2026 The Brenwill Workshop Ltd.", "Licensed under the Apache License 2.0"); MoltenVK v1.4.2's README.md:10 (the same copyright line, read with `gh api`), hosted under KhronosGroup; its LICENSE at v1.4.2 (fetched 21 Oct); scripts/package-macos-app.sh:2, 14, 21 |
| SPIRV-Cross (Apache 2.0 or MIT), by Arm Limited, The Brenwill Workshop Ltd., Bradley Austin Davis and Hans-Kristian Arntzen: its parser and its GLSL, MSL and reflection compilers, inside MoltenVK | LICENSE:3618-3632: "SPIRV-Cross (in libMoltenVK.dylib, in the macOS app's Contents/Frameworks)"; "its parser and its GLSL, MSL and reflection compilers" (:3621-3622); its copyright lines (:3624-3629); "SPDX-License-Identifier: Apache-2.0 OR MIT, used here under the Apache License 2.0" (:3630-3631) |
| Inside MoltenVK: SPIRV-Tools | LICENSE:3636-3660: "SPIRV-Tools (in libMoltenVK.dylib, in the macOS app's Contents/Frameworks)", "its core library" (:3639-3642); the Khronos Group's, Google's and AMD's (:3644-3657), under the Apache License 2.0 (:3658) |
| Inside MoltenVK: SPIRV-Headers | LICENSE:3664-3741: "SPIRV-Headers (in libMoltenVK.dylib, in the macOS app's Contents/Frameworks)", whose grammar files SPIRV-Tools' tables are generated from and whose spirv.hpp SPIRV-Cross compiles (:3667-3671); the Khronos Group's, under its MIT-style notice (:3673-3697), and the shipped grammar files' own statements, the Khronos Group's and Arm's, under the MIT License (:3699-3741) |
| Inside MoltenVK: cereal | LICENSE:3745-3774: "cereal (in libMoltenVK.dylib, in the macOS app's Contents/Frameworks)", "its binary archives" (:3748-3749); Randolph Voorhies's and Shane Grant's (:3751), under the BSD 3-clause text that follows (:3754-3774) |
| AppImage runtime (MIT), by probonopd: type2-runtime, the part at the start of the Linux AppImage that mounts or extracts the rest | LICENSE:2788-3122: "AppImage runtime (type2-runtime, the start of the Linux AppImage, with the libraries linked into it)" (:2788); "The Linux AppImage begins with the AppImage runtime, the program that mounts or extracts the image after it: type2-runtime's build of its commit fedfad51a, which scripts/appimage-pins.sh in Phobos's source pins by its SHA-256 and CI checks in each AppImage it makes" (:2791-2794); Phobos 2.4.0's is "8f39b89, type2-runtime's continuous build when it was made" (:2796-2797); type2-runtime's LICENSE, "MIT License", "Copyright (c) 2004-23 probonopd" (:2830-2852) |
| Linked into the AppImage runtime: musl, libfuse, squashfuse, zstd, zlib and mimalloc | LICENSE:2797-2828: the runtime is "statically linked with musl, libfuse 3.15.0 (patched by type2-runtime), squashfuse 0.5.2, zstd, zlib and mimalloc" (:2798-2799), then each part's licence and source: musl under the MIT license, Rich Felker et al. (:2805-2807; its COPYRIGHT, :2869-3064); libfuse under the GNU LGPL 2.1, Miklos Szeredi, its source and type2-runtime's patch carried beside the AppImage in Phobos's releases, with type2-runtime's own source (:2808-2817); squashfuse under its BSD-style licence, Dave Vasilevsky and Phillip Lougher (:2818-2819; :3066-3098); zstd under Zstandard's BSD licence (:2820-2822); zlib under zlib's, Jean-loup Gailly and Mark Adler (:2823-2826); mimalloc under the MIT license, Microsoft Corporation and Daan Leijen (:2827-2828; :3100-3122) |
| libc++, libc++abi, libunwind and compiler-rt (Apache 2.0 with LLVM Exceptions; MIT), by LLVM contributors: LLVM's runtime libraries from the Android NDK, in the app, with compiler-rt in the macOS app too | LICENSE:1837-1902: "libc++ and LLVM's other runtime libraries (the Android NDK's, in the APKs; compiler-rt's also in the macOS app)" (:1838); three of the APKs' native libraries carry libc++ (:1841-1846); "LLVM's libc++abi and libunwind are linked with libc++ into libphobos_android.so and libhook_impl.so, and compiler-rt's builtins are in those, in libdatastore_shared_counter.so, in FFmpeg's libavcodec.so and libavutil.so ... and, from Apple's toolchain, in the macOS app's Phobos and libMoltenVK.dylib" (:1846-1850); libcxx/LICENSE.TXT "puts LLVM's code under the Apache License 2.0, whose text appears above, with the LLVM Exceptions", and its code under LLVM's legacy license "is used here under the MIT license" (:1850-1855); the other three's LICENSE.TXT are libc++'s text, "and their legacy code is used here the same way" (:1856-1859); "Copyright (c) 2009-2014 by the contributors listed in CREDITS.TXT" and compiler-rt's "Copyright (c) 2009-2015" line (:1882-1883) |
| "The full licence for every component is in LICENSE" | LICENSE. #296 ("LICENSE: the notices of the third-party code the builds ship that it lacked") merged on 22 Oct at 00:10 EDT (2026-10-22T04:10:26Z), adding 19 notices, 38 to 57 (its body; docs/handoff.md:44-48 at 062dd53e2). #299 ("LICENSE: LLVM's other runtime libraries under libc++'s notice, and #296's review nits") merged on 22 Oct at 22:51 EDT (2026-10-23T02:51:42Z) and named libc++abi, libunwind and compiler-rt in libc++'s notice (LICENSE:1838, 1846-1859), with "the Open-source licenses screen still shows 58 notices (57 in LICENSE, plus COPYING's)" (its body). The credits are matched to it |
| Phobos's licence text; components keep theirs; firmware not covered by the GPL | README.md:271-274; LICENSE:1-22 |
| How it's made: "I build Phobos with AI coding agents and steer what they work on"; an independent reviewer checks every change since September; claims measured on his RP6 and PSP-1000 | docs/development-process.md:3-48 ("agent-authored"; independent review of the exact snapshot); docs/progress.md:60, 257; the commits' authors (Cursor Agent, Replit Agent) in git. The statement was the owner's choice of 21 Oct ~19:07 **(notes)**; on 23 Oct it went into his voice at his request **(notes)**, with the same claims |
| Disclaimer: no games provided; systems that need a BIOS beyond the firmware ares ships take one from your own hardware | LICENSE:18-22 ("The console firmware that ares ships, compiled into the native library and in the APK's System folder, is not covered by the GPL ... Phobos includes it as upstream ares does"); README.md:173 (Settings → Firmware's Scan Folder identifies each BIOS by content); the claims are the owner's choice of 21 Oct ~19:07 **(notes)**, worded in his voice on 23 Oct |
| Not affiliated with Sony, Nintendo, any other console maker or any game publisher; names, titles and trademarks theirs | True of the project: nothing in the repository or the releases claims otherwise; the site shows publishers' games and logos (the gallery, the 266-game wall), hence "any game publisher" and "what each picture shows" |
| Footer: Phobos comes with no games and isn't affiliated with Sony, Nintendo or any other console maker or game publisher | As for the disclaimer; data/site.json `footer_fine_md` |
| Footer: this site's code, text, data and logo, plus the screenshots and clip of the app's interface, are free under GPL-3.0-or-later, linked to its LICENSE; pictures and clips of games, other people's art in the interface pictures, and trademarks aren't covered and belong to their owners (the same grant and exclusions as before 23 Oct, in looser words) | The owner's decisions of 22 Oct ~01:10 (the code) and 23 Oct ~01:27 (the text, data, logo and the app's own screenshots) **(notes)**; the site's LICENSE, the GNU GPL's text, version 3 (byte for byte gnu.org's gpl-3.0.txt and Phobos's COPYING), and README's Licence section, which names what it covers, the app's pictures by file, says the desktop program's two aren't under it, and gives the "or later"; the other people's art: the games' (MEDIA.md's rows), Google's Material icons, Apache 2.0, in the app's dock, back arrow and theme cards (android/.../ui/MainScaffold.kt:604-606, PhobosScaffold.kt:114 and ThemeGallery.kt:34-36 at master 7986aef5b; LICENSE: the Apache License 2.0's text from :181, its "Used by" at :183-185, Material Icons at :3898-3906), and the Library's console art, BAXY Square's, MIT (LICENSE:3830-3845); the link's address follows the host, as for the site's address below |
| The site's address (canonical links, og:url, og:image, twitter:image, the 404 page's `<base>`) | The owner's choice of host **(notes)**: https://pwnedbygary.github.io/phobos-site/; data/site.json `base_url` |

## Left off the site

- The owner's other words from private chats: quoting them needs his agreement.
- "this repository carries that history from bsnes in August 2010 onward" (docs/progress.md:57), of ares's history:
  this machine's clone is shallow, so it couldn't be checked.
- Argosy among the frontends: v1.1.0's notes name it, but README.md:211-213 says it will work only once its maintainers
  accept Phobos's entry, so the site names ES-DE and Daijisho only.
- Vulkan Memory Allocator and librashader: vendored in thirdparty/ but in no build (nothing outside thirdparty/
  includes `vk_mem_alloc.h` or librashader's headers; #296's handoff entry, docs/handoff.md:110-113, says the same).
- The current desktop interface as "sleek" or "controller-first": not claimed; the site says it's plain today and
  quotes the owner's aim.
- Which round of review a roadmap design is in, and who reviewed what: not stated.
- Any date for the roadmap's items.
- Cut for length on 23 Oct, when the text went into the owner's voice (each still true, its source as before): the
  breadth list of 30 Sep to 3 Oct; desktop-ui, hiro and ruby by name, and the JNI bridge; v1.0.0's stable release
  signing; the homebrew VFPU check and pspdev's hello world of 3 Oct; the frames-per-refresh comparison of 16 Oct;
  #290's cause and its five games; ES-DE and Daijisho by name; #18's 4.76 to 4.15 W; SDL 3 in the desktop chapter;
  the nightly per push in the Builds card; the theme names beyond four, and the HLE's list.

## Noticed while checking (for the repository, not the site)

- #296 merged on 22 Oct (00:10 EDT), and LICENSE now carries the notices of SDL 3, MoltenVK and the AppImage runtime
  and of the code inside them. VMA, librashader, jansson and GLFW need none: none of them is in any build
  (docs/handoff.md:110-113).
- Nightly releases carry only the Android APKs, so the newest desktop build is v2.4.0's.
