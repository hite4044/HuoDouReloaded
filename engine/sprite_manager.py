from sprites.bg import BackGround
from sprites.buttons.game_start import StartButton
from sprites.buttons.more_game import MoreGameButton
from sprites.buttons.music import MusicButton
from sprites.buttons.return_levels import ReturnChooseButton
from sprites.level.buttons import *
from sprites.level.end_cover import *
from sprites.level.level_info import *
from sprites.level.level_manager import LevelManager
from sprites.takes.level_choose import *
from sprites.takes.player_choose import *
from sprites.titles import *
from sprites.transition import TransitionMask


class SpritesManager:
    def __init__(self):
        self.background = BackGround()
        self.brown_player_pose = BrownPlayerPose((854, 515))
        self.game_title = GameTitle((524, 119))
        self.player_choose_title = PlayersChooseTitle((540, 107))
        self.level_choose_title = LevelChooseTitle((538, 54))
        self.more_game_button = MoreGameButton()
        self.win_cover_title = WinCoverTitle()
        self.lose_cover_title = LoseCoverTitle()
        self.start_button = StartButton((546, 322))
        self.music_button = MusicButton()
        self.return_button = ReturnButton((733, 698))

        self.players1_button = Players1Button((364, 262))
        self.players2_button = Players2Button((560, 262))
        self.players3_button = Players3Button((750, 262))
        self.players_ok_button = PlayersOKButton((557, 683))
        self.players_keys = PlayersKeys((292, 516))
        self.players1_choose = PlayersCH((281, 324), rs.sprites.player_pose.black, 1)
        self.players2_choose = PlayersCH((483, 324), rs.sprites.player_pose.red, 2)
        self.players3_choose = PlayersCH((663, 323), rs.sprites.player_pose.purple, 3)

        self.levels_container = LevelsContainer((123, 120))

        self.level_manager = LevelManager()
        self.more_game_play_button = MoreGameLite((760, 44))
        self.reset_button = ResetButton((907, 46))
        self.home_button = HomeButton((981, 46))
        self.level_level_text = LevelLevelText((15, 12))
        self.level_level_number = LevelLevelNumber((80, 15))
        self.bean_counter = BeanCounter((255, 9))
        self.bean_show = BeanShow((219, 14))

        self.return_choose = ReturnChooseButton()
        self.next_level = NextLevelButton()
        self.retry_button = RetryButton()

        self.win_cover = WinCover()
        self.lose_cover = LoseCover()
        self.complete_cover = CompleteCover()

        self.transition = TransitionMask()

    @staticmethod
    def send_event(event_id: int, data = None):
        if event_id == EVENT_TAKE_CHANGE:
            trans_data = TAKE_NAME_MAP[data]
        else:
            trans_data = data
        print(f"EVENT - {EVENT_NAME_MAP[event_id]}" + (f": {trans_data}" if trans_data else ""))
        for _sprites in public.sprites.values():
            for sprite in _sprites:
                sprite.event_parse(event_id, data)
