class GameStats:
    '''
    管理游戏状态
    '''
    def __init__(self,ai_game):
        self.ai_game = ai_game
        self.settings = ai_game.settings
        self.reset_stats()
        self.game_active = False
        self.high_score = int(self.read_log())

    def reset_stats(self):
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def write_log(self):
        with open('log/high_score.txt','w',encoding='utf-8') as f:
            f.write(str(self.ai_game.sb.prep_high_score()))
    def read_log(self):
        with open('log/high_score.txt','r',encoding='utf-8') as f:
            return f.read()