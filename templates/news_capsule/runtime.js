(function() {
  'use strict';

  // --- Parse canonical data (read-only) ---
  var manifest = JSON.parse(document.getElementById('capsule-manifest').textContent);
  var data = JSON.parse(document.getElementById('capsule-data').textContent);

  // --- Partition records by kind ---
  var article = null;
  var claims = [];
  var entities = [];
  var sources = [];
  data.records.forEach(function(rec) {
    if (rec.kind === 'article') article = rec;
    else if (rec.kind === 'claim') claims.push(rec);
    else if (rec.kind === 'entity') entities.push(rec);
    else if (rec.kind === 'cited_source') sources.push(rec);
  });

  if (!article) {
    document.getElementById('article-blocks').textContent = 'Error: no article record found in capsule data.';
    return;
  }

  // Map block_id -> claim list for inline markers
  var claimsByBlock = {};
  claims.forEach(function(c) {
    if (c.block_id) {
      (claimsByBlock[c.block_id] = claimsByBlock[c.block_id] || []).push(c);
    }
  });

  // --- User state (memory only) ---
  var userState = {
    verdicts: {},          // claim_record_id -> "approve" | "reject" | "defer" | "skip"
    claimNotes: {},        // claim_record_id -> string
    summaryNotes: '',
    filter: 'all',
    sidebarTab: 'claims',
    sidebarOpen: true
  };

  // --- DOM refs ---
  var $ = function(id) { return document.getElementById(id); };
  var els = {
    title: $('article-title'),
    subtitle: $('article-subtitle'),
    author: $('article-author'),
    publisher: $('article-publisher'),
    published: $('article-published'),
    captureNote: $('capture-note'),
    blocks: $('article-blocks'),
    summaryNotes: $('summary-notes'),
    sidebar: $('sidebar'),
    layout: document.querySelector('.capsule-layout'),
    btnToggleSidebar: $('btn-toggle-sidebar'),
    filterSelect: $('filter-select'),
    btnCopyJson: $('btn-copy-json'),
    btnCopyMd: $('btn-copy-md'),
    btnPrint: $('btn-print'),
    btnExport: $('btn-export'),
    claimsSummary: $('claims-summary'),
    claimsList: $('claims-list'),
    entitiesList: $('entities-list'),
    sourcesList: $('sources-list'),
    countClaims: $('count-claims'),
    countEntities: $('count-entities'),
    countSources: $('count-sources'),
    footerSourceLine: $('footer-source-line'),
    footerOriginalLink: $('footer-original-link'),
    footerContentMode: $('footer-content-mode'),
    aboutContent: $('about-content'),
    toast: $('toast')
  };

  // --- Header ---
  els.title.textContent = article.title || 'Untitled';
  if (article.subtitle) { els.subtitle.textContent = article.subtitle; els.subtitle.hidden = false; }
  els.author.textContent = article.byline || 'Unknown';
  els.publisher.textContent = article.publisher || '';
  if (article.published_at) {
    els.published.dateTime = article.published_at;
    els.published.textContent = formatDate(article.published_at);
  }
  if (article.captured_at) {
    els.captureNote.textContent = 'Captured ' + formatDate(article.captured_at) +
      (article.content_mode ? ' · ' + article.content_mode.replace(/_/g, ' ') : '');
  }

  // --- Footer provenance ---
  if (article.publisher) {
    els.footerSourceLine.textContent =
      ' The original was published by ' + article.publisher +
      (article.published_at ? ' on ' + formatDate(article.published_at) : '') + '.';
  }
  if (article.url) {
    els.footerOriginalLink.href = article.url;
    els.footerOriginalLink.textContent = article.url;
  } else {
    els.footerOriginalLink.textContent = '(no URL)';
  }
  if (article.content_mode) els.footerContentMode.textContent = article.content_mode;

  // --- Render article blocks ---
  var blocks = article.blocks || [];
  blocks.forEach(function(block, index) {
    var el = renderBlock(block, index);
    els.blocks.appendChild(el);
  });

  function renderBlock(block, index) {
    var div = document.createElement('div');
    div.className = 'block ' + (block.type || 'paragraph');
    if (block.type === 'heading') div.className = 'block heading-' + (block.level || 2);
    div.setAttribute('data-block-id', block.id || ('b_' + index));

    if (block.type === 'heading') {
      var h = document.createElement(block.level === 3 ? 'h3' : 'h2');
      h.textContent = block.text || '';
      div.appendChild(h);
    } else if (block.type === 'quote') {
      var bq = document.createElement('blockquote');
      bq.style.margin = '0';
      var t = document.createElement('span');
      t.textContent = '“' + (block.text || '') + '”';
      bq.appendChild(t);
      if (block.speaker) {
        var attrib = document.createElement('span');
        attrib.className = 'quote-attrib';
        attrib.textContent = '— ' + block.speaker;
        bq.appendChild(attrib);
      }
      div.appendChild(bq);
    } else if (block.type === 'list') {
      var listEl = document.createElement(block.ordered ? 'ol' : 'ul');
      (block.items || []).forEach(function(item) {
        var li = document.createElement('li');
        li.textContent = item;
        listEl.appendChild(li);
      });
      div.appendChild(listEl);
    } else {
      var p = document.createElement('p');
      p.textContent = block.text || '';
      div.appendChild(p);
    }

    // Inline claim markers if this block has claims
    var blockId = block.id || ('b_' + index);
    var blockClaims = claimsByBlock[blockId];
    if (blockClaims && blockClaims.length > 0) {
      var markersEl = document.createElement('span');
      markersEl.className = 'claim-markers';
      blockClaims.forEach(function(claim) {
        var marker = document.createElement('button');
        marker.className = 'claim-marker';
        marker.type = 'button';
        marker.setAttribute('data-claim-id', claim._record_id);
        marker.setAttribute('aria-label', 'Claim ' + (claims.indexOf(claim) + 1) + ': jump to in sidebar');
        marker.textContent = String(claims.indexOf(claim) + 1);
        marker.addEventListener('click', function() {
          switchTab('claims');
          jumpToClaim(claim._record_id);
        });
        markersEl.appendChild(marker);
      });
      // Append markers to last child if paragraph, else to div
      var target = (block.type === 'paragraph' || !block.type) ? div.querySelector('p') : div;
      target.appendChild(markersEl);
    }

    return div;
  }

  // --- Claims panel ---
  function renderClaims() {
    els.claimsList.innerHTML = '';
    var filter = userState.filter;
    var visible = 0;

    claims.forEach(function(claim, i) {
      var verdict = userState.verdicts[claim._record_id];
      if (!matchesClaimFilter(verdict, filter)) return;
      visible++;

      var card = document.createElement('article');
      card.className = 'claim-card';
      card.setAttribute('data-claim-card', claim._record_id);
      if (verdict) card.setAttribute('data-verdict', verdict);

      var header = document.createElement('div');
      header.className = 'claim-header';
      var num = document.createElement('span');
      num.className = 'claim-number';
      num.textContent = 'Claim ' + (i + 1);
      header.appendChild(num);
      if (claim.category) {
        var sep = document.createElement('span'); sep.textContent = '·'; header.appendChild(sep);
        var cat = document.createElement('span'); cat.textContent = claim.category; header.appendChild(cat);
      }
      if (claim.confidence) {
        var sep2 = document.createElement('span'); sep2.textContent = '·'; header.appendChild(sep2);
        var conf = document.createElement('span'); conf.textContent = 'confidence ' + claim.confidence; header.appendChild(conf);
      }
      card.appendChild(header);

      var text = document.createElement('div');
      text.className = 'claim-text';
      text.textContent = claim.text || '';
      card.appendChild(text);

      var actions = document.createElement('div');
      actions.className = 'claim-actions';

      var verdictLabels = {
        approve: 'Verified',
        reject: 'Disputed',
        defer: 'Needs check',
        skip: 'No opinion'
      };
      ['approve', 'reject', 'defer', 'skip'].forEach(function(v) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'verdict-btn';
        btn.setAttribute('data-verdict', v);
        btn.textContent = verdictLabels[v];
        if (verdict === v) btn.classList.add('active');
        btn.addEventListener('click', function() {
          setVerdict(claim._record_id, v);
        });
        actions.appendChild(btn);
      });

      var noteToggle = document.createElement('button');
      noteToggle.type = 'button';
      noteToggle.className = 'claim-note-toggle';
      var hasNote = !!userState.claimNotes[claim._record_id];
      noteToggle.textContent = hasNote ? 'Edit note' : '+ Note';
      actions.appendChild(noteToggle);
      card.appendChild(actions);

      var noteArea = document.createElement('div');
      noteArea.className = 'claim-note-area';
      if (hasNote) noteArea.classList.add('visible');
      var noteTextarea = document.createElement('textarea');
      noteTextarea.placeholder = 'Optional note on this claim...';
      noteTextarea.setAttribute('aria-label', 'Note on claim ' + (i + 1));
      noteTextarea.value = userState.claimNotes[claim._record_id] || '';
      noteTextarea.addEventListener('input', function() {
        var v = this.value.trim();
        if (v) userState.claimNotes[claim._record_id] = v;
        else delete userState.claimNotes[claim._record_id];
        noteToggle.textContent = v ? 'Edit note' : '+ Note';
      });
      noteArea.appendChild(noteTextarea);
      card.appendChild(noteArea);

      noteToggle.addEventListener('click', function() {
        var nowVisible = noteArea.classList.toggle('visible');
        if (nowVisible) noteTextarea.focus();
      });

      if (claim.block_id) {
        var jump = document.createElement('button');
        jump.type = 'button';
        jump.className = 'claim-jump';
        jump.textContent = '↑ See in article';
        jump.addEventListener('click', function() { jumpToBlock(claim.block_id); });
        card.appendChild(jump);
      }

      els.claimsList.appendChild(card);
    });

    if (visible === 0) {
      var empty = document.createElement('div');
      empty.style.color = 'var(--color-text-muted)';
      empty.style.fontSize = '0.85rem';
      empty.style.padding = '0.5rem';
      empty.textContent = 'No claims match the current filter.';
      els.claimsList.appendChild(empty);
    }

    updateClaimsSummary();
  }

  function matchesClaimFilter(verdict, filter) {
    if (filter === 'all') return true;
    if (filter === 'pending') return !verdict;
    return verdict === filter;
  }

  function updateClaimsSummary() {
    var counts = { approve: 0, reject: 0, defer: 0, skip: 0 };
    claims.forEach(function(c) {
      var v = userState.verdicts[c._record_id];
      if (v && counts.hasOwnProperty(v)) counts[v]++;
    });
    var marked = counts.approve + counts.reject + counts.defer + counts.skip;
    var pending = claims.length - marked;

    els.claimsSummary.innerHTML = '';
    [
      { label: 'Verified', count: counts.approve, dot: 'approve' },
      { label: 'Disputed', count: counts.reject, dot: 'reject' },
      { label: 'Needs check', count: counts.defer, dot: 'defer' },
      { label: 'No opinion', count: counts.skip, dot: 'skip' },
      { label: 'Pending', count: pending, dot: 'pending' }
    ].forEach(function(stat) {
      var s = document.createElement('span');
      s.className = 'stat';
      var dot = document.createElement('span');
      dot.className = 'stat-dot ' + stat.dot;
      var b = document.createElement('strong');
      b.textContent = stat.count;
      s.appendChild(dot);
      s.appendChild(b);
      s.appendChild(document.createTextNode(' ' + stat.label));
      els.claimsSummary.appendChild(s);
    });
  }

  function setVerdict(claimId, verdict) {
    var current = userState.verdicts[claimId];
    if (current === verdict) {
      delete userState.verdicts[claimId];
    } else {
      userState.verdicts[claimId] = verdict;
    }
    updateClaimMarkersInArticle(claimId);
    renderClaims();
  }

  function updateClaimMarkersInArticle(claimId) {
    var verdict = userState.verdicts[claimId];
    var markers = document.querySelectorAll('.claim-marker[data-claim-id="' + claimId + '"]');
    markers.forEach(function(m) {
      if (verdict) m.setAttribute('data-verdict', verdict);
      else m.removeAttribute('data-verdict');
    });
  }

  function jumpToClaim(claimId) {
    var card = document.querySelector('[data-claim-card="' + claimId + '"]');
    if (!card) return;
    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    card.classList.remove('flash');
    void card.offsetWidth;
    card.classList.add('flash');
  }

  function jumpToBlock(blockId) {
    var block = document.querySelector('[data-block-id="' + blockId + '"]');
    if (!block) return;
    block.scrollIntoView({ behavior: 'smooth', block: 'center' });
    block.classList.remove('highlighted');
    void block.offsetWidth;
    block.classList.add('highlighted');
    setTimeout(function() { block.classList.remove('highlighted'); }, 2000);
  }

  // --- Entities panel ---
  function renderEntities() {
    els.entitiesList.innerHTML = '';
    entities.forEach(function(ent) {
      var card = document.createElement('div');
      card.className = 'entity-card';
      var name = document.createElement('span');
      name.className = 'entity-name';
      name.textContent = ent.name;
      card.appendChild(name);
      if (ent.entity_type) {
        var type = document.createElement('span');
        type.className = 'entity-type';
        type.textContent = ent.entity_type;
        card.appendChild(type);
      }
      if (ent.mention_block_ids && ent.mention_block_ids.length) {
        var mentions = document.createElement('div');
        mentions.className = 'entity-mentions';
        mentions.textContent = ent.mention_block_ids.length +
          (ent.mention_block_ids.length === 1 ? ' mention' : ' mentions') + ' in the article';
        card.appendChild(mentions);
      }
      if (ent.context) {
        var ctx = document.createElement('div');
        ctx.className = 'entity-context';
        ctx.textContent = ent.context;
        card.appendChild(ctx);
      }
      els.entitiesList.appendChild(card);
    });
    if (entities.length === 0) {
      var empty = document.createElement('div');
      empty.style.color = 'var(--color-text-muted)';
      empty.style.fontSize = '0.85rem';
      empty.textContent = 'No entities tagged.';
      els.entitiesList.appendChild(empty);
    }
  }

  // --- Sources panel ---
  function renderSources() {
    els.sourcesList.innerHTML = '';
    sources.forEach(function(src) {
      var card = document.createElement('div');
      card.className = 'source-card';
      var name = document.createElement('div');
      name.className = 'source-name';
      name.textContent = src.name;
      card.appendChild(name);
      if (src.description) {
        var d = document.createElement('div');
        d.className = 'source-description';
        d.textContent = src.description;
        card.appendChild(d);
      }
      els.sourcesList.appendChild(card);
    });
    if (sources.length === 0) {
      var empty = document.createElement('div');
      empty.style.color = 'var(--color-text-muted)';
      empty.style.fontSize = '0.85rem';
      empty.textContent = 'No cited sources tagged.';
      els.sourcesList.appendChild(empty);
    }
  }

  // --- Tab switching ---
  function switchTab(tabName) {
    userState.sidebarTab = tabName;
    document.querySelectorAll('.sidebar-tab').forEach(function(t) {
      var active = t.getAttribute('data-tab') === tabName;
      t.classList.toggle('active', active);
      t.setAttribute('aria-selected', active ? 'true' : 'false');
    });
    document.querySelectorAll('.sidebar-panel').forEach(function(p) {
      p.hidden = p.id !== ('panel-' + tabName);
      p.classList.toggle('active', p.id === ('panel-' + tabName));
    });
  }

  document.querySelectorAll('.sidebar-tab').forEach(function(tab) {
    tab.addEventListener('click', function() {
      switchTab(this.getAttribute('data-tab'));
    });
  });

  // --- Toolbar wiring ---
  els.btnToggleSidebar.addEventListener('click', function() {
    userState.sidebarOpen = !userState.sidebarOpen;
    els.layout.classList.toggle('sidebar-collapsed', !userState.sidebarOpen);
    this.setAttribute('aria-pressed', userState.sidebarOpen ? 'true' : 'false');
  });

  els.filterSelect.addEventListener('change', function() {
    userState.filter = this.value;
    renderClaims();
  });

  els.btnCopyJson.addEventListener('click', function() {
    copyText(JSON.stringify(data, null, 2), 'Capsule data copied as JSON');
  });

  els.btnCopyMd.addEventListener('click', function() {
    copyText(buildMarkdown(), 'Article copied as Markdown');
  });

  els.btnPrint.addEventListener('click', function() {
    window.print();
  });

  els.btnExport.addEventListener('click', function() {
    var decisions = [];
    claims.forEach(function(c) {
      var v = userState.verdicts[c._record_id];
      var note = userState.claimNotes[c._record_id];
      if (v || note) {
        var entry = { record_id: c._record_id };
        if (v) entry.verdict = v;
        if (note) entry.note = note;
        decisions.push(entry);
      }
    });

    var response = {
      response_schema_version: '0.1.0',
      capsule_reference: {
        uuid: manifest.uuid,
        capsule_version: manifest.capsule_version || manifest.artifact_version,
        snapshot_id: manifest.source.snapshot_id
      },
      response: {
        type: 'decision',
        created_at: new Date().toISOString(),
        created_by: 'recipient',
        payload: { decisions: decisions }
      }
    };
    if (userState.summaryNotes.trim()) {
      response.response.payload.summary_notes = userState.summaryNotes.trim();
    }
    downloadJson(response, slug(article.title || manifest.uuid) + '-response-' + Date.now() + '.json');
    showToast('Response exported');
  });

  els.summaryNotes.addEventListener('input', function() {
    userState.summaryNotes = this.value;
  });

  // --- Tab counts ---
  els.countClaims.textContent = claims.length;
  els.countEntities.textContent = entities.length;
  els.countSources.textContent = sources.length;

  // --- About panel ---
  els.aboutContent.textContent = JSON.stringify(manifest, null, 2);

  // --- Build markdown export ---
  function buildMarkdown() {
    var md = '# ' + (article.title || 'Untitled') + '\n\n';
    if (article.subtitle) md += '*' + article.subtitle + '*\n\n';
    md += 'By ' + (article.byline || 'Unknown');
    if (article.publisher) md += ' · ' + article.publisher;
    if (article.published_at) md += ' · ' + formatDate(article.published_at);
    md += '\n\n';
    if (article.url) md += '<' + article.url + '>\n\n';
    md += '---\n\n';

    (article.blocks || []).forEach(function(b) {
      if (b.type === 'heading') {
        var h = b.level === 3 ? '### ' : '## ';
        md += h + (b.text || '') + '\n\n';
      } else if (b.type === 'quote') {
        md += '> ' + (b.text || '') + '\n';
        if (b.speaker) md += '> — ' + b.speaker + '\n';
        md += '\n';
      } else if (b.type === 'list') {
        (b.items || []).forEach(function(item, i) {
          md += (b.ordered ? (i + 1) + '. ' : '- ') + item + '\n';
        });
        md += '\n';
      } else {
        md += (b.text || '') + '\n\n';
      }
    });

    if (claims.length) {
      md += '\n---\n\n## Extracted claims\n\n';
      claims.forEach(function(c, i) {
        md += (i + 1) + '. ' + (c.text || '');
        var v = userState.verdicts[c._record_id];
        if (v) md += ' **[' + v + ']**';
        var n = userState.claimNotes[c._record_id];
        if (n) md += '\n   _' + n + '_';
        md += '\n';
      });
    }
    return md;
  }

  // --- Utilities ---
  function formatDate(iso) {
    try {
      var d = new Date(iso);
      return d.toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
    } catch (e) { return iso; }
  }
  function slug(s) { return (s || 'capsule').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 50); }

  function copyText(text, successMessage) {
    var done = function() { showToast(successMessage); };
    var failed = function() { showToast('Copy failed — select manually'); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done).catch(function() { fallbackCopy(text, done, failed); });
    } else {
      fallbackCopy(text, done, failed);
    }
  }

  function fallbackCopy(text, ok, ko) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.cssText = 'position:fixed;left:-9999px;top:0;opacity:0';
    document.body.appendChild(ta);
    ta.select();
    try {
      var success = document.execCommand('copy');
      document.body.removeChild(ta);
      if (success) ok(); else ko();
    } catch (e) {
      document.body.removeChild(ta);
      ko();
    }
  }

  function downloadJson(obj, filename) {
    var blob = new Blob([JSON.stringify(obj, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(function() { document.body.removeChild(a); URL.revokeObjectURL(url); }, 0);
  }

  var toastTimer;
  function showToast(msg) {
    els.toast.textContent = msg;
    els.toast.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function() { els.toast.classList.remove('visible'); }, 2000);
  }

  // --- Initial render ---
  renderClaims();
  renderEntities();
  renderSources();
})();
