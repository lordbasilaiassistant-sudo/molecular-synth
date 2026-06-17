/* The Synthesizer brain, in the browser — a faithful JS port of catalog/makerlib
   (checker.py + order.py). Type a request -> decompose -> feasibility verdict -> route
   to a maker -> machine plan. Honest: declines what the synth can't make. */
(function () {
  const NS = '⭐ north-star', RD = '✅ ready', AS = '🟡 assemble', FR = '🔬 frontier';
  const LABEL = { ready: RD, assemble: AS, frontier: FR, 'north-star': NS };
  const ORDER = ['ready', 'assemble', 'frontier', 'north-star'];

  // keyword buckets for UNKNOWN queries (mirror checker._BUCKETS)
  const BUCKETS = [
    [['water', 'ice'], ['ready', 'watersynth', 'drink', ['H2O molecules', 'atoms']]],
    [['coffee', 'tea', 'latte', 'juice', 'soda', 'cola', 'lemonade', 'smoothie', 'drink', 'espresso', 'cocktail', 'milk'],
      ['ready', 'drinksynth', 'drink', ['water + dissolved/suspended molecules', 'atoms']]],
    [['origami', 'nanostructure', 'nanoshape', 'aptamer', 'nanorobot', 'nano', 'dna'],
      ['ready', 'molsynth', 'material', ['DNA scaffold + staples', 'nucleotides', 'atoms']]],
    [['cookie', 'cake', 'bread', 'pizza', 'pasta', 'soup', 'meal', 'sandwich', 'snack', 'sauce', 'dish', 'rice', 'egg', 'food', 'candy', 'chocolate', 'lasagna', 'taco', 'burger', 'burrito', 'noodle', 'fries', 'salad', 'stew', 'curry', 'pancake', 'waffle', 'muffin', 'donut', 'pie', 'fruit'],
      ['assemble', 'kitchen (planned)', 'food', ['stocked ingredients', 'polysaccharides/proteins/lipids/water', 'atoms']]],
    [['case', 'bracket', 'holder', 'part', 'tool', 'toy', 'gear', 'mount', 'widget', 'clip', 'knob', 'object', 'figurine', 'enclosure'],
      ['assemble', 'printsynth (FDM)', 'object', ['a 3D mesh of thermoplastic', 'polymer (PLA/PETG)', 'atoms']]],
    [['protein', 'enzyme', 'antibody', 'peptide', 'hormone', 'insulin'],
      ['frontier', 'biofab (frontier)', 'component', ['amino-acid chain', 'amino acids', 'encoded by DNA', 'atoms']]],
    [['drug', 'molecule', 'compound', 'medicine', 'aspirin', 'vitamin', 'chemical', 'ethanol', 'whiskey', 'alcohol'],
      ['frontier', 'chemfab (frontier)', 'component', ['a sequence of bond-forming reactions', 'atoms + bonds']]],
    [['phone', 'smartphone', 'computer', 'cpu', 'chip', 'microchip', 'battery', 'circuit', 'screen', 'transistor', 'laptop', 'processor'],
      ['north-star', 'none', 'object', ['semiconductors + battery + display', 'doped silicon/metals/polymers', 'atoms']]],
    [['carbon', 'oxygen', 'transmute', 'transmutation', 'element', 'gold', 'lead', 'plutonium', 'uranium', 'replicator', 'materialize'],
      ['north-star', 'none (nuclear)', 'element', ['changing the element = changing the NUCLEUS', 'nuclear transmutation (~MeV/atom)', 'not chemistry — reactor/accelerator only']]],
  ];

  let CAT = null, KB = null;
  const norm = s => s.toLowerCase().trim().replace(/\s+/g, ' ');

  async function loadData() {
    if (CAT && KB) return;
    try {
      const [a, b] = await Promise.all([
        fetch('data/items.json', { cache: 'no-store' }).then(r => r.json()),
        fetch('data/cocktails.json', { cache: 'no-store' }).then(r => r.json()),
      ]);
      CAT = a.items; KB = b;
    } catch (e) {
      CAT = FALLBACK_ITEMS; KB = FALLBACK_KB;
    }
  }

  function bestFeas(styles) {
    const fs = (styles || []).map(s => s.feasibility);
    fs.push('north-star');
    return fs.reduce((m, f) => ORDER.indexOf(f) < ORDER.indexOf(m) ? f : m, 'north-star');
  }
  function findItem(q) {
    q = norm(q);
    for (const it of CAT) {
      const names = [norm(it.name), ...(it.aliases || []).map(norm)];
      if (names.includes(q)) return it;
    }
    for (const it of CAT) {
      const names = [norm(it.name), ...(it.aliases || []).map(norm)];
      if (names.some(n => q.includes(n) || n.includes(q))) return it;
    }
    return null;
  }
  function classifyUnknown(q) {
    const t = norm(q);
    for (const [keys, [feas, maker, cat, tail]] of BUCKETS) {
      if (keys.some(k => t.includes(k)))
        return { name: q, category: cat, cataloged: false, decomposition: [q, ...tail],
          styles: [{ style: 'estimated', maker, feasibility: feas, how: '(estimated from the nearest category — verify and add)', citation: '' }],
          best: feas, notes: 'Not yet cataloged — estimate from the nearest bucket.' };
    }
    return { name: q, category: 'unknown', cataloged: false, decomposition: [q, '(decompose -> components -> molecules -> atoms)'],
      styles: [{ style: 'unknown', maker: 'none', feasibility: 'north-star', how: '(not classified — decompose it)' }],
      best: 'north-star', notes: 'Not recognised. Decompose it (the cookie principle) and add it to the catalog.' };
  }
  function check(q) {
    const it = findItem(q);
    if (!it) return classifyUnknown(q);
    return { name: it.name, category: it.category, cataloged: true, decomposition: it.decomposition || [],
      styles: it.styles || [], best: bestFeas(it.styles), notes: it.notes || '' };
  }

  // ---- drink/cocktail interpreter (mirror order.interpret/fulfill) ----
  const SPIRIT = () => new Set(KB.spirits);
  function interpret(text) {
    let raw = norm(text);
    raw = KB.aliases[raw] || raw;
    const mods = {}, found = [];
    Object.keys(KB.modifiers).sort((a, b) => b.length - a.length).forEach(p => {
      if (raw.includes(p)) { Object.assign(mods, KB.modifiers[p]); found.push(p); }
    });
    let recipe = null, name = null;
    if (KB.recipes[raw]) { recipe = KB.recipes[raw]; name = raw; }
    else for (const n of Object.keys(KB.recipes).sort((a, b) => b.length - a.length))
      if (raw.includes(n)) { recipe = KB.recipes[n]; name = n; break; }
    if (!recipe) {
      let cleaned = raw; found.forEach(p => cleaned = cleaned.replace(p, ' '));
      cleaned = norm(cleaned);
      const sp = KB.spirits.find(s => cleaned.includes(s));
      if (sp) { recipe = { pour: { [sp]: 60 }, ice: false, garnish: '' }; name = sp; }
    }
    if (!recipe) return { kind: 'catalog', raw: text, report: check(text) };
    const sset = SPIRIT();
    let pour = Object.assign({}, recipe.pour), ice = !!recipe.ice, chilled = !!recipe.chilled, garnish = recipe.garnish || '';
    if ('ice' in mods) ice = mods.ice;
    if ('chilled' in mods) chilled = mods.chilled;
    if (mods.mixer === false) { const np = {}; Object.keys(pour).forEach(k => { if (sset.has(k)) np[k] = pour[k]; }); pour = np; }
    if (mods.spirit_mult) Object.keys(pour).forEach(k => { if (sset.has(k)) pour[k] = Math.round(pour[k] * mods.spirit_mult); });
    if (mods.mixer_mult) Object.keys(pour).forEach(k => { if (!sset.has(k)) pour[k] = Math.round(pour[k] * mods.mixer_mult); });
    if (mods.add) Object.assign(pour, mods.add);
    return { kind: 'drink', raw: text, name, pour, ice, chilled, garnish, modifiers: found };
  }
  function fulfill(intent) {
    if (intent.kind === 'catalog') {
      const r = intent.report;
      return { kind: 'catalog', name: r.name, best: r.best, decomposition: r.decomposition,
        makers: [...new Set(r.styles.map(s => s.maker))], notes: r.notes, cataloged: r.cataloged };
    }
    const steps = [], cmds = [], makers = new Set();
    if (intent.ice) { steps.push(['watersynth', 'ICE ~80 g']); cmds.push('ICE 80'); makers.add('watersynth'); }
    if (intent.chilled) { steps.push(['watersynth', 'CHILL glass']); makers.add('watersynth'); }
    for (const [k, v] of Object.entries(intent.pour)) { steps.push(['drinksynth', `POUR ${k} ${v} mL`]); cmds.push(`PUMP ${k} ${v}`); makers.add('drinksynth'); }
    if (intent.garnish) steps.push(['garnish', `GARNISH ${intent.garnish}`]);
    steps.push(['serve', 'SERVE']); cmds.push('DONE');
    return { kind: 'drink', name: intent.name, best: 'ready', pour: intent.pour, ice: intent.ice,
      garnish: intent.garnish, modifiers: intent.modifiers, steps, cmds, makers: [...makers] };
  }
  async function order(text) { await loadData(); return fulfill(interpret(text)); }

  // ---- minimal inline fallback (so the demo never breaks) ----
  const FALLBACK_ITEMS = [
    { name: 'water', aliases: ['h2o', 'glass of water'], category: 'drink', decomposition: ['a glass of water', 'H2O molecules', 'atoms'], styles: [{ style: 'tap/AWG + treat', maker: 'watersynth', feasibility: 'ready' }], notes: '' },
    { name: 'dna nanostructure', aliases: ['dna tetrahedron', 'nanostructure', 'origami'], category: 'material', decomposition: ['a ~10-100 nm shape', 'DNA scaffold + staples', 'nucleotides', 'atoms'], styles: [{ style: 'fold', maker: 'molsynth', feasibility: 'ready' }], notes: 'Atomic precision, nanoscale.' },
    { name: 'cookie', aliases: [], category: 'food', decomposition: ['a cookie', 'flour/sugar/butter/egg', 'starch/sucrose/lipids/proteins', 'atoms'], styles: [{ style: 'assemble+bake', maker: 'kitchen (planned)', feasibility: 'assemble' }], notes: 'Assemble + bake from stock.' },
  ];
  const FALLBACK_KB = { spirits: ['whiskey', 'vodka', 'gin', 'rum', 'tequila'],
    modifiers: { 'on the rocks': { ice: true }, neat: { ice: false, mixer: false }, double: { spirit_mult: 2 } },
    aliases: { 'g&t': 'gin and tonic' },
    recipes: { 'whiskey on the rocks': { pour: { whiskey: 60 }, ice: true, garnish: '' }, 'gin and tonic': { pour: { gin: 50, 'tonic water': 150 }, ice: true, garnish: 'lime' } } };

  window.Synth = { order, check, loadData, LABEL };
})();
