// Common utility functions

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `ui ${type} message`;
    notification.innerHTML = `
        <i class="close icon"></i>
        <div class="content">
            <p>${message}</p>
        </div>
    `;
    
    // Find the first container that has content
    const container = document.querySelector('.ui.container');
    if (!container) {
        console.error('Could not find container for notification');
        return;
    }
    
    // Insert at the beginning of the container
    container.insertBefore(notification, container.firstChild);
    
    // Add click handler for close button
    const closeButton = notification.querySelector('.close.icon');
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            notification.remove();
        });
    }
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Add any other utility functions here 