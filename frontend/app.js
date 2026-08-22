const $ = id => document.getElementById(id);
let pending = null;

const setTimeline = values => document.querySelectorAll('#timeline b').forEach((node, index) => {
  node.textContent = values[index] ?? '—';
});

function render(result) {
  const approval = result.decision === 'REQUIRE_APPROVAL';
  const completed = result.lifecycle === 'COMPLETED';
  const denied = result.decision === 'DENY';
  $('decision').textContent = result.decision;
  $('badge').textContent = completed ? 'COMPLETED' : approval ? 'AWAITING APPROVAL' : result.decision === 'ALLOW' ? 'AUTHORIZED' : 'BLOCKED';
  $('risk').textContent = `${result.risk_level} · ${result.risk_score}/100`;
  $('riskReason').textContent = (result.reasons || []).join(' · ') || 'No policy reasons returned';
  $('requestId').textContent = result.request_id || '—';
  $('evidenceId').textContent = result.evidence_id || '—';
  $('reasoning').textContent = result.agent_reasoning || 'Gemini reasoning unavailable; deterministic policy remains authoritative.';
  setTimeline(['✓', '✓', denied ? '✕' : '✓', approval ? 'PENDING' : '✓', completed ? '✓' : '—', result.evidence_id ? '✓' : '—']);
  $('evidence').textContent = JSON.stringify(result, null, 2);
  $('approval').hidden = !approval;
  $('approve').disabled = !approval;
  $('reject').disabled = !approval;
  $('audit').disabled = !result.evidence_id;
}

async function readJson(response) {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || `request_failed_${response.status}`);
  return body;
}

async function run() {
  const button = $('run');
  $('error').textContent = '';
  button.disabled = true;
  button.textContent = 'Evaluating…';
  const request = {
    request_id: `req-${crypto.randomUUID()}`,
    agent_id: $('agent').value.trim(),
    credential_id: $('credential').value.trim(),
    tool: 'invoice_db',
    action: $('action').value,
    resource: 'invoices',
    requested_scope: Number($('scope').value),
    context: { external: $('external').checked, sensitive: $('sensitive').checked }
  };
  try {
    pending = await readJson(await fetch('/api/v1/decisions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Request-ID': request.request_id },
      body: JSON.stringify(request)
    }));
    render(pending);
  } catch (error) {
    $('decision').textContent = 'ERROR';
    $('badge').textContent = 'FAILED';
    $('error').textContent = error.message || 'Unexpected error';
  } finally {
    button.disabled = false;
    button.textContent = 'Evaluate action';
  }
}

async function resolve(approved) {
  if (!pending?.approval_id) return;
  $('error').textContent = '';
  $('approve').disabled = true;
  $('reject').disabled = true;
  try {
    pending = await readJson(await fetch(`/api/v1/approvals/${pending.approval_id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        approved,
        approver: $('approver').value.trim(),
        reason: approved ? 'Verified by human reviewer' : 'Rejected by human reviewer'
      })
    }));
    render(pending);
  } catch (error) {
    $('error').textContent = error.message || 'Approval failed';
    $('approve').disabled = false;
    $('reject').disabled = false;
  }
}

async function inspectAudit() {
  if (!pending?.evidence_id) return;
  $('audit').disabled = true;
  $('audit').textContent = 'Checking…';
  $('error').textContent = '';
  try {
    const audit = await readJson(await fetch(`/api/v1/audit/${pending.evidence_id}`));
    $('evidence').textContent = JSON.stringify(audit, null, 2);
    const integrity = await readJson(await fetch('/api/v1/audit/integrity'));
    $('integrity').textContent = integrity.valid ? `AUDIT INTEGRITY VERIFIED · ${integrity.events} EVENTS` : `AUDIT INTEGRITY BROKEN AT EVENT ${integrity.broken_at}`;
  } catch (error) {
    $('error').textContent = error.message || 'Audit lookup failed';
  } finally {
    $('audit').disabled = false;
    $('audit').textContent = 'Inspect evidence';
  }
}

$('run').addEventListener('click', run);
$('approve').addEventListener('click', () => resolve(true));
$('reject').addEventListener('click', () => resolve(false));
$('audit').addEventListener('click', inspectAudit);
