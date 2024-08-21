
/* this didn't work */

/*
document.addEventListener('DOMContentLoaded', function() {
    const cyElement = document.getElementById('cytoscape');
    if (cyElement) {
        const cy = cyElement._cyreg.cy;
        cy.on('cxttap', 'node', function(evt) {
            const node = evt.target;
            const event = new CustomEvent('cytoscape:contextmenu', { detail: node.data() });
            window.dispatchEvent(event);
        });
    }
});
*/

/*
document.addEventListener('DOMContentLoaded', function() {
    const cyElement = document.getElementById('cytoscape');
    if (cyElement) {
        cyElement.addEventListener('contextmenu', function(event) {
            event.preventDefault();
            const cy = cyElement._cyreg.cy;
            const node = cy.$(':selected');
            if (node && node.isNode()) {
                const evt = new CustomEvent('cytoscape:contextmenu', { detail: node.data() });
                window.dispatchEvent(evt);
            }
        });
    }
});
*/


