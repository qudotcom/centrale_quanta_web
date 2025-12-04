import random
import re
from app.modules.tournament.engine import QuantumEngine

class QuantumAI:
    def __init__(self):
        self.cols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        self.rows = ['1', '2', '3', '4', '5', '6', '7', '8']

    def get_black_piece_locations(self, ascii_board: str):
        """
        Parses the ASCII board to find squares occupied by Black pieces (lowercase letters).
        Returns a list of squares like ['a7', 'b8', ...].
        """
        locations = []
        # The board comes in as a string with pipes and newlines.
        # We need to map the visual grid back to coordinates.
        lines = ascii_board.strip().split('\n')
        
        # We expect the ascii board lines to look like "8 | r n b ... |"
        # We iterate only the rank lines (usually index 1 to 8 in the split list)
        current_rank = 8
        
        for line in lines:
            # Check if this line represents a rank (starts with a number)
            if re.match(r'\s*\d', line):
                # Clean the line to get just the pieces: "r n b q k b n r"
                # Remove the "8 | " prefix and " |" suffix
                content = line.split('|')[1].strip()
                pieces = content.split(' ')
                
                for i, piece in enumerate(pieces):
                    # In Quantum Chess ASCII, black pieces are usually lowercase
                    # (Note: This depends on the specific ASCII output of the lib, 
                    # but usually lowercase = black, uppercase = white)
                    if piece.islower() and piece != '.': 
                        col = self.cols[i]
                        square = f"{col}{current_rank}"
                        locations.append(square)
                
                current_rank -= 1
                
        return locations

    def calculate_move(self, engine: QuantumEngine):
        """
        Tries to find the best move for Black.
        """
        # 1. Get current board state
        board_visual = engine.get_ascii_visual()
        my_pieces = self.get_black_piece_locations(board_visual)
        
        valid_moves = []
        
        # 2. Brute-force valid moves (Efficiency: Check likely moves first)
        # Trying every piece against every square is 16 * 64 = 1024 checks. 
        # The engine is fast enough for this.
        
        targets = [f"{c}{r}" for c in self.cols for r in self.rows]
        
        for source in my_pieces:
            for target in targets:
                if source == target:
                    continue
                
                move_str = f"{source}{target}"
                
                # We clone the engine/board history to test the move without breaking the real game
                # Since engine.apply_move changes state, we assume the engine passed here 
                # is a TEMPORARY one or we just test validity.
                # However, engine.apply_move returns True/False.
                # We need to test on a COPY.
                
                # Workaround: Since we can't easily deepcopy the C++ object in the library,
                # we just try the move. If it works, we record it and UNDO (if possible) 
                # or better: we use the history string to rebuild a fresh engine for every check.
                # BUT rebuilding is slow.
                
                # OPTIMIZED APPROACH: Just generate the string and ask the engine.
                # Since we are inside the logic flow, we rely on the router to handle the state.
                # Here we just return a "Candidate".
                valid_moves.append(move_str)

        # Since checking validity 1000 times via `apply_move` (which rebuilds history) is slow,
        # We will pick a random subset of plausible moves (e.g. Pawn push, Knight jump)
        # to try against the real engine in the Router.
        
        # actually, let's return a list of prioritized candidates for the router to try.
        return self._prioritize_candidates(my_pieces)

    def _prioritize_candidates(self, my_pieces):
        """
        Returns a list of moves to try in order.
        """
        candidates = []
        
        # STRATEGY 1: Center Control (d5, e5)
        center_targets = ['d5', 'e5', 'd4', 'e4']
        
        # STRATEGY 2: Random aggression
        # Generate 20 random moves to try
        for _ in range(50):
            if not my_pieces: break
            source = random.choice(my_pieces)
            
            # Bias towards center or forward moves
            target_col = random.choice(self.cols)
            target_row = random.choice(self.rows)
            target = f"{target_col}{target_row}"
            
            if source != target:
                candidates.append(f"{source}{target}")
        
        # Add simple pawn pushes specifically if we have pieces on row 7
        for p in my_pieces:
            if '7' in p: # Likely a pawn
                col = p[0]
                # Try pushing 1 or 2 squares
                candidates.insert(0, f"{col}7{col}5") # Aggressive
                candidates.insert(0, f"{col}7{col}6") # Safe

        return candidates
