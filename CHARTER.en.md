# Charter for Finding Applications of 722 AI Mathematics Manuscripts

Project: **MathWeave** · [GitHub](https://github.com/yiduo/mathweave)

October 20, 2026 · @email4u

English translation prepared October 22, 2026. The [Chinese original](722篇AI数学论文应用价值挖掘纲领.md) remains unchanged. This document translates the program and its targets; it is not a claim that those targets have been achieved. The original heading “Six principles” contains eight numbered principles, all preserved below. The original embedded illustration was unavailable and is represented by its caption.

**Corpus note.** The charter uses the historical count of 722 manuscripts. At the project's pinned upstream revision, reconciliation records 719 current manuscripts in 372 result families. See [current progress](PROGRESS.en.md) for the distinction between catalogue coverage, actual reading, decomposition drafts, completed research, and reviewed results. This repository references [OpenAI's official math repository](https://github.com/openai/math); it does not redistribute its `math/` directory.

## 1. Purpose

This charter guides an AI agent system that connects OpenAI's 722 publicly released mathematics manuscripts, grouped into 372 result families, with relevant historical literature. The system will systematically identify possible applications and develop each lead far enough for a person to test it.

**Why do this?** The uses of mathematics are rarely predictable in advance. Conic sections waited roughly 1,800 years before explaining planetary orbits; Boolean algebra waited around 80 years before becoming a foundation of circuit design; number theory became central to public-key cryptography more than three decades after being described as something that would never be used in war. These results were released to demonstrate capability. Their application value is likely underestimated.

**Three starting judgments:**

1. **Public results form a portfolio of options.** Any individual paper has a low probability of finding an application, but the expected value of hundreds together can be high. That value accrues to those best able to find uses, rather than necessarily to those who publish the results.
2. **Value lies in connections.** A result's usefulness often appears only when connected to decades of earlier methods, problems in other disciplines, and current engineering bottlenecks. The unit of research is therefore a network of “result family + historical lineage + application problem,” rather than an isolated paper.
3. **A lead matters only if it can be tested.** Every application hypothesis must specify how a person or program could judge it true or false. An idea without a test is inspiration, not a deliverable.

**Phase-one objective, over 12 weeks:** structurally decompose all 372 families, establish their historical lineages, produce at least 100 application cards with preliminary checks, and advance at least 10 to prototypes or numerical validation.

## 2. Scope and principles

### Sources to investigate

- **Core corpus:** 722 manuscripts and 372 result families in `openai/math`, approximately 4,000 proposed problems, some Lean formalizations, and reasoning summaries for 10 families.
- **Historical corpus:** classical results improved upon or addressed by each family, using arXiv, zbMATH, MathSciNet, Mathlib, textbooks, and surveys.
- **Application corpus:** open engineering and scientific problems, surveys, benchmarks, and industrial requirements in areas including communications and coding, cryptography, optimization and scheduling, materials and quantum physics, plasma and fluid simulation, machine learning theory, and formal verification.

### Exclusions

- **No expansion of mathematical knowledge as a phase-one objective.** The project seeks applications within existing results and historical literature. New mathematical questions discovered along the way are recorded, without pursuing their proofs or completing the theory.
- Do not claim new mathematical theorems or replace peer review.
- Do not put unverified mathematical conclusions directly into engineering systems.
- Route sensitive leads, including cryptanalysis and critical infrastructure, to a controlled process rather than developing them in the public workflow.

### Six principles

1. **Favor imagination over caution.** Historically valuable connections often appeared strained at first: the Radon transform and medical imaging, number theory and network security, Riemannian geometry and satellite positioning. Encourage distant analogies, interdisciplinary associations, and bold conjectures. Generate a hundred extra ideas rather than miss one valuable connection.
2. **Admit broadly; reject slowly.** Retain any connection with a plausible explanation. Rejection requires a concrete reason: a mathematical contradiction, adverse experimental evidence, or assumptions that fail in the target domain. “Too distant,” “not useful yet,” and “no precedent” are insufficient.
3. **Validate before adoption.** The charter notes three withdrawn papers involving sign errors or mismatches between natural-language and Lean statements. Lean establishes a formal proposition, but does not establish that it is the proposition the paper intended. Credibility determines how far a lead may advance, not whether it may be proposed and retained.
4. **Make every conclusion traceable.** Attach a source chain identifying the manuscript, proposition, and historical dependencies. References must be accessible for inspection.
5. **Use external judges rather than model self-assessment.** Numerical experiments, simulations, benchmarks, or domain experts decide application hypotheses; the generating model does not grade its own claims.
6. **Keep human and AI responsibilities explicit.** AI performs broad exploration, decomposition, and imaginative association. People set direction, review specifications, and take responsibility for conclusions advanced to pilots.
7. **Cross-check with multiple model providers.** At least two different providers independently perform key steps, reducing shared blind spots and offering different associations.
8. **Retain unconfirmed connections.** Untestable and unsuccessful connections belong in the knowledge base with their reasons. They map the terrain for later work and may become useful when conditions change.

## 3. Architecture

*Original illustration caption: a six-stage pipeline operates on one shared knowledge graph; human gates sit between mapping, testing, and translation into practice.*

The system has three parts: a shared knowledge graph, a six-stage pipeline, and agents with distinct responsibilities. The graph is the single source of recorded facts. Each stage reads from and writes to it; conclusions are not passed informally between agents.

The first three stages can run with substantial automated parallelism. Human gates begin at stage four. Their purpose is to **classify and route** leads, determining pace and next steps rather than deleting them. A skeptic agent works independently of the lead-generating agent to find counterexamples and gaps. Its objections accompany each card, but carry no unilateral veto.

## 4. The six stages

### Stage 1: Parse and decompose

- **Input:** all manuscripts, Lean code, and available reasoning summaries for one result family.
- **Action:** extract five types of component from each manuscript: main propositions in natural and formal language; key lemmas; proof methods; newly introduced tools or constructions; and explicit constants and bounds. Record assumptions and scope.
- **Check:** compare natural-language and Lean statements individually. Flag mismatches for human review.
- **Output:** a structured family record in the graph.

### Stage 2: Reconstruct historical lineage

- **Trace predecessors:** whose result is improved? What were the old and new bounds? Who first posed the problem, in what context, and to address what practical concern?
- **Trace uses:** which fields depend on the problem or method? Where have earlier results been applied? Could the new result replace an old one to tighten a bound or accelerate an algorithm?
- **Connect across the corpus:** identify repeated methods, objects, and constants across the 722 manuscripts, and form thematic clusters.
- **Output:** a lineage graph for each family. Highlight “an earlier result is already used; the new result could directly upgrade it,” a promising route to practical adoption.

### Stage 3: Extract transferable methods

Describe proof techniques as components in language independent of their original field: their inputs, outputs, and conditions.

Distinguish three types: **usable conclusion**, where the theorem supplies an engineering bound; **usable method**, where a proof technique transfers to another problem; and **usable construction**, where a constructed code, graph, algorithm, or other object is itself useful.

**Output:** a component library with sources and applicability conditions.

### Stage 4: Map across domains

- **Structural matching:** express engineering problems as the same “input–output–conditions” contracts and find matching or similar structures.
- **Equation and object matching:** recognize the same equations, random structures, and optimization problems under different disciplinary names.
- **Reverse search:** start with an engineering bottleneck and ask which improved bound or construction would relieve it, then search the graph.
- **Distant association:** deliberately place a family into 10 unrelated fields, such as biology, finance, transportation, energy, language, and art. Describe what usefulness there might look like, then retain plausible mappings.
- **Combination:** combine methods from two or three families and ask what they could solve together that none could solve alone.
- **Classify by imaginative distance:** near analogy means a similar problem in another setting; distant analogy means similar structure across remote disciplines; bold conjecture means a vague but plausible intuition. Retain all three and route them to suitable tests rather than filtering by initial credibility.
- **Output:** candidate connections specifying their mapping, additional assumptions, and analogy class. The first human gate classifies and supplements them; “too strained” alone is not a reason to delete a lead.

### Stage 5: Form and test application hypotheses

Write a falsifiable prediction where possible: “Applying X to Y should improve metric Z by this amount.” For a bold conjecture that cannot yet be quantified, specify what would be needed to falsify it.

Assign an external judge: a numerical experiment, simulation, public benchmark, existing dataset, or domain expert. Prioritize small tests that can be completed within a week, while retaining leads that cannot yet be tested.

A skeptic independently searches for counterexamples, hidden assumptions, and adverse literature. An advocate develops the strongest supporting case. Attach both views side by side.

Classify outcomes as:

- **Supported:** external evidence supports the prediction; advance to stage six.
- **Pending:** testing is unavailable or evidence is insufficient; retain and revisit.
- **Observation:** the present test is adverse, but a different setting or changed conditions may justify another attempt.
- **Rejected:** an explicit mathematical contradiction or adverse experimental result supports rejection; archive the reason while keeping the lead searchable.

Only formal rejection requires signatures from at least two reviewers. Pending and observation records need no approval to remain in the knowledge base.

### Stage 6: Rank and translate into practice

Rank leads by “impact × feasibility × time to adoption × credibility.” Find appropriate industry partners for leading candidates and prepare pilot proposals. Route sensitive directions to the controlled process.

Review quarterly which connections succeed and which produce noise, then adjust stage-four matching strategies.

## 5. Initial seed hypotheses

These human-proposed seeds calibrate exploration quality. The system should independently rediscover most of them and identify connections beyond the list. **Every entry below is an untested hypothesis.**

| Result area | Historical predecessor | Possible application | Distance |
| --- | --- | --- | --- |
| Mézard–Parisi diluted spin glasses, F221 | Cavity method; random constraint satisfaction | LDPC decoding thresholds; random SAT difficulty transitions | Near |
| NP-hardness at SDP thresholds, F102 | Goemans–Williamson approximation; Unique Games Conjecture | Approximation limits in chip placement, power-grid partitioning, and logistics | Near |
| Three-dimensional relativistic Vlasov–Maxwell, F362 | Glassey–Strauss global existence framework | Reliability and numerical schemes for fusion plasma and space-weather simulation | Intermediate |
| Free group factors, F287 | Voiculescu's free probability | Large MIMO communication; spectra of neural-network weight matrices | Intermediate |
| Spontaneous magnetization in quantum Heisenberg ferromagnets, F271 | Dyson–Lieb–Simon reflection positivity | Phase transitions in quantum materials and hardware; simulator benchmarks | Intermediate |
| Quasipolynomial arithmetic-progression bounds, F159; multiplicative-function correlations, F007 | Szemerédi, Behrend, Kelley–Meka | Derived pseudorandomness tools for complexity and random-generator testing | Intermediate |
| Mahler conjecture, lattices, convex bodies, F087 | Geometry of numbers; Minkowski | Lattice-cryptography parameter assessment; **sensitive, controlled routing only** | Intermediate |
| Sphere packing, spherical codes, binary-code bounds | Shannon; Delsarte linear-programming bounds | Communication constellations, quantization, vector retrieval | Near |
| Irrationality measure of π, F017; zero-free regions of ζ | Diophantine approximation; prime number theorem | High-precision computation and prime-distribution error bounds; limited direct use | Distant |
| Hodge conjecture for CM abelian varieties | Deligne; period theory | String-theory compactification; theoretical foundations of isogeny cryptography | Distant |
| Lean formalizations throughout the corpus | Mathlib; history of theorem-prover engineering | Formal verification libraries for chips and critical software; automated-proof training data | Near |

Near means a numerical or benchmark test may be possible within a year. Intermediate requires domain partners and operational data. Distant means primarily theoretical value, retained for future connections. Distant does not mean useless: the Radon transform also waited about half a century before CT applications.

## 6. Quality control and validation

### Credibility grades

| Grade | Meaning | Permitted use |
| --- | --- | --- |
| A | Formalized, with human-reviewed agreement between formal and natural-language statements | May support the theoretical basis of an engineering pilot |
| B | Lean proof exists; specification has not been reviewed by a person | Explore applications; upgrade to A before a pilot |
| C | Natural-language proof only | Explore with explicit risk; numerical investigation only |
| D | Withdrawn or found erroneous | Do not rely on the result; methods and constructions may be reassessed separately |

An application card inherits the lowest credibility grade in its dependency chain.

### Four defenses

1. **Specification review:** a mathematical reviewer confirms that the proof establishes what the paper says. Check signs, quantifier order, boundary cases, and hidden assumptions.
2. **Inspectable citations:** programs check historical DOI or arXiv identifiers, and the cited content must actually be checked in the original. This guards against fabricated references.
3. **Multiple providers and adversarial review:** at least two providers independently generate mappings and hypotheses, prioritizing overlap. The skeptic states the strongest objection to every lead.
4. **External judges:** experiments, benchmarks, or domain experts determine hypothesis outcomes, never model self-grading.

### Sampling

Each week, people review a random 5% of recorded leads. Separate **factual errors**, such as invented citations, misread propositions, or incorrect provenance, from **distance of association**. Pause automation at a stage whose factual-error rate exceeds 10% and repair the process. Track imaginative distance without penalizing it.

### Rejection threshold

None of the following alone justifies rejecting an application:

- The fields are too far apart.
- Nobody has used it this way.
- Adoption would take many years.
- It does not intuitively seem useful.
- A single model recommends rejection.

Valid reasons are mathematical contradiction, assumptions demonstrably false in the target setting, or reproducible adverse external evidence. Record the changed conditions under which a rejected lead would deserve reconsideration.

## 7. Deliverables and data structures

### Four deliverables

1. **Knowledge graph:** nodes represent papers, propositions, methods, constructions, historical literature, and application problems. Relations include “improves,” “depends on,” “is isomorphic to,” “can be used for,” and “has been rejected.” Every relation has provenance and credibility.
2. **Application cards:** one per lead; the basic unit of external delivery.
3. **Failure library:** unsuccessful connections and unsupported hypotheses, with reasons to prevent repeated work.
4. **Quarterly research report:** a one-page decision-maker overview of new leads, pilots, and the largest surprises.

### Application-card fields

| Field | Contents |
| --- | --- |
| Identifier | For example, APP-221-03 |
| Source | Family, manuscript, and exact proposition |
| Historical predecessor | Improved or required classical results, with inspectable citations |
| Transferable component | Conclusion, method, or construction in domain-independent language |
| Target problem | Specific industry, setting, and current bottleneck |
| Mechanism | Why the mathematics could improve the problem |
| Falsifiable hypothesis | Metric and predicted improvement |
| Test and outcome | Judge, method, and supported/adverse/pending result |
| Objections | Skeptic and human red-team concerns |
| Credibility | A, B, C, or D |
| Sensitivity | Whether controlled routing is required |
| Resources | Compute, data, and partners |
| Owner and status | Named responsibility; candidate, testing, pilot, or archived |

## 8. Organization, cadence, metrics, and risks

### People

- **One project lead:** sets priorities and takes responsibility for public conclusions.
- **Three to five part-time mathematical reviewers:** cover analysis, combinatorics, probability and mathematical physics, and algebraic geometry; review specifications and award A status.
- **Three to five domain translators:** understand both mathematics and an engineering area such as communications, optimization, materials, simulation, or formal verification. This is the scarcest role.
- **Engineering partners:** supply real bottlenecks, data, and pilot settings.

### Cadence

| Period | Focus | Completion criteria |
| --- | --- | --- |
| Weeks 1–4 | Knowledge foundation; stage-one decomposition and credibility grading | All 372 families recorded; specification mismatches listed |
| Weeks 5–8 | Historical lineage, components, cross-domain mapping | At least 500 candidates; at least 150 after human classification |
| Weeks 9–12 | Hypothesis testing and ranking | At least 100 application cards, including at least 10 numerically validated leads |
| Quarterly thereafter | Pilots, newly released results, retrospective adjustment | Quarterly report published |

### Metrics

- **Coverage:** fraction of families completing all six stages.
- **Effective leads:** application cards supported by external checks, rather than all generated ideas.
- **Translation into practice:** pilots or adoption by partners.
- **False-positive rate:** proportion rejected in human sampling.
- **Unit cost:** compute and human hours per effective card.

### Main risks

| Risk | Response |
| --- | --- |
| The underlying paper is wrong | Credibility grades and specification review; upgrade to A before adoption |
| Premature rejection misses distant applications | Broad admission, slow rejection, concrete reasons and two signatures; revisit pending and observation records |
| Similar models share blind spots | Multiple providers, distant association, human seeds, and reverse questions from engineering |
| Too many leads dilute attention | Rank rather than delete; prioritize supported and near-analogy leads while retaining distant and bold ideas cheaply |
| Public overstatement | Be imaginative internally and restrained publicly; claim only externally supported scope and attach objections |
| Sensitive results leak | Automatically route cryptanalysis and similar directions to controlled processes; do not develop them in the public graph |
| Copyright and attribution | Identify original results and historical sources; respect repository licenses |
| Compute costs grow uncontrollably | Use lower-cost models for the first three stages; reserve expensive models for mapping, association, and adversarial review |
| Competitors move faster | Durable value lies in a trustworthy network of connections and failure records, rather than priority on one lead |
