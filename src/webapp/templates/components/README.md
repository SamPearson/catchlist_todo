# UI Component Library

This directory contains reusable UI components for the application.

## Available Components

### 1. Display Box
`display_box.html`

A versatile container for organizing content with options for titles, collapsible sections, and tabbed interfaces.

```jinja
{% from "components/display_box.html" import display_box %}

{# Simple box with title #}
{% call display_box(id="my-box", title="Box Title") %}
    <p>Content goes here</p>
{% endcall %}

{# Collapsible box #}
{% call display_box(id="collapsible-box", title="Collapsible Box", collapsible=true) %}
    <p>This content can be collapsed by clicking the arrow in the header</p>
{% endcall %}

{# Tabbed box #}
{% call display_box(id="tabbed-box", title="Tabbed Box", tabs=["Tab 1", "Tab 2", "Tab 3"]) %}
    <div class="ui bottom attached tab segment active" data-tab="tabbed-box-tab-1">
        <p>Content for Tab 1</p>
    </div>
    
    <div class="ui bottom attached tab segment" data-tab="tabbed-box-tab-2">
        <p>Content for Tab 2</p>
    </div>
    
    <div class="ui bottom attached tab segment" data-tab="tabbed-box-tab-3">
        <p>Content for Tab 3</p>
    </div>
{% endcall %}
```

### 2. Slideout Panel
`slideout.html`

A component for hiding content that can be toggled visible with a clickable trigger.

```jinja
{% from "components/slideout.html" import slideout %}

{% call slideout(id="my-slideout", trigger_text="Click to show more") %}
    <p>This content will slide in/out when the trigger is clicked.</p>
{% endcall %}
```

### 3. Check-in Popout
`checkin.html`

A specialized component for logging check-ins on tasks, with comment field, RPE rating, and fireworks animation.

```jinja
{% from "components/checkin.html" import checkin_popout %}

{{ checkin_popout(task_id="task-123") }}
```

### 4. Search Box
`search_box.html`

A search component with an option to show advanced filters.

```jinja
{% from "components/search_box.html" import search_box %}

{% call search_box(id="my-search", placeholder="Search items...") %}
    <div class="field">
        <div class="ui checkbox">
            <input type="checkbox" name="include_archived">
            <label>Include archived</label>
        </div>
    </div>
{% endcall %}
```

### 5. Add Box
`add_box.html`

A form component for adding new items, with support for hidden advanced options.

```jinja
{% from "components/add_box.html" import add_box %}

{% call add_box(id="my-add-box", placeholder="Enter new item...", submit_text="Create") %}
    <div class="field">
        <label>Description</label>
        <textarea name="description" rows="2"></textarea>
    </div>
{% endcall %}
```

### 6. List Box
`list_box.html`

A component for displaying lists of items with loading states, empty messages, and pagination.

```jinja
{% from "components/list_box.html" import list_box %}

{{ list_box(id="my-list", empty_message="No items found") }}
```

## JavaScript API

The List Box component exposes a JavaScript API for controlling its state:

```javascript
// Show loading state
window.listBoxes['my-list'].showLoading();

// Hide loading state
window.listBoxes['my-list'].hideLoading();

// Set items (expects array of HTML strings)
window.listBoxes['my-list'].setItems([
    '<div class="content"><div class="header">Item 1</div></div>',
    '<div class="content"><div class="header">Item 2</div></div>'
]);

// Setup pagination
window.listBoxes['my-list'].setupPagination(1, 5); // currentPage, totalPages
```

## Events

The components emit various events that you can listen for:

```javascript
// Search input changes
document.addEventListener('searchChange', function(e) {
    console.log('Search query:', e.detail.query);
});

// New item added
document.addEventListener('itemAdd', function(e) {
    console.log('New item data:', e.detail.formData);
});

// Pagination page changed
document.addEventListener('pageChange', function(e) {
    console.log('Navigated to page:', e.detail.page);
});
```

## Demo

Visit the `/demo` page to see all components in action. This page can be toggled on/off by setting the `SHOW_DEMO` environment variable to `True` or `False`. 