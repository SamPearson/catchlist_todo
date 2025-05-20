/**
 * Comments functionality for Catchlist Todo App
 */

// Base API URL - will be set by the template
let apiUrl = '';

// Set the API URL from the template
function setApiUrl(url) {
    apiUrl = url;
}

// Get auth token from cookies
function getAuthToken() {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith('auth_token=')) {
            return cookie.substring('auth_token='.length, cookie.length);
        }
    }
    return '';
}

// Load comments for an entity
function loadComments(entityType, entityId, containerId) {
    fetch(`${apiUrl}/comments/${entityType}/${entityId}`, {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + getAuthToken()
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(comments => {
        displayComments(comments, containerId);
    })
    .catch(error => {
        console.error('Error loading comments:', error);
        document.getElementById(containerId).innerHTML = `
            <div class="ui negative message">
                <div class="header">Error Loading Comments</div>
                <p>Could not load comments. Please try again later.</p>
            </div>
        `;
    });
}

// Display comments in a container
function displayComments(comments, containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (comments.length === 0) {
        container.innerHTML = `
            <div class="ui message">
                <p>No comments yet. Add one below.</p>
            </div>
        `;
        return;
    }
    
    const commentsList = document.createElement('div');
    commentsList.className = 'ui comments';
    
    comments.forEach(comment => {
        const commentEl = document.createElement('div');
        commentEl.className = 'comment';
        commentEl.dataset.id = comment.id;
        
        const content = document.createElement('div');
        content.className = 'content';
        
        const author = document.createElement('div');
        author.className = 'author';
        author.textContent = 'You';
        
        const metadata = document.createElement('div');
        metadata.className = 'metadata';
        
        const date = document.createElement('span');
        date.className = 'date';
        date.textContent = comment.created_at;
        
        const text = document.createElement('div');
        text.className = 'text';
        text.textContent = comment.content;
        
        metadata.appendChild(date);
        
        if (comment.rpe) {
            const rpe = document.createElement('span');
            rpe.className = 'ui mini label';
            rpe.textContent = `RPE: ${comment.rpe}/10`;
            metadata.appendChild(rpe);
        }
        
        content.appendChild(author);
        content.appendChild(metadata);
        content.appendChild(text);
        
        const actions = document.createElement('div');
        actions.className = 'actions';
        
        const editLink = document.createElement('a');
        editLink.className = 'edit-comment';
        editLink.textContent = 'Edit';
        editLink.href = '#';
        editLink.addEventListener('click', (e) => {
            e.preventDefault();
            editComment(comment.id, comment.content, comment.rpe);
        });
        
        const deleteLink = document.createElement('a');
        deleteLink.className = 'delete-comment';
        deleteLink.textContent = 'Delete';
        deleteLink.href = '#';
        deleteLink.addEventListener('click', (e) => {
            e.preventDefault();
            deleteComment(comment.id, containerId);
        });
        
        actions.appendChild(editLink);
        actions.appendChild(deleteLink);
        
        content.appendChild(actions);
        commentEl.appendChild(content);
        commentsList.appendChild(commentEl);
    });
    
    container.appendChild(commentsList);
}

// Create a comment form
function createCommentForm(entityType, entityId, containerId) {
    const formId = `comment-form-${entityType}-${entityId}`;
    
    const form = document.createElement('form');
    form.className = 'ui reply form';
    form.id = formId;
    
    form.innerHTML = `
        <div class="field">
            <textarea name="content" placeholder="Add a comment..."></textarea>
        </div>
        <div class="field">
            <label>RPE (Rate of Perceived Exertion) 1-10:</label>
            <select name="rpe" class="ui dropdown">
                <option value="">Optional</option>
                ${Array.from({length: 10}, (_, i) => `<option value="${i+1}">${i+1}</option>`).join('')}
            </select>
        </div>
        <button class="ui blue labeled submit icon button">
            <i class="icon edit"></i> Add Comment
        </button>
    `;
    
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const content = form.elements.content.value.trim();
        const rpe = form.elements.rpe.value;
        
        if (content) {
            submitComment(entityType, entityId, content, rpe, containerId);
            form.reset();
        }
    });
    
    return form;
}

// Submit a new comment
function submitComment(entityType, entityId, content, rpe, containerId) {
    const data = {
        entity_type: entityType,
        entity_id: entityId,
        content: content
    };
    
    if (rpe) {
        data.rpe = parseInt(rpe);
    }
    
    fetch(`${apiUrl}/comments`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + getAuthToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(() => {
        // Reload comments after successful submission
        loadComments(entityType, entityId, containerId);
    })
    .catch(error => {
        console.error('Error submitting comment:', error);
        alert('Could not submit comment. Please try again later.');
    });
}

// Edit a comment
function editComment(commentId, content, rpe) {
    const newContent = prompt('Edit your comment:', content);
    if (newContent === null || newContent.trim() === '') return;
    
    let newRpe = rpe;
    if (rpe) {
        const rpeStr = prompt('Edit RPE (1-10):', rpe);
        if (rpeStr !== null) {
            newRpe = parseInt(rpeStr);
            if (isNaN(newRpe) || newRpe < 1 || newRpe > 10) {
                newRpe = rpe;  // Keep original if invalid
            }
        }
    }
    
    const data = {
        content: newContent.trim()
    };
    
    if (newRpe) {
        data.rpe = newRpe;
    }
    
    fetch(`${apiUrl}/comments/${commentId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + getAuthToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(comment => {
        // Find and update the comment in the DOM
        const commentEl = document.querySelector(`.comment[data-id="${comment.id}"]`);
        if (commentEl) {
            const textEl = commentEl.querySelector('.text');
            if (textEl) textEl.textContent = comment.content;
            
            const rpeEl = commentEl.querySelector('.metadata .ui.mini.label');
            if (rpeEl && comment.rpe) {
                rpeEl.textContent = `RPE: ${comment.rpe}/10`;
            } else if (!rpeEl && comment.rpe) {
                const metadataEl = commentEl.querySelector('.metadata');
                const rpeSpan = document.createElement('span');
                rpeSpan.className = 'ui mini label';
                rpeSpan.textContent = `RPE: ${comment.rpe}/10`;
                metadataEl.appendChild(rpeSpan);
            }
        }
    })
    .catch(error => {
        console.error('Error updating comment:', error);
        alert('Could not update comment. Please try again later.');
    });
}

// Delete a comment
function deleteComment(commentId, containerId) {
    if (!confirm('Are you sure you want to delete this comment?')) return;
    
    fetch(`${apiUrl}/comments/${commentId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': 'Bearer ' + getAuthToken()
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(() => {
        // Remove the comment element from the DOM
        const commentEl = document.querySelector(`.comment[data-id="${commentId}"]`);
        if (commentEl) {
            const commentsContainer = commentEl.closest('.ui.comments');
            commentEl.remove();
            
            // If no more comments, show "no comments" message
            if (commentsContainer && commentsContainer.children.length === 0) {
                document.getElementById(containerId).innerHTML = `
                    <div class="ui message">
                        <p>No comments yet. Add one below.</p>
                    </div>
                `;
            }
        }
    })
    .catch(error => {
        console.error('Error deleting comment:', error);
        alert('Could not delete comment. Please try again later.');
    });
}

// Initialize comments section for an entity
function initializeComments(entityType, entityId, containerSelector) {
    const container = document.querySelector(containerSelector);
    if (!container) return;
    
    // Create container for comments
    const commentsContainerId = `comments-${entityType}-${entityId}`;
    const commentsContainer = document.createElement('div');
    commentsContainer.id = commentsContainerId;
    commentsContainer.className = 'comments-container';
    
    // Add comments section title
    const title = document.createElement('h4');
    title.className = 'ui dividing header';
    title.textContent = 'Comments';
    
    container.appendChild(title);
    container.appendChild(commentsContainer);
    
    // Add comment form
    const commentForm = createCommentForm(entityType, entityId, commentsContainerId);
    container.appendChild(commentForm);
    
    // Load existing comments
    loadComments(entityType, entityId, commentsContainerId);
    
    return commentsContainerId;
} 