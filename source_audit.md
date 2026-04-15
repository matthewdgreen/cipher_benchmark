# Source Audit: Benchmark Data Sources

**Date:** 2026-04-15
**Status:** Initial audit — details to be refined with hands-on exploration

---

## Source 1: DECRYPT / DECODE Database

**URL:** https://de-crypt.org / https://de-crypt.org/decrypt-web
**Maintained by:** Uppsala University (Beata Megyesi et al.) and partners
**Key papers:**
- [The DECODE Database Collection of Historical Ciphers and Keys (2019)](https://ep.liu.se/ecp/158/008/ecp19158008.pdf)
- [The DECODE Database Version 2 (2022)](https://ecp.ep.liu.se/index.php/histocrypt/article/view/397)
- [Decryption of historical manuscripts: the DECRYPT project (2020)](https://www.tandfonline.com/doi/full/10.1080/01611194.2020.1716410)

### What it contains
- **10,106 total records** (as of current web interface)
- **6,396 keys**, **3,692 ciphers**, **1,124 transcription pages**
- Primarily early modern European diplomatic/military correspondence
- Covers a wide range of cipher types: simple substitution, homophonic substitution, nomenclators, etc.
- Rich metadata per record: provenance, location, date, cipher type, symbol set, code length, key properties (20+ fields)

### What's available per record
- **Images:** Digitized images of ciphertexts and keys are included for some records (not all). Many images come from external archives (Vatican Secret Archives, national archives, etc.)
- **Transcriptions:** Computer-readable transcriptions exist for a subset (1,124 transcription pages noted)
- **Plaintext/solutions:** The database tracks decryption status explicitly with four values:
  - `Decrypted`
  - `Non-decrypted`
  - `Partially decrypted`
  - `N/A`
- **Keys:** 6,396 key records, linked to cipher records where applicable

### Access model
- **Web interface:** Public, no account required for browsing
- **REST API:** Referenced in the web app configuration (`api/` endpoint), but no public API documentation found
- **Export:** The web interface offers export to CSV, Excel, HTML, PDF, XML
- **Bulk download:** No dedicated bulk download mechanism found; export from web interface may be limited
- **Authentication:** JWT tokens mentioned in config, suggesting some API features may require auth

### Rights / licensing
- **Source code:** Apache License v2.0
- **Database:** Separate "special terms and conditions" — NOT Apache-licensed
- **Images:** Rights are complex. Many images originate from external archives (Vatican, national libraries) and the DECODE database may not hold redistribution rights for those images
- **Citation requirement:** Must cite the DECODE database papers if used in research

### API findings (2026-04-15)

The DECODE REST API is accessible at `https://de-crypt.org/decrypt-web/api/`. Key endpoints:
- `api/list/Records` — list/search records with query parameters
- `api/view/Records/{id}` — view single record detail
- Supports pagination: `start`, `recperpage` params
- Filter by field: `x_status=1`, `x_record_type=1`, etc.
- **No authentication required** for read access

**Status code mapping** (confirmed from web app source):
| Code | Label | Record count |
|---|---|---|
| 1 | Decrypted | 1,378 (1,359 ciphers + 19 keys) |
| 2 | Non-decrypted | 806 |
| 3 | Partially decrypted | 385 |
| 4 | N/A | 7,082 |

**Critical finding: DECODE is a metadata catalog, not a data repository.** Individual record API responses contain rich metadata (provenance, cipher type, symbol sets, language, dates) but **no image URLs, no transcription text, no plaintext data**. Images are hosted by source archives, not by DECODE. Most records note: "The image is not in the public domain."

### Bulk export results (2026-04-15)

Exported all 1,400 decrypted cipher records via the API. CSV saved to `data_staging/decode_decrypted_ciphers.csv`.

**Language distribution (plaintext language of decrypted ciphers):**
| Language | Records |
|---|---|
| French | 513 |
| English | 252 |
| Spanish | 171 |
| Italian | 171 |
| Unknown | 121 |
| Hungarian | 82 |
| Dutch | 48 |
| Latin | 9 |
| German | 9 |
| Other | 24 |

**Top holding archives:**
| City | Records | Archive |
|---|---|---|
| London | 455 | British Library / TNA |
| Paris | 343 | BnF / Archives Nationales |
| Budapest | 177 | Hungarian National Archives |
| Madrid | 98 | BRAH / AHN |
| The Hague | 69 | Nationaal Archief NL |
| Kew | 62 | The National Archives UK |
| Naples | 50 | Archivio di Stato di Napoli |
| Milano | 26 | Various |
| Venice | 19 | Various |
| Simancas | 16 | Archivo General de Simancas |
| München | 16 | Various |
| Vienna | 16 | Various |
| New Haven | 15 | Yale (Beinecke?) |

### Realistic yield estimate (updated with API data)
- **1,359 decrypted cipher records** in the database — far more than initially expected
- **However:** records are metadata-only. No images or text data are served through the database itself
- **To get actual benchmark data**, we would need to:
  1. Use DECODE metadata to identify solved records
  2. Access source archives independently for images
  3. Obtain or create transcriptions and plaintext separately
- **Estimated usable for open release:** Still low (10–50) — image rights remain the bottleneck
- **Estimated usable for linked release:** 100–500+ (link to DECODE record + source archive)
- **Best path:** Focus on records from archives with permissive digital access (e.g., some Spanish national archives have open digitization programs)

### HistoCrypt shared tasks (high-priority sub-source)
The DECRYPT project ran shared tasks at the HistoCrypt conferences (2020, 2021, 2022) where curated subsets of ciphers were distributed to participants with paired ciphertext transcriptions and plaintext solutions. These are the **most benchmark-ready subsets** in the entire DECRYPT ecosystem — estimated 50–100 well-paired records with transcriptions and solutions already aligned. The shared task data may be available from HistoCrypt organizers or through the Linkoping University Electronic Press (which publishes HistoCrypt proceedings).

### CrypTool connection
The CrypTool project (https://www.cryptool.org, GitHub: https://github.com/CrypToolProject) collaborated with DECRYPT and may have additional structured data, tools, or curated cipher examples worth investigating.

### Next steps (updated after API exploration)
1. ~~Use the web interface to filter records by `Decrypted` status and export to CSV~~ **DONE** — API provides this directly
2. ~~Test the API endpoint for programmatic access~~ **DONE** — API works without auth
3. **Write a script to bulk-export all 1,359 decrypted cipher records** via the API with full metadata
4. **Cross-reference decrypted records with archives that have open digital access** — identify which source archives provide freely accessible digitized images
5. Review the "special terms and conditions" in detail
6. **Investigate HistoCrypt shared task datasets** — contact organizers or check HistoCrypt proceedings for download links
7. **Contact Beata Megyesi's team** at Uppsala about bulk access and licensing for benchmark use
8. Check CrypTool project repositories for additional structured cipher data
9. **Sample 5–10 decrypted records from different archives** — check source archive websites for image availability

---

## Source 2: HCPortal (Portal of Historical Ciphers)

**URL:** https://hcportal.eu / https://crypto.hcportal.eu
**Maintained by:** Slovak University of Technology in Bratislava (Eugen Antal et al.)
**Key papers:**
- [HCPortal Overview (HistoCrypt 2020)](https://ep.liu.se/ecp/171/003/ecp2020_171_003.pdf)
- [HCPortal Modules for Teaching and Promoting Cryptology](https://ecp.ep.liu.se/index.php/histocrypt/article/view/151)

### What it contains
- **Database of cryptograms** — ~763 records as of 2021 publication; likely more now
- **Database of cipher keys** — 319 cipher keys across 5 languages and 3 archives
- **Cryptologists database** — biographical records
- **ML datasets** — machine learning datasets (details unknown)
- In 2025, the cryptograms and keys databases were merged into a unified interface at crypto.hcportal.eu

### What's available per record
- Unknown in detail — the main app is a JavaScript SPA that couldn't be fetched for inspection
- The portal emphasizes visualization and search capabilities
- Full-text search and advanced filtering (by location, language, sender, etc.)
- Unclear whether records include actual images, transcriptions, or plaintext solutions

### Access model
- **Web interface:** Public, free access ("We support free access to information")
- **Public API:** Confirmed — both cryptograms and cipher keys databases are accessible via public API
- **API documentation:** Was at `cryptograms.hcportal.eu/api/apidoc/` (returned 404 during audit — may have moved with the 2025 database merger)
- **ManuLab API:** A separate framework accessible via PHP scripts, documentation reportedly available

### Relationship to DECRYPT/DECODE
- HCPortal is a **separate, independent project** from DECRYPT/DECODE
- Built by Slovak researchers vs. Uppsala/Swedish team
- There may be some overlap in records (both catalog European historical ciphers) but they are distinct databases
- Potential for complementary coverage

### Rights / licensing
- "We support free access to information" — but no explicit license statement found
- Need to verify whether data can be redistributed or only accessed via the portal

### Realistic yield estimate
- **Highly uncertain** — the JavaScript-rendered interface prevented inspection of actual data
- ~763+ cryptogram records, but unknown how many have images, transcriptions, and solutions
- The cipher keys database (319 keys) is promising — keys paired with solved ciphertexts could be valuable
- **Estimated usable records:** Cannot estimate without hands-on exploration
- **Action needed:** Manual exploration of the web interface and API is required

### Next steps
1. Manually browse crypto.hcportal.eu to understand record structure and data availability
2. Locate the current API documentation (may have moved from the old URL)
3. Check whether records include downloadable images and transcriptions
4. Assess overlap with DECRYPT/DECODE records
5. Contact Eugen Antal's team if API docs are unavailable

---

## Source 3: ICDAR Historical Cipher Handwriting Competition & Related Datasets

**Competition URL:** https://rrc.cvc.uab.es/?ch=27 (Robust Reading Competition platform)
**Key paper:** [ICDAR 2024 Competition on Handwriting Recognition of Historical Ciphers (Springer)](https://link.springer.com/chapter/10.1007/978-3-031-70552-6_20)
**Research groups:** Beata Megyesi (Uppsala), Alicia Fornes & Mohamed Ali Souibgui (CVC Barcelona)

### What it contains

**ICDAR 2024 HR-Ciphers competition dataset:**
- **~600 pages** of historical cipher manuscripts, segmented into text lines with manual transcriptions
- Two categories:

**Ciphers with digits:**
- Documents from the Vatican Secret Archive, multiple centuries
- 76 different symbols, primarily digits with diacritics

**Ciphers with symbol alphabets:**
- **Borg cipher** (17th century): 34 symbols, graphic signs + Latin letters, plaintext in Latin
- **Copiale cipher** (mid-18th century): ~100 symbols across 105 pages, plaintext in German
- **BnF documents** (16th century): French noble correspondence, plaintext in French
- **Ramanacoil manuscript** (1674): from National Archives of the Netherlands

**Related datasets from the same research ecosystem:**
- **Copiale cipher dataset:** The single most valuable item — 105 pages, ~75,000 characters, fully deciphered by Knight, Megyesi & Schaefer (2011). Both transcription and German plaintext are published. Spans all 3 benchmark tracks.
- **Borg cipher dataset:** ~16 annotated pages with symbol-level bounding boxes, ~100+ distinct symbol classes. Partially deciphered.
- **CVC Barcelona symbol datasets:** Cropped symbol images with class labels and bounding boxes from multiple cipher manuscripts. Used for few-shot symbol recognition research. Published by Fornes, Souibgui et al.

### What's available per record
- **Images:** Line-segmented images of cipher text (competition dataset); page-level scans exist for Copiale and Borg
- **Ground truth:** Manual transcriptions (symbol-level) — competition ground truth is **transcriptions of cipher symbols, NOT plaintext decryptions**
- **Plaintext/solutions:** Not in the competition dataset itself, but published separately for key manuscripts:
  - Copiale: full plaintext published (Knight, Megyesi, Schaefer 2011)
  - Borg: partial solutions in published literature
  - Vatican/BnF: varies by document
- **Format:** Each text line image has a corresponding transcription file

### Access model
- **ICDAR competition:** Hosted on RRC platform, registration likely required for download. Training data released January 2024.
- **Copiale/Borg datasets:** Shared through research publications and upon request to authors. Some may be on Zenodo.
- **CVC datasets:** Some shared via CVC website or on request to Fornes et al.

### Rights / licensing
- **ICDAR competition:** Specific license terms not found. ICDAR competitions typically require post-competition dataset release. Organizers may have secured redistribution rights.
- **Copiale images:** Held by a private collection; high-res scans made available for research, but redistribution rights unclear.
- **Borg/Vatican images:** Vatican archives have strict reproduction rules — likely restricted for redistribution.
- **CVC datasets:** Varies; some are research-use-only.
- **Zenodo deposits:** When deposited, typically CC-BY or similar. Search for "cipher handwriting", "DECRYPT cipher", "Copiale".

### Relevance to our benchmark
- **Track A (Image → Transcription):** Directly relevant — this is exactly what the ICDAR competition measures
- **Track B (Transcription → Plaintext):** Relevant for manuscripts with known solutions (primarily Copiale)
- **Track C (Image → Plaintext):** Relevant for Copiale; requires combining images with separately-sourced solutions for others

### Realistic yield estimate
- **Track A only:** Up to ~600 pages from the competition dataset (line-segmented); 10–25 page-level records from curated Copiale/Borg datasets
- **All 3 tracks (need images + transcription + plaintext):** 10–20 records, primarily from the Copiale cipher
- **Open release:** 5–15 records depending on image rights clearance
- **Linked release:** 20–30+ if linking to archive-hosted images
- **Main blocker:** Image redistribution rights from source archives

### Key references
- Knight, Megyesi, Schaefer (2011). "The Copiale Cipher." Workshop on Building and Using Comparable Corpora.
- Souibgui, Fornes et al. (2021). "A Few-shot Learning Approach for Historical Ciphered Manuscript Recognition."
- Souibgui, Fornes et al. (2022). "Text line recognition of historical ciphered manuscripts." Pattern Recognition.
- Barrere, Souibgui, Fornes, Megyesi (2022–2023). Transformer-based HTR for ciphers. ICDAR proceedings.

### Next steps
1. Register on the RRC platform and attempt to download the ICDAR 2024 competition dataset
2. Search Zenodo for existing data deposits: "Copiale cipher", "DECRYPT", "cipher handwriting"
3. Contact Fornes/Souibgui at CVC Barcelona about their symbol datasets and licensing
4. Verify Copiale image redistribution rights
5. For each manuscript in the competition dataset, check whether a published decryption/plaintext exists
6. Assess whether line-segmented format can be adapted to page-level (our benchmark unit)
7. Check for ICDAR 2025 cipher competition — may have additional data

---

## High-Priority Single Source: Copiale Cipher (data acquired 2026-04-15)

**Source URL:** https://www.su.se/english/research/research-catalogue/research-projects/d/decipherment-of-historical-manuscripts/the-copiale-cipher
**Paper:** Knight, Megyesi, Schaefer (2011). "The Copiale Cipher." ACL Workshop. https://aclanthology.org/W11-1202/
**Local staging:** `data_staging/copiale/`

### What we have

All files downloaded from Stockholm University:

| File | Size | Description |
|---|---|---|
| `copiale-transcription.txt` | 237 KB | Symbol-level transcription, ASCII-encoded, page-delimited |
| `copiale-deciphered.txt` | 87 KB | German plaintext decipherment, page-delimited |
| `copiale-translation.txt` | 79 KB | English translation, page-delimited |
| `copiale-manuscript-part1.pdf` | 13 MB | Manuscript images, pages 1–~52 |
| `copiale-manuscript-part2.pdf` | 12 MB | Manuscript images, pages ~53–105 |
| `copiale-paper.pdf` | 436 KB | Knight/Megyesi/Schaefer paper |

### Data quality assessment

- **105 pages** total in the manuscript
- **102 pages** have aligned transcription + German decipherment (pages 19, 33, 46, 100 missing from both; transcription additionally missing pages 32, 55, 92)
- **~98 pages** with full three-way alignment (transcription + decipherment + translation)
- **Transcription format:** Space-separated ASCII tokens representing cipher symbols (e.g., `L i t : m z grr bar b l`). Includes 11 documented logograms (`*o*` = society, `*star*` = secret, etc.)
- **Page boundaries:** Clearly marked with `## PAGE N` in all three files
- **Cipher type:** Homophonic substitution with nomenclator elements (secret society initiation ritual)
- **Plaintext language:** German
- **~100 distinct symbol classes** in the cipher alphabet

### Benchmark value
- **Track A:** Excellent — manuscript images + symbol transcription ground truth for ~100 pages
- **Track B:** Excellent — symbol transcription + German plaintext for ~100 pages
- **Track C:** Excellent — manuscript images + German plaintext for ~100 pages
- **This single source could provide 30–50% of the MVP benchmark** if images can be extracted from the PDFs at page level

### Rights status
- **Manuscript images:** Held by a private collection. High-resolution scans hosted on Stockholm University website for research. **Redistribution rights: UNCLEAR — needs verification.** May need to be linked-only.
- **Transcription + plaintext:** Created by the research team (Knight, Megyesi, Schaefer). Likely redistributable under academic terms. Published as supplementary data with an ACL paper.
- **Risk:** If images can't be redistributed, Tracks A and C would be linked-only, but Track B (transcription→plaintext) could still be open release.

### Next steps for Copiale
1. **Extract individual page images** from the manuscript PDFs
2. **Verify page alignment** between extracted images and transcription/plaintext page markers
3. **Contact Megyesi's team** to clarify redistribution rights for images
4. **Parse the transcription format** — document the symbol inventory and verify against the paper
5. **Create benchmark records** for 10 pilot pages spanning different sections of the manuscript

---

## Source comparison summary

| Factor | DECRYPT/DECODE | HCPortal | ICDAR HR-Ciphers | Copiale (standalone) |
|---|---|---|---|---|
| Total records | ~10,100 (1,359 decrypted) | ~763+ | ~600 pages | ~100 pages |
| Images available | Metadata only (external) | Unknown | Yes (line-segmented) | Yes (PDF, needs extraction) |
| Transcriptions | ~1,124 pages (not in API) | Unknown | Yes (all pages) | Yes (all pages) |
| Plaintext/solutions | 1,359 marked Decrypted | Unknown | Not directly | Yes (German + English) |
| API access | Yes (REST, no auth) | Yes (public) | RRC platform | Direct download |
| Redistribution rights | Special terms (unclear) | "Free access" (vague) | Unclear | Images unclear; text likely OK |
| Best for tracks | Metadata/discovery | TBD | A (transcription) | All three tracks |
| Estimated MVP yield | 10–50 open / 100–500 linked | Unknown | 10–20 all tracks | 30–50 pages all tracks |

---

## Recommended collection strategy

### Phase 1: DECRYPT/DECODE (primary source)
- Highest priority: largest database, tracks solved status, has metadata and export
- Filter by `Decrypted` status, then check for image + transcription availability
- Rights are the main risk — plan for linked-only release for most records

### Phase 2: ICDAR dataset (Track A anchor)
- Best source for image→transcription ground truth
- Supplement with published plaintext for manuscripts with known solutions
- Line-to-page conversion may be needed

### Phase 3: HCPortal (supplementary)
- Requires manual exploration before commitment
- Public API is promising if documentation can be located
- May offer records not in DECRYPT

### Phase 4: Additional sources to investigate
- **HistoCrypt shared tasks (2020–2022):** Curated challenge datasets from the DECRYPT project with paired transcriptions and solutions — likely the single fastest path to benchmark-ready records
- **CrypTool project:** Collaborated with DECRYPT; may have additional structured data (https://www.cryptool.org, https://github.com/CrypToolProject)
- **NCID / ACA synthetic ciphers:** See Source 4 below
- **Friedman collection (NSA):** Some declassified historical cipher material
- **Published scholarship:** Individual papers solving specific historical ciphers often include images and solutions
- **Wikimedia Commons:** Some historical cipher manuscripts are public domain

---

## Source 4: NCID / CrypTool Synthetic Cipher Data

**URL:** https://github.com/ernstleierzopf/ncid / https://www.cryptool.org/en/cto/ncid/
**Key paper:** [Detection of Classical Cipher Types with Feature-Learning Approaches (2021)](https://link.springer.com/chapter/10.1007/978-981-16-8531-6_11)

### What it contains
- The Neural Cipher Identifier (NCID) project generated a **massive synthetic dataset** for training cipher type classifiers
- **10 million generated ciphertext records** across **55 ACA (American Cryptogram Association) standard cipher types**
- Cipher types include: Vigenere, Beaufort, Playfair, bifid, homophonic, foursquare, and many more
- Ciphertexts generated from Gutenberg library plaintext, in two lengths: exactly 100 characters or variable 51–428 characters
- **82.78% classification accuracy** achieved with ensemble models

### Relevance to our benchmark
- These are **synthetic, not historical** — explicitly separated from the core real-world benchmark per our plan
- Useful as a **control set / sanity check**: if a tool can't crack synthetic Vigenere, there's no point testing it on real nomenclators
- The 55 ACA cipher types provide good coverage of classical cipher families
- Source code on GitHub allows regenerating ciphertexts with different parameters

### Access and licensing
- GitHub repo: https://github.com/ernstleierzopf/ncid (open source)
- CrypTool project: https://www.cryptool.org (free educational software)
- Generated data is reproducible from public-domain Gutenberg texts

### Realistic yield for our benchmark
- **Not for the core benchmark** (synthetic data excluded per plan)
- Could provide an **unlimited synthetic control set** for Track B (transcription→plaintext)
- No images, so not relevant for Tracks A or C

### Next steps
1. Clone the NCID repo and review the cipher generation pipeline
2. Assess whether we want a small curated synthetic control set (e.g., 100–200 examples across key cipher families)
3. Determine which ACA cipher types overlap with historical cipher families in our real-world set

---

## Zenodo search results

A systematic search of Zenodo for historical cipher datasets yielded **no directly usable deposits**. Searches for "Copiale cipher", "DECRYPT cipher", "cipher handwriting", "historical ciphers dataset", and "nomenclator dataset" returned no relevant results. This suggests:

- The DECRYPT project has not deposited curated datasets on Zenodo (or they are under different keywords)
- The ICDAR competition data is hosted on the RRC platform, not Zenodo
- CVC Barcelona's cipher symbol datasets may be shared directly rather than through public repositories

This is a significant finding: **there is no readily downloadable, well-packaged historical cipher benchmark dataset on major data repositories.** This validates the need for this project.

---

## Archive Digital Access & Rights Analysis

Based on the 1,400 decrypted cipher records in DECODE, the top holding archives and their digital access status:

| Archive City | Records | Archive | Digital Access | Image Rights for Benchmark |
|---|---|---|---|---|
| London | 455 | British Library / TNA | BL: CC0 for public domain digitizations. TNA: Crown copyright waived for most; £40 fee for open-access web publication of up to 20 images | **Promising** — BL has strong open-access stance |
| Paris | 343 | BnF / Archives Nationales | BnF/Gallica: Free non-commercial reuse with attribution ("Source gallica.bnf.fr / BnF"). Commercial needs license | **Good for linked-only**, possibly open with attribution |
| Budapest | 177 | Hungarian National Archives | Unknown — needs investigation | **Unknown** |
| Madrid | 98 | BRAH / AHN | Varies by institution. PARES portal provides free access but redistribution requires archive permission + possible fees | **Linked-only likely** |
| The Hague | 69 | Nationaal Archief NL | Generally open access for public domain materials | **Needs investigation** |
| Kew | 62 | The National Archives UK | Crown copyright waived/expired; £40 fee for open-access web use up to 20 images | **Promising** — but fee-based for web publication |
| Naples | 50 | Archivio di Stato di Napoli | Unknown — needs investigation | **Unknown** |
| Simancas | 16 | Archivo General de Simancas | PARES portal: free access, but must contact archive before redistribution. May require fees per Law 37/2007 | **Linked-only likely** |
| New Haven | 15 | Yale (Beinecke?) | Yale generally allows scholarly use of public domain items | **Needs investigation** |

### British Library digital access findings (2026-04-15)
- BL uses **IIIF** for digitised manuscripts, served via Universal Viewer at `bl.digirati.io`
- Searching the BL Archives & Manuscripts Catalogue for "cipher" with digitised=Yes returns **5 digitised items** out of 26 cipher-related manuscripts, including:
  - **Add MS 11252**: King Charles I letters with cipher keys (1646–1681) — confirmed digitised (July 2020–Jan 2021 batch)
  - **Add MS 18980**: Royalist correspondence with cipher (1642–1643)
  - **Sloane MS 3188**: John Dee's conferences with angels (1581–1693)
- **BL catalogue supports "Language: Cipher" filter** — 43 cipher-tagged manuscripts have been digitised:
  - **7 currently viewable** (free, IIIF):
    1. Cotton MS Caligula B VII (England/Scotland papers, 1525–1556)
    2. Cotton MS Caligula C I (England/Scotland, 1567–1570)
    3. Cotton MS Caligula C II (Mary Queen of Scots cipher letter, 1569–1572)
    4. Cotton MS Caligula C III (England/Scotland, 1568–1585)
    5. Cotton MS Vespasian C IV (England/Spain, 1527–1529)
    6. IOR/E/3/16 (East India Company, 1637–1639)
    7. IOR/R/15/1/134 f 32 (cipher letter, 1852)
  - **36 temporarily offline** due to 2023 Rhysida ransomware attack — including Thurloe State Papers (Add MS 4157–4159), Charles I cipher keys (Add MS 11252), Walsingham letter-book (Harley MS 260), and more. ~1,000 manuscripts were restored in Oct 2024; remainder ongoing.
- **IIIF API pattern:** `https://bl.digirati.io/iiif/ark:/81055/{ark_id}/manifest.json`
- **Download tool:** https://github.com/balta2ar/manuscript-dl can download from IIIF sources including BL
- **License:** BL does not claim new copyright on digitizations of public domain works. Reuse terms vary per item — non-commercial use generally permitted. UK law treats unpublished manuscripts (even medieval ones) as copyright-protected, complicating open licensing.
- **TNA (Kew) State Papers:** Cipher images mostly behind Gale/Cengage paywall (State Papers Online, subscription ~£200K institutional). Individual images £38.75 via TNA Image Library. Free physical access with reader's ticket.
- **Realistic assessment:** Of 455 London-held DECODE records, 7 BL manuscripts are currently viewable online, 36 more will return post-recovery. Many DECODE records may reference folios within larger volumes not tagged as "Cipher" in BL. TNA records are largely paywalled. **Short-term yield: 5–15 records from the 7 available manuscripts. Medium-term: 30–50+ as BL restores access.**

### Key takeaways for rights strategy
1. **British Library (455 records)** is the most promising for open release — CC0 policy for public domain digitizations, but access currently limited by cyber-attack recovery
2. **BnF/Gallica (343 records)** allows free non-commercial reuse with attribution — viable for an academic benchmark
3. **TNA Kew (62 records)** — Crown copyright waived, but web publication has a small fee
4. **Spanish archives (114 records)** — free access via PARES but redistribution is restricted
5. **Budapest, Naples, The Hague** — need separate investigation
6. The **linked-only release** strategy from the plan is well-justified — most archives allow access but not redistribution

### Estimated open-release yield by archive
- British Library: 20–50 records (if images are on Gallica/BL viewer and public domain)
- BnF: 10–30 records (with attribution, non-commercial)
- Others: case-by-case

**Total estimated open-release yield from DECODE metadata + archive images: 30–80 records** (if we can match DECODE records to digitized images at source archives)

---

## Open questions

1. What exactly are the DECODE database "special terms and conditions"?
2. Can we get programmatic access to DECODE's API, or is export-from-web-interface the only option?
3. What is the current state of HCPortal's API after the 2025 database merger?
4. What are the ICDAR competition dataset's redistribution terms?
5. How many DECODE records have status `Decrypted` AND have associated images AND transcriptions?
6. Do HistoCrypt shared tasks have downloadable datasets, or were they distributed only to participants?
7. Can we contact Megyesi (Uppsala) and Fornes (CVC Barcelona) to negotiate benchmark data access?
8. Should we investigate the Copiale cipher independently as a well-documented single-source anchor for the benchmark?
