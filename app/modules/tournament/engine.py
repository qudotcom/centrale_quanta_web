import unitary.quantum_chess.quantum_board as qb
import unitary.quantum_chess.ascii_board as ab

class QuantumEngine:
    def __init__(self):
        # This now initializes the REAL Cirq-based quantum simulator
        self.board = qb.CirqBoard(board_prefix="qchess")

    def load_game(self, move_history: str):
        """
        Replays the real quantum moves.
        """
        if not move_history:
            return

        moves = move_history.split(',')
        for m in moves:
            if m:
                try:
                    # The real engine parses strings like "e2e4"
                    self.board.do_move(m)
                except Exception as e:
                    print(f"Physics Error on move {m}: {e}")

    def get_ascii_visual(self):
        """
        Returns the board state.
        Note: The real library might show probabilities (e.g., 'N:50%')
        """
        return str(ab.AsciiBoard(self.board))

    def apply_move(self, move_str: str):
        """
        Executes a move on the Quantum Circuit.
        """
        try:
            # This triggers the quantum simulation (Split, Merge, Measure)
            self.board.do_move(move_str)
            return True
        except Exception as e:
            print(f"Invalid Quantum Move: {e}")
            return False

def get_board_state(move_history_str):
    engine = QuantumEngine()
    engine.load_game(move_history_str)
    return engine.get_ascii_visual()
