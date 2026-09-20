const fs = require('fs');
const html = fs.readFileSync('Dashboard_Fanta_1000.html', 'utf8');

const mockElement = (id) => ({
    id: id || '',
    classList: { add: () => {}, remove: () => {} },
    appendChild: () => {},
    style: {},
    innerHTML: '',
    textContent: '',
    value: 'ALL'
});

global.document = {
    getElementById: (id) => mockElement(id),
    createElement: (tag) => mockElement(tag),
    querySelectorAll: () => []
};
global.window = {
    addEventListener: () => {}
};
global.localStorage = {
    getItem: () => null,
    setItem: () => {},
    removeItem: () => {}
};

const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/g);
const code = scriptMatch[scriptMatch.length - 1].replace(/<\/?script>/g, '');

eval(code + `
console.log('PLAYERS count:', PLAYERS.length);
renderTable();
console.log('renderTable: SUCCESS');
updateBudgetUI();
console.log('updateBudgetUI: SUCCESS');
renderSidebarRoster();
console.log('renderSidebarRoster: SUCCESS');
renderSquadBuilder();
console.log('renderSquadBuilder: SUCCESS');
`);
