"""
Allows the engine to analyze test positions.


Attributes:
  enginepath: The path/filename or filename of the engine to be tested.
  epdfn: The epd test file.
  movetime: Analysis time in seconds.
  correct: The number of correct solutions found by engine.
  totalpos: Then total number of positions in the epd file.  
"""


import chess
import chess.engine


class Analysis:
    def __init__(self, enginepath: str, epdfn: str,
                 movetime: float = 1.0):
        self.enginepath = enginepath
        self.epdfn = epdfn
        self.movetime = movetime
        self.correct = 0
        self.totalpos = 0

    def get_epds(self):
        """Returns the epd lines from epd file.
        """
        with open(self.epdfn, 'r') as f:
            for lines in f:
                line = lines.rstrip()
                yield line

    def run(self):
        """Test the engine on the test file.

        Save number of correct and all positins counts.
        """
        engine = chess.engine.SimpleEngine.popen_uci(self.enginepath)
        for epd in self.get_epds():
            board, info = chess.Board.from_epd(epd)
            self.totalpos += 1
            result = engine.analyse(
                board,
                chess.engine.Limit(time=self.movetime), game=object())
            move = result['pv'][0]
            if move in info["bm"]:
                self.correct += 1
        engine.quit()
