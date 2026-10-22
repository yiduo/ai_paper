import copy
import unittest

from ai_value.navigation import build_navigation


def node(i, kind, **p):
    return dict(id=i, kind=kind, properties=p)


class NavigationTests(unittest.TestCase):
    def test_text_only_baseline_and_unrun_plan_do_not_become_checked_edges(self):
        nodes = {n['id']: n for n in [
            node('F-A', 'family', title='Catalogue only', subject='Logic', manuscript_ids=['P-A']),
            node('P-A', 'manuscript', family_id='F-A'),
            node('APP-A', 'connection', title='Conditional', family_ids=['F-A'],
                 baseline='old solver', part_ids=['PART-A'], run_ids=[], theoretical_grade='unknown'),
            node('PART-A', 'method', input='x', output='y', conditions='if eligible'),
        ]}
        before = copy.deepcopy(nodes)
        result = build_navigation(nodes, [], {})
        card = result['applications'][0]
        self.assertIn('baseline_text_without_direct_comparator_edge', card['gaps'])
        self.assertIn('no_actual_run', card['gaps'])
        self.assertFalse(result['families'][0]['actual_reading_recorded'])
        self.assertEqual(result['totals']['with_explicit_unestablished_gates'], 0)
        self.assertEqual(nodes, before)

    def test_explicit_gate_and_comparator_are_preserved_without_closing_dependencies(self):
        nodes = {n['id']: n for n in [
            node('F-A', 'family', title='F', subject='Logic'),
            node('APP-A', 'connection', title='A', family_ids=['F-A'], theoretical_grade='unknown'),
            node('GATE-A', 'method', prerequisite_status='unestablished'),
            node('OLD-A', 'literature'),
        ]}
        edges = [dict(id='E-G', source='APP-A', relation='depends_on', target='GATE-A'),
                 dict(id='E-B', source='APP-A', relation='compared_with', target='OLD-A')]
        result = build_navigation(nodes, edges, {})
        card = result['applications'][0]
        self.assertEqual(card['explicit_unestablished_gate_edges'], ['E-G'])
        self.assertEqual(card['direct_comparator_edges'], ['E-B'])
        self.assertEqual(card['theoretical_grade'], 'unknown')
        self.assertEqual(result['edges']['E-G'], edges[0])

    def test_analysis_foreign_keys_join_methods_but_identical_doi_versions_stay_distinct(self):
        nodes = {n['id']: n for n in [
            node('F-A', 'family', title='F', subject='Logic', manuscript_ids=['P-A']),
            node('P-A', 'manuscript', family_id='F-A'),
            node('CLM-A', 'claim', manuscript_id='P-A'),
            node('PART-A', 'method'),
            node('ANALYSIS-A', 'family_analysis', family_id='F-A', method_ids=['PART-A'],
                 source_decomposition_draft_complete=True, historical_lineage_complete=False),
            node('LIT-V1', 'literature', doi='10.1234/ABC'),
            node('LIT-V2', 'literature', doi='10.1234/abc'),
        ]}
        for n in nodes.values():
            n['sources'] = []
        result = build_navigation(nodes, [], {'partially_read_families': {'F-A': ['selected text']}})
        f = result['families'][0]
        self.assertEqual(f['claim_ids'], ['CLM-A'])
        self.assertEqual(f['method_ids'], ['PART-A'])
        self.assertTrue(f['source_draft_complete'])
        self.assertFalse(f['historical_lineage_complete'])
        self.assertEqual(result['identity_review_candidates'][0]['node_ids'], ['LIT-V1', 'LIT-V2'])


if __name__ == '__main__':
    unittest.main()
