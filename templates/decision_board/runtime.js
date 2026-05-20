(function() {
  'use strict';

  // --- Parse canonical data (read-only) ---
  var manifest = JSON.parse(document.getElementById('capsule-manifest').textContent);
  var data = JSON.parse(document.getElementById('capsule-data').textContent);

  // --- User state lives in memory only ---
  var userState = {
    decisions: {},   // record_id -> "approve" | "reject" | "defer" | "skip"
    notes: {},       // record_id -> note string
    summaryNotes: '',
    filter: 'all',
    groupBy: 'category',
    sortBy: 'default'
  };

  var DECISION_ORDER = { 'approve': 0, 'reject': 1, 'defer': 2, 'skip': 3 };

  // --- DOM refs ---
  var $ = function(id) { return document.getElementById(id); };
  var els = {
    title: $('header-title'),
    description: $('header-description'),
    meta: $('header-meta'),
    cards: $('cards-container'),
    progressStats: $('progress-stats'),
    progressFill: $('progress-fill'),
    groupSelect: $('group-select'),
    sortSelect: $('sort-select'),
    filterSelect: $('filter-select'),
    btnClear: $('btn-bulk-clear'),
    btnExport: $('btn-export'),
    btnCopyJson: $('btn-copy-json'),
    btnPrint: $('btn-print'),
    summaryNotes: $('summary-notes'),
    aboutContent: $('about-content'),
    toast: $('toast')
  };

  // --- Render header ---
  els.title.textContent = manifest.title;
  els.description.textContent = manifest.description;
  els.meta.innerHTML = '';
  [
    'v' + (manifest.capsule_version || manifest.artifact_version),
    'Spec ' + manifest.spec_version,
    manifest.created_at.split('T')[0],
    manifest.source.included_records + ' options'
  ].forEach(function(label) {
    var span = document.createElement('span');
    span.textContent = label;
    els.meta.appendChild(span);
  });

  // --- Sort a record list (stable, non-mutating) ---
  function sortRecords(records) {
    var mode = userState.sortBy;
    if (mode === 'default') return records;
    var sorted = records.slice();
    sorted.sort(function(a, b) {
      if (mode === 'title-asc') return cmp(a.title, b.title);
      if (mode === 'title-desc') return cmp(b.title, a.title);
      if (mode === 'category') return cmp(a.category || '~', b.category || '~') || cmp(a.title, b.title);
      if (mode === 'decision') {
        var da = userState.decisions[a._record_id];
        var db = userState.decisions[b._record_id];
        var oa = da in DECISION_ORDER ? DECISION_ORDER[da] : 99;
        var ob = db in DECISION_ORDER ? DECISION_ORDER[db] : 99;
        return oa - ob || cmp(a.title, b.title);
      }
      return 0;
    });
    return sorted;
  }
  function cmp(a, b) { return a < b ? -1 : a > b ? 1 : 0; }

  // --- Render cards (grouped or flat) ---
  function render() {
    els.cards.innerHTML = '';
    var records = sortRecords(data.records);
    var groupBy = userState.groupBy;
    var filter = userState.filter;

    // Group
    var groups;
    if (groupBy === 'none') {
      groups = [{ name: null, records: records }];
    } else if (groupBy === 'decision') {
      var byDecision = {};
      records.forEach(function(rec) {
        var dec = userState.decisions[rec._record_id] || 'pending';
        if (!byDecision[dec]) byDecision[dec] = [];
        byDecision[dec].push(rec);
      });
      var order = ['pending', 'approve', 'reject', 'defer', 'skip'];
      groups = order.filter(function(k) { return byDecision[k]; }).map(function(k) {
        return { name: capitalize(k), records: byDecision[k] };
      });
    } else {
      // group by field (default: category)
      var byField = {};
      records.forEach(function(rec) {
        var key = rec[groupBy] || 'Uncategorized';
        if (!byField[key]) byField[key] = [];
        byField[key].push(rec);
      });
      groups = Object.keys(byField).sort().map(function(k) {
        return { name: k, records: byField[k] };
      });
    }

    // Render groups + cards
    groups.forEach(function(group) {
      var visibleInGroup = group.records.filter(function(rec) {
        return matchesFilter(rec, filter);
      });
      if (visibleInGroup.length === 0) return;

      var groupSection = document.createElement('div');
      groupSection.className = 'group-section';

      if (group.name) {
        var hdr = document.createElement('div');
        hdr.className = 'group-header';
        var h2 = document.createElement('h2');
        h2.textContent = group.name;
        var count = document.createElement('span');
        count.className = 'group-count';
        count.textContent = visibleInGroup.length + (visibleInGroup.length === 1 ? ' option' : ' options');
        hdr.appendChild(h2);
        hdr.appendChild(count);
        groupSection.appendChild(hdr);
      }

      visibleInGroup.forEach(function(rec) {
        groupSection.appendChild(renderCard(rec));
      });

      els.cards.appendChild(groupSection);
    });

    if (els.cards.children.length === 0) {
      var empty = document.createElement('div');
      empty.style.padding = '2rem';
      empty.style.textAlign = 'center';
      empty.style.color = 'var(--color-text-muted)';
      empty.textContent = 'No options match the current filter.';
      els.cards.appendChild(empty);
    }

    updateProgress();
  }

  function matchesFilter(rec, filter) {
    var dec = userState.decisions[rec._record_id];
    if (filter === 'all') return true;
    if (filter === 'pending') return !dec;
    return dec === filter;
  }

  function renderCard(rec) {
    var card = document.createElement('article');
    card.className = 'card';
    card.setAttribute('data-record-id', rec._record_id);
    var currentDecision = userState.decisions[rec._record_id];
    if (currentDecision) card.setAttribute('data-decision', currentDecision);

    // Header
    var header = document.createElement('div');
    header.className = 'card-header';
    var titleBlock = document.createElement('div');
    titleBlock.className = 'card-title-block';
    var title = document.createElement('div');
    title.className = 'card-title';
    title.textContent = rec.title;
    titleBlock.appendChild(title);
    if (rec.category) {
      var cat = document.createElement('div');
      cat.className = 'card-category';
      cat.textContent = rec.category;
      titleBlock.appendChild(cat);
    }
    header.appendChild(titleBlock);
    card.appendChild(header);

    // Description
    if (rec.description) {
      var desc = document.createElement('p');
      desc.className = 'card-description';
      desc.textContent = rec.description;
      card.appendChild(desc);
    }

    // Context
    if (rec.context) {
      var ctx = document.createElement('div');
      ctx.className = 'context-block';
      var label = document.createElement('strong');
      label.textContent = 'Context: ';
      ctx.appendChild(label);
      ctx.appendChild(document.createTextNode(rec.context));
      card.appendChild(ctx);
    }

    // Evidence grid
    var hasFor = Array.isArray(rec.evidence_for) && rec.evidence_for.length > 0;
    var hasAgainst = Array.isArray(rec.evidence_against) && rec.evidence_against.length > 0;
    if (hasFor || hasAgainst) {
      var grid = document.createElement('div');
      grid.className = 'evidence-grid';
      if (hasFor) grid.appendChild(renderEvidence('For', rec.evidence_for));
      if (hasAgainst) grid.appendChild(renderEvidence('Against', rec.evidence_against));
      card.appendChild(grid);
    }

    // Decision bar
    var bar = document.createElement('div');
    bar.className = 'decision-bar';
    bar.setAttribute('role', 'group');
    bar.setAttribute('aria-label', 'Decision for ' + rec.title);

    ['approve', 'reject', 'defer', 'skip'].forEach(function(choice) {
      var btn = document.createElement('button');
      btn.className = 'decision-btn';
      btn.setAttribute('data-choice', choice);
      btn.setAttribute('type', 'button');
      btn.textContent = capitalize(choice);
      if (currentDecision === choice) btn.classList.add('active');
      btn.addEventListener('click', function() {
        setDecision(rec._record_id, choice, card, bar);
      });
      bar.appendChild(btn);
    });

    var noteToggle = document.createElement('button');
    noteToggle.className = 'note-toggle';
    noteToggle.type = 'button';
    var hasNote = !!userState.notes[rec._record_id];
    noteToggle.textContent = hasNote ? 'Edit note' : '+ Add note';
    bar.appendChild(noteToggle);
    card.appendChild(bar);

    // Note area
    var noteArea = document.createElement('div');
    noteArea.className = 'note-area';
    if (hasNote) noteArea.classList.add('visible');
    var noteTextarea = document.createElement('textarea');
    noteTextarea.placeholder = 'Optional note explaining your decision...';
    noteTextarea.setAttribute('aria-label', 'Note for ' + rec.title);
    noteTextarea.value = userState.notes[rec._record_id] || '';
    noteTextarea.addEventListener('input', function() {
      var val = this.value.trim();
      if (val) {
        userState.notes[rec._record_id] = val;
      } else {
        delete userState.notes[rec._record_id];
      }
      noteToggle.textContent = val ? 'Edit note' : '+ Add note';
    });
    noteArea.appendChild(noteTextarea);
    card.appendChild(noteArea);

    noteToggle.addEventListener('click', function() {
      var nowVisible = noteArea.classList.toggle('visible');
      if (nowVisible) noteTextarea.focus();
    });

    return card;
  }

  function renderEvidence(label, items) {
    var block = document.createElement('div');
    block.className = 'evidence-block';
    var lbl = document.createElement('div');
    lbl.className = 'evidence-label';
    lbl.textContent = label;
    block.appendChild(lbl);
    var ul = document.createElement('ul');
    items.forEach(function(item) {
      var li = document.createElement('li');
      li.textContent = item;
      ul.appendChild(li);
    });
    block.appendChild(ul);
    return block;
  }

  function setDecision(recordId, choice, cardEl, barEl) {
    var current = userState.decisions[recordId];
    if (current === choice) {
      delete userState.decisions[recordId];
      cardEl.removeAttribute('data-decision');
    } else {
      userState.decisions[recordId] = choice;
      cardEl.setAttribute('data-decision', choice);
    }
    barEl.querySelectorAll('.decision-btn').forEach(function(btn) {
      btn.classList.toggle('active', btn.getAttribute('data-choice') === userState.decisions[recordId]);
    });
    updateProgress();
    if (userState.groupBy === 'decision' || userState.filter !== 'all') {
      render();
    }
  }

  function updateProgress() {
    var total = data.records.length;
    var counts = { approve: 0, reject: 0, defer: 0, skip: 0 };
    data.records.forEach(function(rec) {
      var d = userState.decisions[rec._record_id];
      if (d && counts.hasOwnProperty(d)) counts[d]++;
    });
    var decided = counts.approve + counts.reject + counts.defer + counts.skip;
    var pending = total - decided;

    els.progressStats.innerHTML = '';
    [
      { label: 'Approved', count: counts.approve, dot: 'approve' },
      { label: 'Rejected', count: counts.reject, dot: 'reject' },
      { label: 'Deferred', count: counts.defer, dot: 'defer' },
      { label: 'Skipped', count: counts.skip, dot: 'skip' },
      { label: 'Pending', count: pending, dot: 'pending' }
    ].forEach(function(stat) {
      var span = document.createElement('span');
      span.className = 'stat';
      var dot = document.createElement('span');
      dot.className = 'stat-dot ' + stat.dot;
      var strong = document.createElement('strong');
      strong.textContent = stat.count;
      span.appendChild(dot);
      span.appendChild(strong);
      span.appendChild(document.createTextNode(' ' + stat.label));
      els.progressStats.appendChild(span);
    });

    var pct = total > 0 ? (decided / total) * 100 : 0;
    els.progressFill.style.width = pct + '%';
  }

  // --- Toolbar wiring ---
  els.groupSelect.addEventListener('change', function() {
    userState.groupBy = this.value;
    render();
  });
  els.sortSelect.addEventListener('change', function() {
    userState.sortBy = this.value;
    render();
  });
  els.filterSelect.addEventListener('change', function() {
    userState.filter = this.value;
    render();
  });
  els.btnClear.addEventListener('click', function() {
    if (Object.keys(userState.decisions).length === 0 && Object.keys(userState.notes).length === 0) {
      showToast('Nothing to clear');
      return;
    }
    if (!window.confirm('Clear all decisions and notes? This cannot be undone.')) return;
    userState.decisions = {};
    userState.notes = {};
    render();
    showToast('Decisions cleared');
  });
  els.btnCopyJson.addEventListener('click', function() {
    copyText(JSON.stringify(data, null, 2), 'Data copied as JSON');
  });
  els.btnPrint.addEventListener('click', function() {
    window.print();
  });
  els.summaryNotes.addEventListener('input', function() {
    userState.summaryNotes = this.value;
  });

  // --- Export response ---
  els.btnExport.addEventListener('click', function() {
    var decisions = [];
    data.records.forEach(function(rec) {
      var verdict = userState.decisions[rec._record_id];
      var note = userState.notes[rec._record_id];
      if (verdict || note) {
        var entry = { record_id: rec._record_id };
        if (verdict) entry.verdict = verdict;
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
        payload: {
          decisions: decisions
        }
      }
    };
    if (userState.summaryNotes.trim()) {
      response.response.payload.summary_notes = userState.summaryNotes.trim();
    }

    downloadJson(response, slug(manifest.title) + '-response-' + Date.now() + '.json');
    showToast('Response exported');
  });

  // --- About panel ---
  els.aboutContent.textContent = JSON.stringify(manifest, null, 2);

  // --- Utilities ---
  function capitalize(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
  function slug(s) { return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40); }

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
      if (success) { ok(); } else { ko(); }
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
    setTimeout(function() {
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }, 0);
  }

  var toastTimer;
  function showToast(msg) {
    els.toast.textContent = msg;
    els.toast.classList.add('visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function() { els.toast.classList.remove('visible'); }, 2000);
  }

  // --- Initial render ---
  render();
})();
