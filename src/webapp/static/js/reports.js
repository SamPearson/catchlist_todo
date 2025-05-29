function loadSoftCommittedTasks(period, startDate, endDate) {
    fetch(`/api/commitments/soft/${period}?start=${startDate}&end=${endDate}`)
        .then(response => response.json())
        .then(data => {
            displaySoftCommittedTasks(data);
        })
        .catch(error => {
            console.error('Error loading soft committed tasks:', error);
            showError('Failed to load soft committed tasks');
        });
}

function displaySoftCommittedTasks(tasks) {
    const container = document.getElementById('soft-committed-tasks');
    container.innerHTML = '';
    
    if (tasks.length === 0) {
        container.innerHTML = '<div class="ui placeholder segment"><div class="ui icon header"><i class="tasks icon"></i>No soft committed tasks</div></div>';
        return;
    }
    
    const list = document.createElement('div');
    list.className = 'ui divided list';
    
    tasks.forEach(task => {
        const item = document.createElement('div');
        item.className = 'item';
        
        const content = document.createElement('div');
        content.className = 'content';
        
        const header = document.createElement('div');
        header.className = 'header';
        header.textContent = task.title;
        
        const description = document.createElement('div');
        description.className = 'description';
        description.textContent = task.description || '';
        
        const meta = document.createElement('div');
        meta.className = 'meta';
        
        if (task.project_task) {
            const project = document.createElement('span');
            project.className = 'ui label';
            project.textContent = task.project_task.project.name;
            meta.appendChild(project);
        }
        
        const actions = document.createElement('div');
        actions.className = 'ui buttons';
        
        const completeBtn = document.createElement('button');
        completeBtn.className = `ui icon button ${task.completed ? 'green' : ''}`;
        completeBtn.innerHTML = `<i class="check icon"></i>`;
        completeBtn.onclick = () => toggleSoftCommitmentComplete(task.id, !task.completed);
        
        const checkinsBtn = document.createElement('button');
        checkinsBtn.className = 'ui icon button';
        checkinsBtn.innerHTML = '<i class="history icon"></i>';
        checkinsBtn.onclick = () => showCheckins('soft_commitment', task.id);
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'ui icon button red';
        removeBtn.innerHTML = '<i class="trash icon"></i>';
        removeBtn.onclick = () => removeSoftCommitment(task.id);
        
        actions.appendChild(completeBtn);
        actions.appendChild(checkinsBtn);
        actions.appendChild(removeBtn);
        
        content.appendChild(header);
        content.appendChild(description);
        content.appendChild(meta);
        content.appendChild(actions);
        
        item.appendChild(content);
        list.appendChild(item);
    });
    
    container.appendChild(list);
}

function addSoftCommitment(event) {
    event.preventDefault();
    
    const form = event.target;
    const title = form.querySelector('input[name="title"]').value;
    const description = form.querySelector('textarea[name="description"]').value;
    const period = document.querySelector('.ui.tab.active').dataset.period;
    
    if (!title) {
        showError('Title is required');
        return;
    }
    
    const startDate = getStartDateForPeriod(period);
    const endDate = getEndDateForPeriod(period);
    
    fetch('/api/commitments/soft', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            title,
            description,
            time_period: period,
            start_date: startDate,
            end_date: endDate
        })
    })
    .then(response => response.json())
    .then(data => {
        form.reset();
        loadSoftCommittedTasks(period, startDate, endDate);
    })
    .catch(error => {
        console.error('Error adding soft commitment:', error);
        showError('Failed to add soft commitment');
    });
}

function toggleSoftCommitmentComplete(id, completed) {
    fetch(`/api/commitments/soft/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ completed })
    })
    .then(response => response.json())
    .then(data => {
        const period = document.querySelector('.ui.tab.active').dataset.period;
        const startDate = getStartDateForPeriod(period);
        const endDate = getEndDateForPeriod(period);
        loadSoftCommittedTasks(period, startDate, endDate);
    })
    .catch(error => {
        console.error('Error updating soft commitment:', error);
        showError('Failed to update soft commitment');
    });
}

function removeSoftCommitment(id) {
    if (!confirm('Are you sure you want to remove this soft commitment?')) {
        return;
    }
    
    fetch(`/api/commitments/soft/${id}`, {
        method: 'DELETE'
    })
    .then(() => {
        const period = document.querySelector('.ui.tab.active').dataset.period;
        const startDate = getStartDateForPeriod(period);
        const endDate = getEndDateForPeriod(period);
        loadSoftCommittedTasks(period, startDate, endDate);
    })
    .catch(error => {
        console.error('Error removing soft commitment:', error);
        showError('Failed to remove soft commitment');
    });
}

// Helper functions for date calculations
function getStartDateForPeriod(period) {
    const now = new Date();
    switch (period) {
        case 'week':
            const day = now.getDay();
            const diff = now.getDate() - day + (day === 0 ? -6 : 1);
            return new Date(now.setDate(diff)).toISOString().split('T')[0];
        case 'month':
            return new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
        case 'season':
            const month = now.getMonth();
            const seasonStart = Math.floor(month / 3) * 3;
            return new Date(now.getFullYear(), seasonStart, 1).toISOString().split('T')[0];
        case 'year':
            return new Date(now.getFullYear(), 0, 1).toISOString().split('T')[0];
        default:
            return now.toISOString().split('T')[0];
    }
}

function getEndDateForPeriod(period) {
    const now = new Date();
    switch (period) {
        case 'week':
            const day = now.getDay();
            const diff = now.getDate() - day + (day === 0 ? 0 : 7);
            return new Date(now.setDate(diff)).toISOString().split('T')[0];
        case 'month':
            return new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().split('T')[0];
        case 'season':
            const month = now.getMonth();
            const seasonEnd = Math.floor(month / 3) * 3 + 2;
            return new Date(now.getFullYear(), seasonEnd + 1, 0).toISOString().split('T')[0];
        case 'year':
            return new Date(now.getFullYear(), 11, 31).toISOString().split('T')[0];
        default:
            return now.toISOString().split('T')[0];
    }
}

// Update the loadTabContent function to include soft commitments
function loadTabContent(tab) {
    const period = tab.dataset.period;
    const startDate = getStartDateForPeriod(period);
    const endDate = getEndDateForPeriod(period);
    
    // Show/hide soft committed section based on tab
    const softCommittedSection = document.getElementById('soft-committed-section');
    softCommittedSection.style.display = period === 'day' ? 'none' : 'block';
    
    // Load regular commitments
    loadCommitments(period, startDate, endDate);
    
    // Load soft commitments for non-day tabs
    if (period !== 'day') {
        loadSoftCommittedTasks(period, startDate, endDate);
    }
    
    // Load other content...
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    // ... existing event listeners ...
    
    // Add event listener for soft commitment form
    const softCommitmentForm = document.getElementById('add-soft-commitment-form');
    if (softCommitmentForm) {
        softCommitmentForm.addEventListener('submit', addSoftCommitment);
    }
}); 