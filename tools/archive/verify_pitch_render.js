const fs = require('fs');
const html = fs.readFileSync('Dashboard_Fanta_1000.html', 'utf8');

const mockElement = (id) => ({
    id: id || '',
    classList: { add: () => {}, remove: () => {} },
    appendChild: () => {},
    style: {},
    innerHTML: '',
    textContent: '',
    value: 'Atalanta'
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
console.log('Testing renderPitchTeam for Atalanta...');
renderPitchTeam('Atalanta');
console.log('renderPitchTeam(Atalanta): SUCCESS');
console.log('Testing renderPitchTeam for Inter...');
renderPitchTeam('Inter');
console.log('renderPitchTeam(Inter): SUCCESS');
console.log('Testing renderPitchTeam for Juventus...');
renderPitchTeam('Juventus');
console.log('renderPitchTeam(Juventus): SUCCESS');
`);
