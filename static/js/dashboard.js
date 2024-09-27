const socket = io();

socket.on('connect', function() {
    console.log('Connected to server');
});

socket.on('update_data', function(data) {
    updateDashboard(data);
});

function updateDashboard(data) {
    const dashboardElement = document.getElementById('dashboard');
    dashboardElement.innerHTML = '';

    const bunkersContainer = document.createElement('div');
    bunkersContainer.className = 'bunkers-container';

    Object.entries(data).forEach(([bunkerId, bunkerData]) => {
        const bunkerElement = createBunkerElement(bunkerId, bunkerData);
        bunkersContainer.appendChild(bunkerElement);
    });

    dashboardElement.appendChild(bunkersContainer);
}

function createBunkerElement(bunkerId, bunker) {
    const bunkerElement = document.createElement('div');
    bunkerElement.className = 'bunker';
    bunkerElement.innerHTML = `
        <h2>Bunker ${bunkerId}</h2>
        <div class="bunker-layout">
            <div class="cabinets-container">
                ${createCabinetRows(bunker.cabinets)}
            </div>
            <div class="stocker" data-status="${bunker.stocker.status}">
                <div>Stocker</div>
                <div class="gas-tanks">
                    ${bunker.stocker.gas_tanks.map(tank => `
                        <div class="gas-tank" data-status="${tank.status || 'unknown'}"></div>
                    `).join('')}
                </div>
            </div>
            ${createAGV(bunker.agv)}
        </div>
    `;
    return bunkerElement;
}

function createCabinetRows(cabinets) {
    let cabinetHtml = '';
    const cabinetIds = Object.keys(cabinets).sort((a, b) => parseInt(a) - parseInt(b));
    const rowSize = Math.ceil(cabinetIds.length / 3);
    
    for (let i = 0; i < 3; i++) {
        cabinetHtml += `
            <div class="cabinet-row">
                ${cabinetIds.slice(i * rowSize, (i + 1) * rowSize).map(cabinetId => {
                    // 항상 2개의 gas_tank를 보장
                    const gasTanks = cabinets[cabinetId].gas_tanks || [];
                    const gasTanksHtml = Array(2).fill().map((_, index) => {
                        const tank = gasTanks[index] || { status: 'unknown' };
                        return `<div class="gas-tank" data-status="${tank.status || 'unknown'}"></div>`;
                    }).join('');

                    return `
                        <div class="cabinet">
                            <div>Cabinet ${cabinetId}</div>
                            <div class="gas-tanks">
                                ${gasTanksHtml}
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }
    
    return cabinetHtml;
}

function createAGV(agv) {
    const position = calculateAGVPosition(agv.position);
    return `
        <div class="agv" style="left: ${position.x}; top: ${position.y};">
            AGV<br>(${agv.status || 'unknown'})
        </div>
    `;
}

function calculateAGVPosition(position) {
    const x = `calc(${position.x}% - 15px)`;
    const y = `calc(${position.y}% - 15px)`;
    return { x, y };
}

socket.on('error', function(error) {
    console.error('Error:', error);
});