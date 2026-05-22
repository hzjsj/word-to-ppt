const API_BASE = 'http://127.0.0.1:8000';

function formatTime(value) {
  return value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '-';
}

function statusBadge(status) {
  return `<span class="badge ${status}">${status}</span>`;
}

async function fetchTasks() {
  const status = document.getElementById('status-filter').value;
  const query = new URLSearchParams({ limit: '100' });
  if (status) query.set('status', status);

  const res = await fetch(`${API_BASE}/tasks?${query.toString()}`);
  const data = await res.json();

  const tbody = document.getElementById('task-body');
  tbody.innerHTML = data.map(task => `
    <tr>
      <td>${task.id}</td>
      <td>${task.filename}</td>
      <td>${task.task_type}</td>
      <td>${statusBadge(task.status)}</td>
      <td>${(task.options || []).join('、')}</td>
      <td>${task.message || '-'}</td>
      <td>${formatTime(task.created_at)}</td>
    </tr>
  `).join('');
}

async function submitTask(event) {
  event.preventDefault();
  const formData = new FormData(event.target);

  let options = [];
  const optionsRaw = formData.get('options')?.trim();
  if (optionsRaw) {
    try {
      options = JSON.parse(optionsRaw);
      if (!Array.isArray(options)) throw new Error();
    } catch {
      alert('options 必须是 JSON 数组，例如 ["设置标题", "更改字体"]');
      return;
    }
  }

  const payload = {
    filename: formData.get('filename'),
    task_type: formData.get('task_type'),
    options,
    message: formData.get('message') || null,
  };

  const res = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const error = await res.text();
    alert(`提交失败: ${error}`);
    return;
  }

  event.target.reset();
  await fetchTasks();
}

document.getElementById('task-form').addEventListener('submit', submitTask);
document.getElementById('refresh-btn').addEventListener('click', fetchTasks);
document.getElementById('status-filter').addEventListener('change', fetchTasks);

fetchTasks();
