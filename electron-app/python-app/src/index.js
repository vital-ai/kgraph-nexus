import { contextMenus } from './cytoscape-context-menus.js';

let register = function(cytoscape) {
    if (!cytoscape) {
        return;
    } // can't register if cytoscape unspecified

    cytoscape('core', 'contextMenus', contextMenus);
};

if (typeof cytoscape !== 'undefined') {
    // Register for plain javascript
    register(cytoscape);
}

export default register;