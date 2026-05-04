const API = window.location.origin;
const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];

let calYear, calMonth, calEvents = [];

function init() {
  const now = new Date();
  calYear = now.getFullYear();
  calMonth = now.getMonth();
  document.getElementById('topbar-date').textContent = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  loadStats();
  loadEvents();
  loadHistory();
}

async function loadHistory() {
  try {
    const res = await fetch(`${API}/history`);
    const data = await res.json();
    if (!data.emails.length) return;
    renderResults({ processed: data.emails.filter(e => e.status === 'success').length, details: data.emails });
    document.getElementById('stat-last-run').textContent = `${data.emails.length} emails total`;
  } catch (_) {}
}

async function loadStats() {
  try {
    const res = await fetch(`${API}/stats`);
    const data = await res.json();
    document.getElementById('stat-total').textContent = data.total_processed;
  } catch (_) {}
}

async function loadEvents() {
  try {
    const res = await fetch(`${API}/events`);
    const data = await res.json();
    calEvents = data.events || [];
    document.getElementById('stat-events').textContent = calEvents.length;
    renderCalendar();
    renderEventsList();
  } catch (_) {
    calEvents = [];
    renderCalendar();
  }
}

async function fetchEmails() {
  const max = document.getElementById('max-results').value;
  const btn = document.getElementById('fetch-btn');
  const spinner = document.getElementById('spinner');
  const btnText = document.getElementById('btn-text');

  btn.disabled = true;
  btnText.textContent = 'Processing...';
  spinner.style.display = 'inline-block';

  try {
    const res = await fetch(`${API}/fetch?max_results=${max}`);
    const data = await res.json();
    const time = new Date().toLocaleTimeString();
    data.time = time;
    localStorage.setItem('lastRun', JSON.stringify(data));
    renderResults(data);
    loadStats();
    loadEvents();
    document.getElementById('stat-last-run').textContent = `Last run: ${time}`;
  } catch (e) {
    alert('Error connecting to agent: ' + e.message);
  } finally {
    btn.disabled = false;
    btnText.textContent = 'Fetch Now';
    spinner.style.display = 'none';
  }
}

function renderResults(data) {
  document.getElementById('stat-success').textContent = data.processed;
  const errors = data.details.filter(r => r.status === 'error').length;
  document.getElementById('stat-errors').textContent = errors;
  document.getElementById('result-count').textContent = `${data.details.length} emails`;

  const tbody = document.getElementById('results-body');
  if (!data.details.length) {
    tbody.innerHTML = '<tr class="empty-row"><td colspan="3">No new emails to process</td></tr>';
    return;
  }

  tbody.innerHTML = data.details.map(r => `
    <tr>
      <td><div class="subject-cell" title="${r.subject}">${r.subject}</div></td>
      <td>${actionBadge(r.action)}</td>
      <td>${statusBadge(r.status)}</td>
    </tr>
  `).join('');
}

function actionBadge(action) {
  if (action === 'create_event') return '<span class="badge badge-event">Event</span>';
  if (action === 'log_to_sheets') return '<span class="badge badge-log">Sheet</span>';
  return '<span class="badge badge-error">Error</span>';
}

function statusBadge(status) {
  return status === 'success'
    ? '<span class="badge badge-success">Success</span>'
    : '<span class="badge badge-error">Error</span>';
}

// CALENDAR
function changeMonth(dir) {
  calMonth += dir;
  if (calMonth > 11) { calMonth = 0; calYear++; }
  if (calMonth < 0) { calMonth = 11; calYear--; }
  renderCalendar();
}

function renderCalendar() {
  document.getElementById('cal-title').textContent = `${MONTHS[calMonth]} ${calYear}`;

  const today = new Date();
  const firstDay = new Date(calYear, calMonth, 1).getDay();
  const daysInMonth = new Date(calYear, calMonth + 1, 0).getDate();
  const daysInPrev = new Date(calYear, calMonth, 0).getDate();

  const eventDates = new Set(
    calEvents
      .filter(e => {
        const d = new Date(e.date);
        return d.getFullYear() === calYear && d.getMonth() === calMonth;
      })
      .map(e => parseInt(e.date.split('-')[2]))
  );

  const eventsByDate = {};
  calEvents.forEach(e => {
    const d = new Date(e.date);
    if (d.getFullYear() === calYear && d.getMonth() === calMonth) {
      const day = parseInt(e.date.split('-')[2]);
      if (!eventsByDate[day]) eventsByDate[day] = [];
      eventsByDate[day].push(e);
    }
  });

  let html = '';
  // Previous month days
  for (let i = firstDay - 1; i >= 0; i--) {
    html += `<div class="cal-day other-month">${daysInPrev - i}</div>`;
  }
  // Current month days
  for (let d = 1; d <= daysInMonth; d++) {
    const isToday = d === today.getDate() && calMonth === today.getMonth() && calYear === today.getFullYear();
    const hasEvent = eventDates.has(d);
    const eventsTitle = hasEvent ? eventsByDate[d].map(e => e.summary).join(', ') : '';
    const classes = ['cal-day', isToday ? 'today' : '', hasEvent ? 'has-event' : ''].filter(Boolean).join(' ');
    const dot = hasEvent ? '<span class="event-dot"></span>' : '';
    const attrs = hasEvent ? `onmouseenter="showTooltip(event,'${eventsTitle}')" onmouseleave="hideTooltip()"` : '';
    html += `<div class="${classes}" ${attrs}>${d}${dot}</div>`;
  }
  // Next month filler
  const total = firstDay + daysInMonth;
  const remaining = total % 7 === 0 ? 0 : 7 - (total % 7);
  for (let d = 1; d <= remaining; d++) {
    html += `<div class="cal-day other-month">${d}</div>`;
  }

  document.getElementById('cal-days').innerHTML = html;
}

function renderEventsList() {
  const body = document.getElementById('events-list-body');
  if (!calEvents.length) {
    body.innerHTML = '<div class="no-events">No events this month</div>';
    return;
  }
  body.innerHTML = calEvents.map(e => `
    <div class="event-item">
      <div class="event-dot-lg"></div>
      <div>
        <div class="ev-title">${e.summary}</div>
        <div class="ev-date">${formatDate(e.date)}</div>
      </div>
    </div>
  `).join('');
}

function formatDate(dateStr) {
  return new Date(dateStr + 'T12:00:00').toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}

function showTooltip(e, text) {
  const t = document.getElementById('tooltip');
  t.textContent = text;
  t.style.display = 'block';
  t.style.left = (e.clientX + 12) + 'px';
  t.style.top = (e.clientY - 10) + 'px';
}

function hideTooltip() {
  document.getElementById('tooltip').style.display = 'none';
}

init();
