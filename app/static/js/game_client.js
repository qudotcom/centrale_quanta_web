document.addEventListener("DOMContentLoaded", function() {
    // 1. Setup "Enter" key listener for better UX
    const input = document.getElementById('move-input');
    if (input) {
        input.addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                submitMove();
            }
        });
    }
});

async function submitMove() {
    // 2. Get Match ID from the HTML data attribute
    const gameData = document.getElementById('game-data');
    if (!gameData) {
        console.error("Game data not found");
        return;
    }
    const matchId = gameData.dataset.matchId;

    // 3. Get Input Data
    const input = document.getElementById('move-input');
    const logPanel = document.getElementById('game-logs');
    const move = input.value;

    if (!move) return;

    // 4. Update Log (Optimistic UI)
    logPanel.innerHTML += `<div>> Attempting move: ${move}...</div>`;
    logPanel.scrollTop = logPanel.scrollHeight;

    try {
        // 5. Send Request to Backend
        const response = await fetch(`/tournament/move/${matchId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ move_str: move })
        });

        const data = await response.json();

        // 6. Handle Response
        if (data.success) {
            // Update the ASCII board
            document.getElementById('quantum-board').innerText = data.new_board;
            logPanel.innerHTML += `<div style="color: #fff;">> MOVE SUCCESS. State Updated.</div>`;
            input.value = ''; // Clear input
        } else {
            logPanel.innerHTML += `<div style="color: red;">> ERROR: ${data.message}</div>`;
        }
    } catch (error) {
        console.error(error);
        logPanel.innerHTML += `<div style="color: red;">> CONNECTION FAILURE</div>`;
    }
    
    // Auto-scroll to bottom of logs
    logPanel.scrollTop = logPanel.scrollHeight;
}
