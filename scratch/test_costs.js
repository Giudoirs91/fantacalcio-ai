const fs = require('fs');
const players = JSON.parse(fs.readFileSync('processed_players_master.json', 'utf-8'));
global.PLAYERS = players;
global.State = { systemMode: 'classic' };
global.window = global;
global.document = { getElementById: () => null };
global.isPlayerBought = () => false;
global.isPlayerTakenByOther = () => false;
global.isPlayerAvailable = () => true;

// Read ai_squads.js, replacing const with var so they attach to global/scope
let code = fs.readFileSync('web/js/ai_squads.js', 'utf-8');
code = code.replace(/const AI_SQUADS_DATA/g, 'global.AI_SQUADS_DATA');
code = code.replace(/const MANTRA_AI_SQUADS_DATA/g, 'global.MANTRA_AI_SQUADS_DATA');
code = code.replace(/const REAL_AUCTION_PRICES/g, 'global.REAL_AUCTION_PRICES');
eval(code);

console.log('=== CLASSIC SQUADS ===');
global.AI_SQUADS_DATA.forEach(sq => {
    let tot = 0;
    const details = [];
    ['P','D','C','A'].forEach(r => {
        const names = [...(sq.starters[r] || []), ...(sq.bench[r] || [])];
        names.forEach(n => {
            const p = PLAYERS.find(pl => pl.role === r && pl.name.toLowerCase() === n.toLowerCase()) ||
                      PLAYERS.find(pl => pl.role === r && pl.name.toLowerCase().includes(n.toLowerCase())) ||
                      PLAYERS.find(pl => pl.name.toLowerCase().includes(n.toLowerCase()));
            const cost = p ? getPlayerAuctionCost(p) : 1;
            tot += cost;
            details.push({ n, role: r, found: p ? p.name : 'NOT FOUND', cost, prezzo_cons: p ? p.prezzo_cons : 0 });
        });
    });
    console.log(sq.id, sq.name, 'TOTAL SPENT:', tot);
    if (tot > 1000) {
        console.log('  OVER BUDGET BY:', tot - 1000);
        details.sort((a,b) => b.cost - a.cost).slice(0, 10).forEach(d => console.log('    ', d.n, 'cost:', d.cost, 'prezzo_cons:', d.prezzo_cons));
    }
});

console.log('\n=== MANTRA SQUADS ===');
global.MANTRA_AI_SQUADS_DATA.forEach(sq => {
    let tot = 0;
    const details = [];
    ['P','D','C','A'].forEach(r => {
        const names = [...(sq.starters[r] || []), ...(sq.bench[r] || [])];
        names.forEach(n => {
            const p = PLAYERS.find(pl => pl.role === r && pl.name.toLowerCase() === n.toLowerCase()) ||
                      PLAYERS.find(pl => pl.role === r && pl.name.toLowerCase().includes(n.toLowerCase())) ||
                      PLAYERS.find(pl => pl.name.toLowerCase().includes(n.toLowerCase()));
            const cost = p ? getPlayerAuctionCost(p) : 1;
            tot += cost;
            details.push({ n, role: r, found: p ? p.name : 'NOT FOUND', cost, prezzo_cons: p ? p.prezzo_cons : 0 });
        });
    });
    console.log(sq.id, sq.name, 'TOTAL SPENT:', tot);
    if (tot > 1000) {
        console.log('  OVER BUDGET BY:', tot - 1000);
        details.sort((a,b) => b.cost - a.cost).slice(0, 10).forEach(d => console.log('    ', d.n, 'cost:', d.cost, 'prezzo_cons:', d.prezzo_cons));
    }
});
