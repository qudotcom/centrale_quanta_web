import unitary.quantum_chess.quantum_board as qb
import unitary.quantum_chess.ascii_board as ab
import unitary.quantum_chess.move as move_lib

class QuantumEngine:
    def __init__(self):
        # Initialize a fresh Quantum Board (CirqBoard)
        self.board = qb.CirqBoard(board_prefix="qchess")

    def load_game(self, move_history: str):
        """
        Replays the game from a string of moves (e.g., 'e2e4,e7e5,a1a3^')
        to restore the quantum state.
        """
        if not move_history:
            return

        moves = move_history.split(',')
        for m in moves:
            if m:
                # In a full impl, you would parse the algebraic notation here.
                # For this MVP, we assume the library handles simple algebraic or we catch errors.
                try:
                    self.board.do_move(m)
                except Exception as e:
                    print(f"Error replaying move {m}: {e}")

    def get_ascii_visual(self):
        """Returns the specific string representation for our Terminal UI"""
        visual = ab.AsciiBoard(self.board)
        return str(visual)

    def apply_move(self, move_str: str):
        """
        Attempts to apply a move. Returns True if valid, False if invalid.
        """
        try:
            # The library do_move handles the logic
            result = self.board.do_move(move_str)
            return True
        except Exception as e:
            print(f"Invalid Move: {e}")
            return False

# Helper to get board from DB string
def get_board_state(move_history_str):
    engine = QuantumEngine()
    engine.load_game(move_history_str)
    return engine.get_ascii_visual()
