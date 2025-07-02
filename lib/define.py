# 事件定义
EVENT_TAKE_CHANGE = 0x00  # 场景变化：场景ID
EVENT_PLAYERS_COUNT_CHANGE = 0x02  # 游玩玩家数量：玩家数量
EVENT_REQ_CLONE = 0x03  # 请求关卡编辑器克隆选中的对象
EVENT_REQ_LEVEL_SAVE = 0x04  # 请求关卡编辑器保存此关卡
EVENT_REQ_DELETE = 0x05  # 请求关卡编辑器删除选中的对象
EVENT_LEVEL_ENTER = 0x06  # 玩家进入关卡
EVENT_LEVEL_RESET = 0x07  # 玩家重置关卡
EVENT_LEVEL_EXIT = 0x08  # 玩家退出关卡
EVENT_LEVEL_END = 0x09  # 玩家完成关卡
EVENT_COVER_FINISH = 0x0A # 结束界面结束进场滑动
EVENT_COVER_EXIT = 0x0B  # 结束界面开始退场
EVENT_LEVEL_NEXT = 0x0C  # 玩家进入下一个关卡
EVENT_REQ_RELOAD_LEVEL = 0x0D
EVENT_SWITCH_HT_MODE = 0x0E
EVENT_NAME_MAP: dict[int, str] = {
    value: name for name, value in globals().items() if name.startswith("EVENT_") and isinstance(value, int)
}

# 关卡结局定义
LEVEL_END_WIN = 0x00  # 玩家赢了
LEVEL_END_LOSE = 0x01  # 玩家输了
LEVEL_END_ALL_COMPLETE = 0x02  # 玩家完成所有关卡

# 场景定义
TAKE_EMPTY = 0x00  # 占位用，用来为转场遮罩做参数
TAKE_START = 0x01  # 开始界面
TAKE_PLAYERS_CHOOSE = 0x02  # 玩家选择界面
TAKE_LEVEL_CHOOSE = 0x03  # 关卡选择界面
TAKE_PLAY = 0x04  # 关卡游玩场景
TAKE_NAME_MAP: dict[int, str] = {
    value: name for name, value in globals().items() if name.startswith("TAKE_") and isinstance(value, int)
}

# 图层定义
LAYER_HIDE = 0x00  # 位于背景下，永远不可见
LAYER_BG = 0x01  # 背景
LAYER_PLAY = 0x02  # 关卡元素图层
LAYER_UI_SHADOW = 0x03  # 界面阴影
LAYER_UI = 0x04  # 界面
LAYER_END_UI_BG = 0x05  # 结束界面背景
LAYER_END_UI_SHADOW = 0x06  # 结束界面阴影
LAYER_END_UI = 0x07  # 结束界面
LAYER_COVER = 0x08  # 转场遮罩
LAYERS = [LAYER_HIDE,
          LAYER_BG,
          LAYER_PLAY,
          LAYER_UI_SHADOW, LAYER_UI,
          LAYER_END_UI_BG, LAYER_END_UI_SHADOW, LAYER_END_UI,
          LAYER_COVER]

# 自定义设置
# 显示帧率 (low)
SHOW_PERF = True

# 显示更新时间占用最大的精灵 (mid)
SPRITE_PERF = False

# 启用关卡编辑 (None)
LEVEL_EDIT = False

# 可否移动界面元素 (None)
ELE_EDIT = True

# 加载时在窗口显示日志 (high)
LOADING_LOG = False

# 渲染加载日志时帧数
LOADING_FPS = 30

# 游戏缩放
GAME_SCALE = 1.5

# 使用修复前的动画 (卡顿感会变大，但不影响计算) (None)
OLD_ANIMATION = False

# 玩家重力加速度
G = 0.4 * 60

# 玩家移动速度
PLAYER_MOVE_SPEED = 270 / 60

# 目前游戏的版本
VERSION = "beta 1.0"
