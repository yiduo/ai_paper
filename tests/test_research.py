import gzip
import itertools
import json
from pathlib import Path
import random
import unittest

from ai_value.corpus import parse_catalogue
from ai_value.graph import affected_nodes, human_gate, review_sample, theoretical_grade, validate
from ai_value.prefix import exact_order, peak_squared, transfer_order
from ai_value.superstring import exact_scs, forced_counts, lower_bound

ROOT = Path(__file__).resolve().parents[1]


class CatalogueTests(unittest.TestCase):
    def test_verification_results_keep_kind_and_exclude_nested_labels(self):
        from ai_value.source_results import named_results
        sample = r'''\begin{verification}[Finite certificate]
\label{ver:certificates} A recorded computation.
\begin{table}\label{tab:counts}Nested table.\end{table}
\begin{equation}\label{eq:count}n=1\end{equation}
\end{verification}
\begin{verification}No statement label.
\begin{table}\label{only:table}Nested.\end{table}\end{verification}'''
        results = named_results(sample)
        self.assertEqual([(r['kind'], r['label']) for r in results],
                         [('verification', 'ver:certificates')])
        self.assertEqual(results[0]['label_aliases'], [])
        upstream = ROOT/'math/preprints/Foulkes-Conjecture-for-the-Sixth-Symmetric-Power-September-25-2026/build/sections'
        if upstream.exists():
            actual = [r for p in upstream.glob('*.tex') for r in named_results(p.read_text())
                      if r['kind'] == 'verification']
            self.assertEqual({r['label'] for r in actual}, {'ver:certificates', 'ver:band'})

    def test_result_labels_inside_statements_exclude_nested_equations(self):
        from ai_value.source_results import named_results
        sample = r'''\begin{lemma}[A reduction]
First sentence. \label{reduction} Remaining condition.
\begin{equation}\label{equation:bound}x=1\end{equation}
\end{lemma}
\begin{lemma}No result label.
\begin{equation}\label{only:equation}x=2\end{equation}\end{lemma}
\begin{lemma}A {\label{only:group} grouped label}.\end{lemma}'''
        results = named_results(sample)
        self.assertEqual([r['label'] for r in results], ['reduction'])
        self.assertIn('First sentence.', sample[results[0]['statement_start']:results[0]['statement_end']])
        aliases = named_results(r'\begin{lemma}Text.\label{a}\label{b}\end{lemma}')
        self.assertEqual(aliases[0]['label'], 'a')
        self.assertEqual(aliases[0]['label_aliases'], ['b'])
        base = ROOT/'math/preprints/Almost-Linear-Time-Maximum-Cardinality-Matching-in-Sparse-General-Graphs-September-24-2026/build/sections'
        if base.exists():
            self.assertIn('lem:backend-reduction', {r['label'] for r in named_results((base/'07-backend-quality.tex').read_text())})
            self.assertIn('update:flat-lift', {r['label'] for r in named_results((base/'08-backend-updates.tex').read_text())})

    def test_result_coverage_keeps_cleveref_label_types(self):
        from ai_value.source_results import named_results
        sample = r'''\begin{lemma}[Logarithmic expansion]
\label[lemma]{tree:log-expansion}
An exact tree identity.\end{lemma}
\begin{proposition}\label[proposition]{upper:bound}
A uniform upper bound.\end{proposition}
% \begin{lemma}\label[lemma]{commented}\end{lemma}
\begin{lemma} Unlabelled.\end{lemma}'''
        results = named_results(sample)
        self.assertEqual([r['label'] for r in results], ['tree:log-expansion','upper:bound'])
        self.assertEqual(sample[results[0]['statement_start']:results[0]['statement_end']].strip(),
                         'An exact tree identity.')
        upstream = ROOT/'math/preprints/The-Mezard-Parisi-formula-for-diluted-spin-glasses-September-23-2026/build/sections/trees.tex'
        if upstream.exists():
            labels = {r['label'] for r in named_results(upstream.read_text())}
            self.assertEqual(labels, {'tree:insertion','tree:log-expansion','tree:extension-expansion',
                                     'tree:reference-total','tree:charging','tree:regular-shapes'})

    def test_result_coverage_keeps_nested_citation_titles(self):
        from ai_value.source_results import named_results
        sample = r'''% \begin{lemma}\label{commented}\end{lemma}
\begin{theorem}[Construction, {\cite[Theorem~1.1]{Companion}}]
\label{construction} Actual statement.\end{theorem}
\begin{lemma}[Escaped \] bracket]\label{second} Statement.\end{lemma}
\begin{lemma} Unlabelled statement.\end{lemma}'''
        self.assertEqual([r['label'] for r in named_results(sample)], ['construction','second'])
        upstream = ROOT/'math/preprints/The-Artinian-Lex-Plus-Powers-Betti-Theorem-September-23-2026/build/sections/01-forms.tex'
        if upstream.exists():
            self.assertEqual([r['label'] for r in named_results(upstream.read_text())], ['thm:forms'])

    def test_parentheses_in_pdf_path(self):
        families, papers = parse_catalogue('**007. Example.** Claim\n&emsp;[Title](preprints/CAT(0)/paper.pdf)')
        self.assertEqual(papers[0]['path'], 'preprints/CAT(0)/paper.pdf')
        self.assertEqual(families[0]['id'], 'F-007')

    def test_duplicate_papers_rejected(self):
        with self.assertRaises(ValueError):
            parse_catalogue('**001. Example.**\n&emsp;[x](preprints/x.pdf)\n&emsp;[x](preprints/x.pdf)')

    def test_all_old_manuscripts_are_explained(self):
        rows = [json.loads(x) for x in (ROOT/'data/corpus/reconciliation.jsonl').read_text().splitlines()]
        self.assertEqual(len(rows), 722)
        self.assertFalse(any(r['status']=='unresolved' for r in rows))
        self.assertEqual(sum(r['status']=='withdrawn_proof' for r in rows), 3)
        self.assertEqual(sum(r['status']=='revised_explicit_version_link' for r in rows), 27)
        self.assertEqual({r['family_id'] for r in rows if r['status']=='withdrawn_proof'}, {'F-032'})


class ExperimentTests(unittest.TestCase):
    def test_pressure_conditional_law_against_literal_index_enumeration(self):
        from decimal import Decimal, localcontext
        from ai_value.pressure_audit import conditional_profiles, conditional_pressure, literal_spin_log_partition
        with localcontext() as ctx:
            ctx.prec = 55
            beta = Decimal('0.7')
            for law, signs in [('symmetric_rademacher',(-1,1)),
                               ('deterministic_positive_one',(1,)),('zero',(0,))]:
                profiles = conditional_profiles(law,2)
                logs = {c:literal_spin_log_partition(beta,c) for c in range(-2,3)}
                events = list(itertools.product(range(2),range(2),signs))
                for count in range(3):
                    values = []
                    for sample in itertools.product(events,repeat=count):
                        partition = Decimal(0)
                        for spin in itertools.product((-1,1),repeat=2):
                            score = sum(j*spin[i]*spin[k] for i,k,j in sample)
                            partition += (beta*score).exp()
                        values.append(partition.ln()/2)
                    brute = sum(values)/len(values)
                    computed = conditional_pressure(profiles[count],beta,logs)
                    self.assertLess(abs(computed-brute),Decimal('1e-50'))

    def test_poisson_tail_majorants_cover_mass_and_first_moment(self):
        from decimal import Decimal, localcontext
        from fractions import Fraction
        from ai_value.pressure_audit import poisson_tail_majorants,poisson_weights,decimal_fraction
        with localcontext() as ctx:
            ctx.prec = 60
            mean,cutoff = Fraction(3,2),8
            weights = poisson_weights(decimal_fraction(mean),cutoff)
            tail,first = poisson_tail_majorants(mean,cutoff)
            self.assertGreater(decimal_fraction(tail),1-sum(weights))
            self.assertGreater(decimal_fraction(first),decimal_fraction(mean)-sum(k*w for k,w in enumerate(weights)))
            self.assertEqual(poisson_tail_majorants(Fraction(0),8),(0,0))
            with self.assertRaises(ValueError):
                poisson_tail_majorants(Fraction(9),8)

    def test_betti_oracles_against_complete_intersection(self):
        from ai_value.betti_budget import graded_betti, multigraded_betti, lex_generators, ideal_numerator, prescribed_numerator
        generators = lex_generators(2,[1,2,2,1],0,[2,3],6)
        self.assertEqual(set(generators),{(2,0),(0,3)})
        expected = {'0:0':1,'1:2':1,'1:3':1,'2:5':1}
        self.assertEqual(graded_betti(2,generators),expected)
        self.assertEqual(multigraded_betti(2,generators,100)[0],expected)
        self.assertEqual(ideal_numerator(2,generators),[1,0,-1,-1,0,1])
        self.assertEqual(prescribed_numerator(2,[1,2,2,1],0),[1,0,-1,-1,0,1])
        with self.assertRaises(ValueError):
            lex_generators(2,[1,3],0,[],3)
        from ai_value.betti_budget import experiment
        with self.assertRaisesRegex(ValueError,'characteristic zero'):
            experiment({'input':{'characteristic':2}})

    def test_full_law_audit_keeps_absent_permutations(self):
        from collections import Counter
        from ai_value.permutation_audit import statistics, fisher_yates
        cyclic = Counter({(0,1,2):1,(1,2,0):1,(2,0,1):1})
        stats = statistics(cyclic,3,3,3)
        self.assertEqual(stats['max_one_card_tv'],'0')
        self.assertEqual(stats['full_tv'],'1/2')
        self.assertEqual(stats['support_lower_bound'],'1/2')
        law = fisher_yates(4)
        self.assertEqual(len(law),24)
        self.assertEqual(set(law.values()),{1})
        self.assertEqual(statistics(law,4,24,24)['full_tv'],'0')

    def test_resource_failure_keeps_real_outputs_and_source_snapshot(self):
        import shutil
        import tempfile
        from ai_value.experiments import run
        with tempfile.TemporaryDirectory(prefix='ai-value-resource-check-') as folder:
            root = Path(folder)
            shutil.copytree(ROOT/'src',root/'src',ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copytree(ROOT/'configs',root/'configs')
            spec = json.loads((ROOT/'experiments/specs/EXP-130-001.json').read_text())
            spec['resource_limit_seconds'] = 0
            target = root/'experiments/specs/EXP-130-001.json'
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(spec))
            manifest = run(root,'EXP-130-001')
            self.assertEqual(manifest['result'],'resource_envelope_exceeded')
            archive = root/'experiments/runs'/manifest['run_id']
            rows = json.loads(gzip.decompress((archive/'raw.json.gz').read_bytes()))
            self.assertEqual(len(rows),37)
            snapshot = json.loads(gzip.decompress((archive/'inputs.json.gz').read_bytes()))
            self.assertIn('src/ai_value/experiments.py',snapshot)
            self.assertEqual(run(root,'EXP-130-001')['run_id'],manifest['run_id'])

    def test_face_derivatives_and_gauge_invariance(self):
        from fractions import Fraction as F
        from ai_value.transport import face_differentials,cell_mass_moments
        slopes = [(F(0),F(0)),(F(-1),F(0)),(F(1),F(1))]
        intercepts = [F(0),F(0),F(-15,8)]
        masses,moments,dm,db,_ = face_differentials(slopes,intercepts,(1,1,1))
        self.assertEqual(sum(masses),1)
        self.assertEqual(sum(x for x,y in moments),0)
        self.assertEqual(sum(y for x,y in moments),0)
        self.assertFalse(any(dm))
        self.assertFalse(any(any(row) for row in db))
        _,_,dm,db,_ = face_differentials(slopes,intercepts,(0,0,1))
        h = F(1,2**20)
        plus,_,_ = cell_mass_moments(slopes,[intercepts[0],intercepts[1],intercepts[2]+h])
        minus,_,_ = cell_mass_moments(slopes,[intercepts[0],intercepts[1],intercepts[2]-h])
        self.assertEqual(dm,[(p-m)/(2*h) for p,m in zip(plus,minus,strict=True)])
    def test_exact_polygon_and_transport_oracles(self):
        from fractions import Fraction as F
        from ai_value.transport import area, cell, transport_cost, three_atom_example
        self.assertEqual(area(cell([(1,0,0)])), 2)
        sites = [(F(-1),F(0)),(F(1),F(0)),(F(0),F(0))]
        masses = [F(1,4),F(1,4),F(1,2)]
        self.assertEqual(transport_cost(sites,masses,sites,masses), 0)
        example = three_atom_example(F(1,8))
        self.assertEqual(sum(example['source_masses']),1)
        self.assertEqual(example['source_masses'],example['target_masses'])
        with self.assertRaises(ValueError):
            three_atom_example(F(1,2))
    def test_periodicity_is_a_substantive_ablation(self):
        for h in range(1, 12):
            self.assertEqual(lower_bound(['a'*h]), h)
            self.assertEqual(lower_bound(['a'*h], periodic=False), 1)

    def test_occurrence_counts_against_bruteforce(self):
        words = ['0', '1', '00', '01', '10', '11', '010', '101']
        for strings in itertools.combinations(words, 3):
            optimum = exact_scs(list(strings))
            for s, count in forced_counts(list(strings)).items():
                actual = sum(optimum.startswith(s, i) for i in range(len(optimum)))
                self.assertLessEqual(count, actual)

    def test_subset_dp_against_independent_permutations(self):
        rng = random.Random(42)
        for _ in range(8):
            vectors = [[rng.randrange(-2, 3) for _ in range(3)] for _ in range(5)]
            order, cost = exact_order(vectors)
            brute = min(peak_squared(vectors, list(p)) for p in itertools.permutations(range(5)))
            self.assertEqual(cost, brute)
            self.assertEqual(peak_squared(vectors, order), brute)

    def test_transfer_rejects_nonzero_sum(self):
        with self.assertRaises(ValueError):
            transfer_order([[1, 0], [0, 1]])

    def test_archived_numerical_payloads_compress_losslessly(self):
        import hashlib
        for p in (ROOT/'experiments/runs').glob('*/manifest.json'):
            manifest = json.loads(p.read_text())
            for name, metadata in manifest.get('compressed_payloads', {}).items():
                uncompressed = gzip.decompress((p.parent/name).read_bytes())
                self.assertEqual(hashlib.sha256(uncompressed).hexdigest(), metadata['uncompressed_sha256'])
                self.assertFalse((p.parent/metadata['uncompressed_name']).exists())


class EvidenceTests(unittest.TestCase):
    def test_alternative_routes_and_mandatory_dependencies_use_least_fixed_point(self):
        nodes = {i: {'id': i, 'kind': 'method', 'properties': {}}
                 for i in ['R1', 'R2', 'X', 'Y', 'M', 'CONTEXT', 'DOWNSTREAM']}
        nodes['MAIN'] = {'id': 'MAIN', 'kind': 'claim', 'properties': {
            'alternative_proof_route_ids': ['R1', 'R2']}}
        edges = [{'source': a, 'relation': rel, 'target': b} for a, rel, b in [
            ('R1', 'depends_on', 'X'), ('R2', 'uses', 'Y'),
            ('MAIN', 'depends_on', 'M'), ('DOWNSTREAM', 'derived_from', 'MAIN'),
            ('R1', 'depends_on', 'MAIN'),  # A cycle must not activate itself.
            ('R1', 'supports', 'MAIN'), ('CONTEXT', 'related_to', 'MAIN')]]
        self.assertEqual(affected_nodes(nodes, edges, set()), set())
        self.assertEqual(affected_nodes(nodes, edges, {'X'}), {'X', 'R1'})
        self.assertEqual(affected_nodes(nodes, edges, {'X', 'Y'}),
                         {'X', 'Y', 'R1', 'R2', 'MAIN', 'DOWNSTREAM'})
        self.assertEqual(affected_nodes(nodes, edges, {'M'}),
                         {'M', 'MAIN', 'R1', 'DOWNSTREAM'})
        self.assertNotIn('CONTEXT', affected_nodes(nodes, edges, {'MAIN'}))

    def test_alternative_route_declarations_reject_invalid_references(self):
        from ai_value.graph import validate_alternative_routes, impact_report
        for routes in [[], 'R', ['R', 'R'], ['MISSING'], ['MAIN'], [1], ['WRONG']]:
            nodes = {'MAIN': {'kind': 'claim', 'properties': {'alternative_proof_route_ids': routes}},
                     'R': {'kind': 'method', 'properties': {}},
                     'WRONG': {'kind': 'literature', 'properties': {}}}
            with self.subTest(routes=routes), self.assertRaisesRegex(ValueError, 'MAIN'):
                validate_alternative_routes(nodes)
        nodes = {'R': {'kind': 'method', 'properties': {}}}
        with self.assertRaises(ValueError):
            impact_report(nodes, [], set())
        with self.assertRaises(ValueError):
            affected_nodes(nodes, [], {'MISSING'})

    def test_real_foulkes_alternatives_and_multiseed_cli(self):
        import subprocess
        import sys
        from ai_value.graph import load, impact_report
        nodes, edges = load(ROOT)
        main, short, independent = ('CLM-210-M-THM-MAIN',
            'PART-210-SHORT-ROUTE', 'PART-210-INDEPENDENT-ROUTE')
        q, chart = 'CLM-210-Q-THM-MAIN', 'CLM-210-M-PROP-LARGE'
        first = impact_report(nodes, edges, {q})
        self.assertIn(short, first['affected'])
        self.assertNotIn(independent, first['affected'])
        self.assertNotIn(main, first['affected'])
        both = impact_report(nodes, edges, {q, chart})
        self.assertIn(main, both['affected'])
        self.assertIn('PART-210-COMPARISON-VS-CANONICAL', both['affected'])
        shared = impact_report(nodes, edges, {'CLM-210-M-VER-BAND'})
        self.assertIn(main, shared['affected'])
        group = next(g for g in first['alternative_routes'] if g['claim_id'] == main)
        self.assertEqual(group['unaffected_routes'], [independent])
        self.assertFalse(group['claim_requires_review'])
        result = subprocess.run([sys.executable, '-m', 'ai_value.cli', 'impact', q,
                                 '--changed', chart, '--root', str(ROOT)],
                                capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout), both)

    def test_browser_and_python_impact_closures_match_on_real_graph(self):
        import shutil
        import subprocess
        from ai_value.graph import load
        node = shutil.which('node')
        if not node:
            self.skipTest('Node is optional for local browser-logic parity verification')
        nodes, edges = load(ROOT)
        cases = [[], ['CLM-210-Q-THM-MAIN'], ['CLM-210-M-PROP-LARGE'],
                 ['CLM-210-Q-THM-MAIN', 'CLM-210-M-PROP-LARGE'],
                 ['CLM-210-M-VER-BAND'], ['CLM-210-M-THM-MAIN'],
                 ['PART-210-CONSUMER-GATE'], ['P-c6dfdbb531ac61fa'],
                 ['PART-317-COMPLETED-TENSOR']]
        script = '''const fn=require(process.argv[1]);let s='';
process.stdin.setEncoding('utf8');process.stdin.on('data',x=>s+=x);
process.stdin.on('end',()=>{const x=JSON.parse(s);process.stdout.write(
JSON.stringify(x.cases.map(c=>fn(x.nodes,x.edges,c))));});'''
        result = subprocess.run([node, '-e', script, str(ROOT/'src/ai_value/impact.js')],
                                input=json.dumps({'nodes': list(nodes.values()), 'edges': edges,
                                                  'cases': cases}),
                                capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout),
                         [sorted(affected_nodes(nodes, edges, set(c))) for c in cases])

    def test_partial_family_never_counts_as_full_source_draft(self):
        from ai_value.graph import load
        nodes,_ = load(ROOT)
        p = nodes['ANALYSIS-F-238']['properties']
        self.assertEqual(len(p['manuscript_ids']),12)
        read_ids = set(p['manuscript_source_drafts_complete_ids'])
        self.assertTrue(read_ids < set(p['manuscript_ids']))
        self.assertIn('P-ce6a8a7cfdd51cf0', read_ids)
        source_results = [rid for mapping in p['result_ids_by_source'].values()
                          for rid in mapping.values()]
        self.assertEqual(set(source_results), set(p['result_ids_by_label'].values()))
        self.assertEqual(len(source_results), len(set(source_results)))
        revealed = {label: rid for label, rid in p['result_ids_by_label'].items()
                    if label.startswith('revealed:')}
        self.assertEqual(len(revealed),17)
        self.assertNotIn('revealed:input:character', revealed)
        self.assertFalse(p['source_decomposition_draft_complete'])
        self.assertFalse(p['full_family_complete'])
        summary = nodes['APP-238-01']['properties']['summary']
        self.assertEqual(summary['support_audit_detected'],4)
        self.assertEqual(summary['marginal_only_detected'],0)
        self.assertEqual(summary['transition_disagreements'],0)

    def test_two_manuscripts_do_not_merge_same_labels_or_bibkeys(self):
        from ai_value.graph import load
        nodes,_ = load(ROOT)
        p = nodes['ANALYSIS-F-149']['properties']
        bounded = nodes[p['result_ids_by_label']['bounded:thm:main']]['properties']
        uniform = nodes[p['result_ids_by_label']['uniform:thm:main']]['properties']
        self.assertNotEqual(p['result_ids_by_label']['bounded:thm:main'],
                            p['result_ids_by_label']['uniform:thm:main'])
        self.assertEqual(bounded['credibility'],'B')
        self.assertEqual(uniform['credibility'],'C')
        self.assertNotEqual(p['historical_references_by_key']['bounded:Anderson2011'],
                            p['historical_references_by_key']['uniform:Anderson2011'])
        self.assertEqual(len(p['result_ids_by_label']),13)
        self.assertEqual(sum(len(v) for v in p['result_ids_by_source'].values()),13)
        self.assertFalse(p['full_family_complete'])

    def test_decomposition_draft_does_not_claim_full_completion(self):
        from ai_value.graph import load
        nodes,_ = load(ROOT)
        p = nodes['ANALYSIS-F-374']['properties']
        self.assertEqual(len(p['result_ids_by_label']),11)
        self.assertTrue(p['source_decomposition_draft_complete'])
        self.assertFalse(p['full_family_complete'])
        self.assertFalse(p['historical_lineage_complete'])
        self.assertEqual(p['formal_status']['local_build'],'not_run')
        self.assertEqual(nodes['CHECK-374-MOMENTS']['properties']['application_hypotheses_added'],0)

    def test_static_lean_index_ignores_comments_and_strings(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('lean_index',ROOT/'scripts/index_lean_closure.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sample = '-- sorry\n/- admit /- sorry -/ axiom -/\ndef x := "sorry"\ntheorem y : True := by sorry\n'
        code = module.code_only(sample)
        self.assertEqual(code.count('sorry'),1)
        index = json.loads(gzip.decompress((ROOT/'data/graph/lean_indices/F-374.json.gz').read_bytes()))
        self.assertEqual(index['local_build'],'not_run')
        self.assertIn('Mathlib',index['external_modules_not_present'])
    def test_historical_version_graph_and_scope_boundaries(self):
        from ai_value.graph import load
        from ai_value.knowledge import neighborhood
        nodes,edges = load(ROOT)
        self.assertEqual(sum(n['kind']=='historical_manuscript' for n in nodes.values()),30)
        self.assertEqual(sum(e['relation']=='supersedes' for e in edges),27)
        self.assertEqual(sum(e['relation']=='withdraws_proof_of' for e in edges),3)
        self.assertEqual(nodes['CLM-262-MATRIX']['properties']['credibility'],'C')
        self.assertEqual(nodes['CLM-262-SCALAR']['properties']['credibility'],'B')
        neighbors = neighborhood(ROOT,'APP-374-01',2)
        self.assertTrue(any(n['kind']=='experiment_run' for n in neighbors['nodes']))
        self.assertFalse(any(n['id']=='F-001' for n in neighbors['nodes']))
    def test_withdrawal_propagates_transitively(self):
        nodes = {i: {'kind': 'claim', 'properties': {'credibility': g, 'dependency_closure_complete': True}}
                 for i, g in [('SOURCE','D'), ('METHOD','B'), ('CARD','A')]}
        edges = [{'source':'METHOD','target':'SOURCE','relation':'depends_on'},
                 {'source':'CARD','target':'METHOD','relation':'uses'}]
        self.assertEqual(theoretical_grade(nodes, edges, 'CARD'), 'D')
        self.assertEqual(affected_nodes(nodes, edges, {'SOURCE'}), set(nodes))

    def test_unknown_dependency_never_upgraded(self):
        nodes = {'CARD': {'kind':'connection','properties':{'credibility':'A','dependency_closure_complete':True}}}
        edges = [{'source':'CARD','target':'MISSING','relation':'depends_on'}]
        self.assertEqual(theoretical_grade(nodes, edges, 'CARD'), 'unknown')

    def test_single_model_cannot_confirm_rejection_or_pilot(self):
        record = {'id':'CARD', 'properties':{'application_result':'否定','workflow':'待人工'}}
        ai_reviews = [{'subject_id':'CARD','actor_type':'model','external_evidence':'x','reviewer_id':str(i),'decision':'confirm_rejection'} for i in range(2)]
        with self.assertRaises(ValueError):
            human_gate(record, ai_reviews, grade='A')
        humans = [dict(r, actor_type='human') for r in ai_reviews]
        human_gate(record, humans, grade='A')
        humans[1]['reviewer_id'] = humans[0]['reviewer_id']
        with self.assertRaises(ValueError):
            human_gate(record, humans, grade='A')
        record['properties'] = {'application_result':'通过','workflow':'试点'}
        with self.assertRaises(ValueError):
            human_gate(record, [], grade='B')

    def test_review_queue_is_stable_and_nonempty(self):
        self.assertEqual(review_sample(['c','b','a'], .05, 1), review_sample(['a','b','c'], .05, 1))
        self.assertEqual(len(review_sample(['a','b','c'], .05, 1)), 1)

    def test_real_graph_and_export_fields(self):
        result = validate(ROOT)
        self.assertEqual(result['human_grading_records'], 0)
        self.assertLessEqual(result['effective_leads'], result['externally_checked_cards'])
        self.assertGreaterEqual(result['externally_checked_cards'], 3)


if __name__ == '__main__':
    unittest.main()
