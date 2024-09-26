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
            <div class="agv-path-vertical agv-path-left"></div>
            <div class="agv-path-vertical agv-path-right"></div>
            <div class="cabinets-container">
                ${createCabinetRows(bunker.cabinets)}
            </div>
            <div class="stocker" data-status="${bunker.stocker.status}">
                Stocker (${bunker.stocker.status})
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
                ${cabinetIds.slice(i * rowSize, (i + 1) * rowSize).map(cabinetId => `
                    <div class="cabinet">
                        <div>Cabinet ${cabinetId}</div>
                        <div class="gas-tanks">
                            ${cabinets[cabinetId].gas_tanks.map(tank => `
                                <div class="gas-tank" data-status="${tank.status || 'unknown'}"></div>
                            `).join('')}
                        </div>
                    </div>
                `).join('')}
            </div>
            ${i < 2 ? '<div class="agv-path"></div>' : ''}
        `;
    }
    
    return cabinetHtml;
}

function createAGV(agv) {
    const position = calculateAGVPosition(agv.position);
    let statusColor = '#1E90FF'; // 기본 색상

    // AGV 상태에 따라 색상 변경 (선택사항)
    switch(agv.status) {
        case 'moving':
            statusColor = '#32CD32'; // 라임 그린
            break;
        case 'loading':
        case 'unloading':
            statusColor = '#FFD700'; // 골드
            break;
        case 'idle':
            statusColor = '#1E90FF'; // 도저히 파란색
            break;
        default:
            statusColor = '#808080'; // 회색 (unknown 상태)
    }

    return `
        <div class="agv" style="left: ${position.x}; top: ${position.y}; background-color: ${statusColor};">
            AGV<br>(${agv.status || 'unknown'})
        </div>
    `;
}

function calculateAGVPosition(position) {
    const pathWidth = 20;
    const agvSize = 60;
    const bunkerPadding = 25;
    const bunkerWidth = 100 - (2 * bunkerPadding);
    const offset = 10; // AGV가 경로 위에 올라가도록 오프셋 설정

    let x, y;

    if (position.x === 0) {
        x = `${bunkerPadding - agvSize/2 + offset}px`;
    } else if (position.x === 100) {
        x = `calc(100% - ${bunkerPadding + agvSize/2 - offset}px)`;
    } else {
        x = `calc(${bunkerPadding}px + ${position.x}% * ${bunkerWidth / 100} - ${agvSize/2}px)`;
    }

    const totalHeight = 700;
    const stockerHeight = 80;
    const stockerMargin = 10;
    const availableHeight = totalHeight - stockerHeight - stockerMargin;
    const cabinetRowHeight = (availableHeight - 2 * pathWidth) / 3;

    if (position.y === 0) {
        y = `${-agvSize/2 + offset}px`;
    } else if (position.y === 100) {
        y = `${availableHeight - agvSize/2 - offset}px`;
    } else if (position.y === 25) {
        y = `${cabinetRowHeight - agvSize/2}px`;
    } else if (position.y === 50) {
        y = `${cabinetRowHeight * 2 + pathWidth - agvSize/2}px`;
    } else if (position.y === 75) {
        y = `${cabinetRowHeight * 3 + pathWidth * 2 - agvSize/2}px`;
    }

    return { x, y };
}