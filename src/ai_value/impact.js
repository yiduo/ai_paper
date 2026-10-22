// Review routing only. Unaffected routes are not verified proofs.
function impactedGraphNodes(nodes, edges, changed) {
  const byId = new Map(nodes.map(n => [n.id, n]));
  for (const id of changed) if (!byId.has(id)) throw new Error('未知节点：' + id);
  const groups = nodes.filter(n => 'alternative_proof_route_ids' in (n.properties || {}));
  for (const n of groups) {
    const routes = n.properties.alternative_proof_route_ids;
    if (n.kind !== 'claim' || !Array.isArray(routes) || !routes.length ||
        routes.some(id => typeof id !== 'string' || id === n.id || byId.get(id)?.kind !== 'method') ||
        new Set(routes).size !== routes.length) throw new Error('替代路线记录无效：' + n.id);
  }
  const affected = new Set(changed);
  const relations = new Set(['depends_on', 'uses', 'derived_from', 'cites']);
  let added = true;
  while (added) {
    added = false;
    const more = new Set();
    for (const e of edges) if (relations.has(e.relation) && affected.has(e.target)) more.add(e.source);
    for (const n of groups) if (n.properties.alternative_proof_route_ids.every(id => affected.has(id))) more.add(n.id);
    for (const id of more) if (!affected.has(id)) { affected.add(id); added = true; }
  }
  return [...affected].sort();
}
if (typeof module !== 'undefined' && module.exports) module.exports = impactedGraphNodes;
