# ba_meta require api 9
"""BSM Boosters — усилители бомб для BombSquad 1.8.x.

Нужен заряд щита из Absorb Shield; без него бомбы ведут себя как обычно.
Всё работает только со СВОИМИ бомбами (которые выкинул сам боец).
«Заряжен» — заряд есть у бойца или уже ушёл в саму бомбу (если боец был
заряжен, когда доставал её).

Ударная бомба (взрыв при касании), заряжен:
  * брошенная заряженная ударная бомба летит и взрывается как обычно,
    только её взрыв несёт заряд;
  * удар кулаком по своей ударной бомбе (например, в воздухе сразу после
    броска) — она уносится во врага
    (доворачивает за противником в направлении удара, до 45°), по дороге
    не взрывается о стены и пол и обходит препятствия — вверх, вниз или в
    сторону, так что долетает и на «Счастливых мыслях»; взрывается при
    касании врага, заряд уходит в её взрыв. Если впереди никого нет — летит
    прямо и взрывается обо что угодно;
  * пинг-понг: цель может отбить летящую в неё бомбу любым ударом — та,
    как мячик, летит дальше по кругу (1 → 2 → 3 → … → 1; вдвоём — обратно
    в пославшего) плавно, по лёгкой спирали, в искрах. Ник того, в кого
    летит мяч, мигает красным, следующего («готовься») — жёлтым. Мяч
    разгоняется (12 → 30 м/с), пока кто-нибудь не пропустит; после
    двух отбиваний попадание — мощный направленный взрыв конусом 50°.

Обычная бомба, заряжен:
  удар кулаком по своей летящей бомбе — она превращается в 6 мини-снарядов
  (счётчик над головой). Каждое нажатие «Бомба» выпускает один снаряд прямо
  по взгляду: летит не падая и при попадании отнимает 50% здоровья
  небольшим аккуратным взрывом — попадает сразу, даже в упор.

Мина, заряжен:
  * заряженная мина, взведясь, по одной выкладывает вокруг себя 6 мин ровным
    кольцом в 2 м (взрыв одной не задевает соседей); свалившиеся с обрыва
    или в пропасть исчезают;
  * пнёшь свою заряженную мину, пока она не взвелась, — суперзаряд: после
    кольца каждая из 6 мин по очереди выбрасывает ещё по 2 наружу (всего
    18, цепная реакция возможна).

Ядерный суицид (нужен Absorb Shield):
  подобрал проклятие («суицид») и спарировал щитом его взрыв — открывается
  QTE на 3.5 секунды: по одной показываются 6 цветных кнопок, жми их по порядку.
  Успел без ошибок — тревога и таймер до взрыва, в самый последний момент
  замедление и наезд камеры, и боец взрывается ядерной бомбой, унося с
  собой всех на карте. Ошибся или не успел — обычный взрыв проклятия.

Ледяная бомба, заряжен:
  * удар кулаком по своей ледяной бомбе — бомба рассыпается льдом, а боец
    получает ледяные кулаки: каждый удар замораживает. Чем больше был заряд,
    тем дольше они держатся;
  * заряженная ледяная бомба, которую просто выкинули, вдобавок к морозной
    волне щита мягко выбрасывает вокруг 3 ледяные мини-бомбы (светятся,
    падают метрах в двух, взрыв обычного радиуса), которые взрываются одна
    за другой вскоре после основной.

Липкая бомба, заряжен:
  * брошенная заряженная липкая бомба шевелит щупальцами из слизи и
    хватает ВСЕХ врагов в радиусе 3.5 м (и тех, кто зайдёт позже) — на
    каждого своё щупальце; бомба и враги притягиваются друг к другу
    (лёгкая бомба летит быстрее), пока не слипнутся, а потом обвивает;
  * удар кулаком по своей липкой бомбе — она превращается в 3 щупальца
    (до 9). Каждое нажатие «Бомба» — одно щупальце, без перезарядки, и
    каждое берёт свободного врага (не того, кого уже схватило другое): оно
    выползает у твоих ног и стремительно ползёт по земле к врагу, на
    которого ты смотришь (узкий конус ±15°, на всю карту); кого настигнет
    первым — под тем встаёт из земли и обвивает (с ног не сбивает,
    увернуться можно прыжком или парированием); на него налепляются 4
    липкие мини-бомбы и через 0.8 с взрываются прямо на нём (заряд делает
    взрывы шире). Нет никого в конусе — проползает 8 м вперёд.

Режим «Мячик» (в списке игр, карта «BSM Арена» — ночной стадион, самое
большое ровное поле в игре): мяч подаётся из центра и летит по кругу, его
отбивают кулаком (только настоящее попадание кулака, отбить может любой);
пропустил — минус жизнь. Мяч летит низко, уходит туда, куда ударили, и
мягкой дугой доворачивает к следующему. Схватил мяч руками
(обычное хватание) — он тащит тебя к следующему; ещё раз — бросил. Боты
четырёх уровней сложности. Бомб нет, но можно драться кулаками и хватать
соперников (забили — минус жизнь).

Работает и на «Счастливых мыслях»: направления и расстояния считаются в 3D.
Мод нужен только хосту: в сетевой игре всё считается на сервере.
"""

from __future__ import annotations

import logging
import math
import random
import weakref
from typing import TYPE_CHECKING

import babase
import bascenev1 as bs
from bascenev1 import _classicassets
from bascenev1lib.actor.bomb import (
    ArmMessage,
    Blast,
    Bomb,
    BombFactory,
    ExplodeMessage,
)
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.scoreboard import Scoreboard
from bascenev1lib.actor.spaz import PunchHitMessage, Spaz
from bascenev1lib.gameutils import SharedObjects
from bascenev1lib.maps import FootballStadium

if TYPE_CHECKING:
    from typing import Any, Sequence

# Версия для автообновления BSM (bsm_updater.py сверяет её с GitHub).
BSM_VERSION = '2.36'

# ------------------------------- Настройки --------------------------------

IMPACT_SPEED = 12.0  # Скорость ударной бомбы после удара (м/с).
IMPACT_FLIGHT_TIME = 4.0  # Сколько она ищет путь к врагу, потом взрывается.
IMPACT_STEER = 0.3  # Плавность разворотов в полёте (1.0 — мгновенно).
IMPACT_ACCEL = 1.5  # Самонаводящаяся бомба разгоняется в полёте (м/с за сек)...
DEFLECT_SPEEDUP = 1.08  # ...и на 8% при каждом отбивании...
DEFLECT_MAX_SPEED = 30.0  # ...но не быстрее этого (м/с).
PANDA_SPEED = 20.0  # С этой скорости отбивание — «внутренний покой» (раз).
PANDA_TIME = 0.7  # Сколько бомба кружит вокруг отбивающего (сек).
DEFLECT_WINDOW = 0.25  # Удар засчитывается, если нажат не раньше стольких
#                        сек до встречи с мячом (сколько угодно раз).
FIST_RADIUS = 0.5  # Плоские карты: мяч отбивается касанием кулака — в таком
#                    радиусе от кулака бьющего (метров).
FLY_DEFLECT_ZONE = 1.0  # «Счастливые мысли»: зона вокруг бойца (метров).
PINGPONG_TURN = 5.0  # Как резко отбитая бомба доворачивает (рад/с) — плавно.
SPIRAL_RADIUS = 0.25  # Лёгкая равномерная спираль в полёте (метров)...
SPIRAL_RATE = 10.0  # ...и её скорость вращения (рад/с).
CONE_AFTER_DEFLECTS = 2  # После стольких отбиваний попадание — конусный взрыв.
CONE_ANGLE = 50.0  # Ширина конуса взрыва (градусов).
CONE_LENGTH = 7.0  # Длина конуса (метров).
CONE_DAMAGE = 900.0  # Урон в конусе вплотную (+ заряд бомбы), к концу слабее.
SHOT_COUNT = 6  # Сколько мини-снарядов даёт отбитая заряженная бомба.
SHOT_MAX = 12  # Сколько снарядов можно носить.
SHOT_SPEED = 12.0  # Скорость снаряда (м/с).
SHOT_LIFETIME = 3.0  # Через сколько секунд снаряд взрывается сам.
SHOT_DAMAGE = 500.0  # Урон снаряда (1000 = полное здоровье).
SHOT_BLAST_RADIUS = 1.2  # Радиус небольшого взрыва снаряда (метров).
SHOT_HIT_RADIUS = 0.6  # Снаряд попадает в бойца, пролетев так близко от его
#                        центра — с первого же мига полёта, хоть вплотную.
MAX_CHARGE_TRIGGER = 3000.0  # Особые усиления при полном заряде щита (300%).
HOMING_SHOT_TURN = 3.2  # Плавность самонаведения полных обычных снарядов.
IMPACT_TOUR_STEER = 0.10  # Мягкие, хорошо читаемые повороты ударной на 300%.
ROUTE_BLAST_RADIUS = 1.25  # Взрыв на каждой цели маршрутного снаряда.
ROUTE_KILL_DAMAGE = 10000.0  # Контактная на 300% ваншотит основную цель.
ROUTE_TURN_TIME = 0.32  # Заметный боковой вираж после каждого попадания.
ICE_ORB_SPEED = 11.0  # Скорость самонаводящегося ледяного заряда.
ICE_ORB_MAX = 3  # Сколько ледяных зарядов можно накопить.
MINE_RING = 6  # Заряженная мина выкладывает столько мин ровным кольцом...
MINE_RING_DIST = 2.0  # ...на таком расстоянии (соседки тоже в 2 м друг от
#                       друга — вне радиуса взрыва мины 1.4 м).
MINE_CHILDREN = 2  # Пнутая: каждая мина кольца выбрасывает ещё столько...
MINE_CHILD_DIST = 1.9  # ...на таком расстоянии наружу (цепочки возможны).
MINE_SEQ_DELAY = 0.12  # Мины вылетают по одной с такой паузой (сек).
NUKE_QTE_TIME = 3.5  # Время на QTE ядерного суицида (сек).
NUKE_QTE_KEYS = 6  # Сколько кнопок нужно нажать.
NUKE_COUNTDOWN = 3.0  # Отсчёт до ядерного взрыва после QTE (сек).
NUKE_SLOWMO = 0.35  # Замедление и наезд камеры: столько секунд до взрыва.
IMPACT_RANGE = 25.0  # Дальность поиска врага для неё (метров).
IMPACT_ANGLE = 45.0  # Насколько враг может быть в стороне от удара (градусов).
ICE_FISTS_TIME = 8.0  # Ледяные кулаки: базовая длительность (сек)...
ICE_FISTS_PER_CHARGE = 0.01  # ...плюс секунд за каждую единицу заряда...
ICE_FISTS_MAX_TIME = 20.0  # ...но не дольше этого.
ICE_FISTS_FREEZE = 3.0  # На сколько секунд замораживает удар ледяным кулаком.
ICE_MINI_BOMBS = 3  # Сколько мини-бомб разбрасывает заряженная ледяная.
ICE_MINI_DELAY = 0.7  # Через сколько после основной взрывается первая...
ICE_MINI_STAGGER = 0.2  # ...и с каким шагом остальные (сек).
TENTACLE_RANGE = 3.5  # Дальность щупальцев заряженной липкой бомбы (метров).
TENTACLE_PULL = 160.0  # Сила, с которой щупальце подтягивает врага.
WHIP_RANGE = 60.0  # Дальность щупальца: на всю карту (метров).
WHIP_ANGLE = 15.0  # Конус поиска цели от взгляда (градусов в каждую сторону).
WHIP_PER_BOMB = 3  # Сколько щупалец даёт одна липучка.
WHIP_HEIGHT = 3.2  # Как высоко щупальце вырастает из земли (метров).
WHIP_CRAWL_SPEED = 20.0  # С какой скоростью щупальце ползёт к цели (м/с).
WHIP_CRAWL_TIME = 12.0  # Сколько оно ползёт, прежде чем сдаться (сек).
WHIP_FUSE = 0.8  # Через сколько взрываются налепленные мини-бомбы (сек).
WHIP_MAX = 9  # Сколько щупалец можно носить.
BALL_LIVES = 3  # Режим «Мячик»: жизней у каждого по умолчанию.
BALL_SERVE_DELAY = 1.5  # Пауза перед подачей нового мяча (сек).
BALL_TURN = 1.5  # Как плавно мяч доворачивает к следующему (рад/с)...
BALL_TURN_RADIUS = 7.0  # ...на скорости — дугой не круче такого радиуса (м).
BALL_HIT_SPREAD = 45.0  # Боты отбивают с разбросом в сторону (градусов).
BALL_SWING_LEAD = 0.27  # Боты замахиваются за столько до встречи с мячом (с):
#                        у удара есть замах, кулак успевает при 0.18–0.36 с.
#                        Засчитывается только настоящее попадание кулака.
BALL_RIDE_BOOST = 1.2  # С тем, кто держит, мяч тянет сильнее (он тяжёлый).
FX_STRENGTH = 0.5  # Сила вспышек, света и тряски камеры (1.0 = максимум).
FLASH_STRENGTH = 0.4  # Яркость и размер вспышек (1.0 = как в версии 1.5).

# --------------------------------------------------------------------------

_TICK = 0.03
_ICE = (0.45, 0.8, 1.6)

# Captured when the plugin switches on (not at import), so plugins that
# patch the same Spaz methods chain instead of overwriting each other.
_orig_init: Any = None
_orig_handlemessage: Any = None
_orig_drop_bomb: Any = None
_orig_bomb_handle_impact: Any = None
_orig_bomb_handlemessage: Any = None
_orig_set_land_mine_count: Any = None
_orig_curse_explode: Any = None
_orig_jump_press: Any = None
_orig_punch_press: Any = None
_orig_bomb_press: Any = None
_orig_pickup_press: Any = None

_SLIME = (0.45, 1.4, 0.35)  # Tentacle color (glowing slime green).


# ------------------------------- Helpers ----------------------------------


def _wcall(func: Any, obj: Any) -> Any:
    """Timer callback that holds its object weakly (no ref cycles)."""
    ref = weakref.ref(obj)

    def _call() -> None:
        target = ref()
        if target is not None:
            func(target)

    return _call


def _snd(name: str, volume: float = 1.0, pos: Sequence[float] | None = None):
    try:
        sound = getattr(_classicassets.audio, name).get()
    except Exception:
        return
    if pos is None:
        sound.play(volume)
    else:
        sound.play(volume, position=pos)


def _seq(pos: Sequence[float] | None, *steps: tuple) -> None:
    """A layered sound cue: (delay, sound name, volume) steps."""
    for delay, name, volume in steps:
        if delay <= 0:
            _snd(name, volume, pos)
        else:
            bs.timer(delay, bs.CallStrict(_snd, name, volume, pos))


def _bright(color: Sequence[float], scale: float = 1.0) -> tuple:
    rgb = [max(0.0, float(c)) for c in color[:3]]
    peak = max(rgb)
    if peak < 0.05:
        return (scale, scale, scale)
    return tuple(c / peak * scale for c in rgb)


def _color(spaz: Spaz) -> tuple:
    try:
        return _bright(spaz.node.color, 1.0)
    except Exception:
        return (1.0, 1.0, 1.0)


def _flash(pos: Sequence[float], color: Sequence[float], size: float,
           light_radius: float, intensity: float,
           duration: float = 0.25) -> None:
    dim = FX_STRENGTH * FLASH_STRENGTH
    color = _bright(color, 1.0)  # Same hue, never over-bright.
    flash = bs.newnode(
        'flash',
        attrs={'position': pos, 'size': size * dim, 'color': color},
    )
    bs.timer(0.08, flash.delete)
    light = bs.newnode(
        'light',
        attrs={
            'position': pos,
            'color': color,
            'radius': light_radius * dim,
            'height_attenuated': False,
            'volume_intensity_scale': 0.6,
        },
    )
    bs.animate(light, 'intensity', {0: intensity * dim, duration: 0})
    bs.timer(duration + 0.05, light.delete)


def _ring(pos: Sequence[float], color: Sequence[float], size: float,
          duration: float) -> None:
    ring = bs.newnode(
        'locator',
        attrs={
            'shape': 'circleOutline',
            'position': pos,
            'color': color,
            'opacity': 0.6,
            'draw_beauty': False,
            'additive': True,
        },
    )
    bs.animate_array(ring, 'size', 1, {0: [0.2], duration: [size]})
    bs.animate(ring, 'opacity', {0: 0.6, duration: 0.0})
    bs.timer(duration + 0.05, ring.delete)


def _popup_text(text: str, pos: Sequence[float],
                color: Sequence[float]) -> None:
    txt = bs.newnode(
        'text',
        attrs={
            'text': text,
            'in_world': True,
            'h_align': 'center',
            'flatness': 1.0,
            'shadow': 1.0,
            'color': (color[0], color[1], color[2], 1.0),
            'scale': 0.0,
        },
    )
    comb = bs.newnode('combine', owner=txt, attrs={'size': 3})
    comb.connectattr('output', txt, 'position')
    bs.animate(comb, 'input0', {0: pos[0], 1.2: pos[0]})
    bs.animate(comb, 'input1', {0: pos[1] + 1.4, 1.2: pos[1] + 2.4})
    bs.animate(comb, 'input2', {0: pos[2], 1.2: pos[2]})
    bs.animate(txt, 'scale', {0: 0.0, 0.1: 0.022, 0.2: 0.016, 1.2: 0.0})
    bs.timer(1.25, txt.delete)


def _shake(intensity: float) -> None:
    bs.camerashake(intensity * FX_STRENGTH)


def _norm(vec: Sequence[float]) -> tuple[tuple[float, float, float], float]:
    length = math.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)
    if length < 1e-4:
        return (0.0, 0.0, 0.0), 0.0
    return (vec[0] / length, vec[1] / length, vec[2] / length), length


# Slow motion is shared by the panda deflect and the nuke close-up: it's on
# while anyone holds it and goes back to what it was once all let go.
_SLOWMO: dict[str, Any] = {'count': 0, 'orig': False, 'gnode': None}


def _slowmo_on(gnode: bs.Node) -> None:
    if _SLOWMO['count'] <= 0 or _SLOWMO['gnode'] is not gnode:
        _SLOWMO.update(count=0, orig=bool(gnode.slow_motion), gnode=gnode)
    _SLOWMO['count'] += 1
    gnode.slow_motion = True


def _slowmo_off(gnode: bs.Node) -> None:
    if _SLOWMO['gnode'] is not gnode or _SLOWMO['count'] <= 0:
        return
    _SLOWMO['count'] -= 1
    if _SLOWMO['count'] == 0:
        try:
            gnode.slow_motion = _SLOWMO['orig']
        except Exception:
            pass


def _team(spaz: Spaz) -> Any:
    own = getattr(spaz, 'bsm_team', None)  # Ball-game bots: each on its own.
    if own is not None:
        return own
    if isinstance(spaz, PlayerSpaz):
        player = spaz.getplayer(bs.Player)
        return player.team if player else None
    return 'bots'


def _look_dir(spaz: Spaz) -> tuple[float, float, float]:
    """Where the fighter is looking. Level on normal maps; on Happy Thoughts
    it also tilts up/down with the way they fly."""
    node = spaz.node
    # The game's position_forward point sits behind the body, so 'forward'
    # is from it toward the body.
    flat, flen = _norm((node.position[0] - node.position_forward[0], 0.0,
                        node.position[2] - node.position_forward[2]))
    if flen < 1e-4:
        flat = (1.0, 0.0, 0.0)
    if not getattr(spaz, 'fly', False):
        return flat
    vel = node.velocity
    _, speed = _norm(vel)
    if speed < 1.0:
        return flat
    pitch = max(-0.9, min(0.9, vel[1] / speed))
    level = math.sqrt(1.0 - pitch * pitch)
    return (flat[0] * level, pitch, flat[2] * level)


def _is_enemy(spaz: Spaz, other: Spaz) -> bool:
    if other is spaz:
        return False
    mine, theirs = _team(spaz), _team(other)
    if mine is None or theirs is None:
        return True
    return mine is not theirs


def _charged(spaz: Spaz) -> bool:
    """Has an Absorb Shield charge (and that plugin is on)."""
    return (
        getattr(spaz, '_ab_stored', 0) > 0
        and getattr(Spaz, 'bsm_take_charge', None) is not None
    )


def _bomb_charge(bomb: Bomb) -> float:
    """Charge Absorb Shield already put into this bomb."""
    return float(getattr(bomb, '_ab_charge', 0.0))


def _is_own_bomb(spaz: Spaz, bomb: Bomb) -> bool:
    """A live bomb this fighter threw."""
    if getattr(bomb, '_exploded', False) or not bomb.node:
        return False
    if bomb.owner is not None and bomb.owner == spaz.node:
        return True
    source = bomb.get_source_player(bs.Player)
    return source is not None and source == spaz.source_player


# ------------------------- Impact bomb + charge ---------------------------


def _find_target(spaz: Spaz, origin: Sequence[float],
                 direction: Sequence[float]) -> bs.Node | None:
    """Closest enemy within the cone of the punch. The cone is horizontal
    and any height counts, so it works the same on Happy Thoughts (flying)
    as on the ground - the ball just flies in another plane."""
    min_cos = math.cos(math.radians(IMPACT_ANGLE))
    direction, dlen = _norm((direction[0], 0.0, direction[2]))
    if dlen < 1e-4:
        return None
    best: bs.Node | None = None
    best_score = 0.0
    for node in bs.getnodes():
        if not node or node.getnodetype() != 'spaz':
            continue
        other = node.getdelegate(Spaz)
        if other is None or not other.is_alive() or not _is_enemy(spaz, other):
            continue
        tpos = node.position_center
        _, dist = _norm([a - b for a, b in zip(tpos, origin)])
        flat, flen = _norm((tpos[0] - origin[0], 0.0, tpos[2] - origin[2]))
        if dist < 0.01 or dist > IMPACT_RANGE or flen < 0.01:
            continue
        cos = flat[0] * direction[0] + flat[2] * direction[2]
        if cos < min_cos:
            continue
        score = dist / cos  # Close and straight ahead wins.
        if best is None or score < best_score:
            best, best_score = node, score
    return best


def _enemy_route(spaz: Spaz, origin: Sequence[float]) -> list[bs.Node]:
    """All living enemies, in a readable nearest-neighbour route."""
    left = []
    for node in _live_fighters():
        other = node.getdelegate(Spaz)
        if other is not None and _is_enemy(spaz, other):
            left.append(node)
    route: list[bs.Node] = []
    pos = tuple(origin)
    while left:
        node = min(left, key=lambda n: math.dist(pos, n.position_center))
        left.remove(node)
        route.append(node)
        pos = node.position_center
    return route


def _avoid_dirs(want: Sequence[float]) -> list[tuple[float, float, float]]:
    """Ways around an obstacle: over, under or past it on either side."""
    side, slen = _norm((-want[2], 0.0, want[0]))  # Horizontal perpendicular.
    if slen < 1e-4:
        side = (1.0, 0.0, 0.0)
    out = []
    for vert, horiz in ((1, 1), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, -1)):
        vec = [want[i] * 0.5 + side[i] * 0.7 * horiz for i in range(3)]
        vec[1] += 0.5 * vert  # A gentle climb/dive, not a straight jump.
        out.append(_norm(vec)[0])
    return out


def _launch_impact_bomb(spaz: Spaz, bomb: Bomb) -> None:
    """Charged punch on our impact bomb: it streaks into the enemy."""
    node = spaz.node
    bnode = bomb.node
    col = _color(spaz)
    hot = _bright(col, 2.0)

    direction, dlen = _norm(node.punch_velocity)
    if dlen < 0.1:
        direction, _ = _norm([a - b for a, b in zip(bnode.position,
                                                    node.position)])
    charge = _bomb_charge(bomb) or float(getattr(spaz, '_ab_stored', 0.0))
    tour = _enemy_route(spaz, bnode.position) if charge >= MAX_CHARGE_TRIGGER else []
    target = tour.pop(0) if tour else _find_target(spaz, bnode.position, direction)
    if target is None:
        # Nobody ahead: a plain shot, goes off on whatever it hits.
        direction, _ = _norm((direction[0], max(direction[1], 0.08),
                              direction[2]))
        bomb._bst_levitate = False  # type: ignore[attr-defined]
    else:
        # Homing: walls and floors don't set it off on the way.
        bomb._bst_levitate = True  # type: ignore[attr-defined]

    # Ours: no blowing up on our own fist; make sure it goes off on contact.
    bomb.owner = node
    if BombFactory.get().land_mine_blast_material not in bnode.materials:
        bomb.arm()

    # The shield charge rides in its explosion (unless it already does).
    if _bomb_charge(bomb) <= 0:
        Spaz.bsm_charge_projectile(spaz, bomb)

    ppos = node.punch_position
    _flash(ppos, hot, 0.8, 1.2, 2.0, 0.2)
    bs.emitfx(position=ppos,
              velocity=(direction[0] * 10.0, direction[1] * 10.0 + 1.0,
                        direction[2] * 10.0),
              count=20, scale=0.8, spread=0.15, chunk_type='spark')
    _shake(1.0)
    _seq(ppos, (0, 'super_punch', 1.0), (0, 'swip2', 1.0),
         (0.02, 'laser_reverse', 0.6))
    if target is not None:  # Lock-on chirp at the target.
        _seq(target.position, (0, 'activate_beep', 0.8),
             (0.08, 'race_beep1', 0.5))
    _start_homing(bomb, node, target, direction, tour=tour)


def _start_homing(bomb: Bomb, sender: bs.Node | None,
                  target: bs.Node | None,
                  direction: Sequence[float],
                  tour: list[bs.Node] | None = None) -> None:
    """Send the bomb flying at the target (straight on if there's none)."""
    bnode = bomb.node
    _unleash(bnode)
    # Kept on the bomb so a punch from its target can turn it around. A
    # ball punched again keeps what it had: its speed, how many times it
    # was returned and whether it already did the panda move.
    prev = getattr(bomb, '_bst_homing', None) or {}
    if prev.get('panda') is not None:
        _end_panda(prev)
    speed0 = max(IMPACT_SPEED, prev.get('speed', IMPACT_SPEED))
    state: dict[str, Any] = {
        'time': 0.0,
        'target': target,
        'sender': sender,
        # Who it goes round: sender, target, then the rest (see
        # _next_in_round).
        'order': [n for n in (sender, target) if n],
        'speed': speed0,
        'deflects': prev.get('deflects', 0),
        'panda_done': prev.get('panda_done', False),
        # The ball game's ball glides low and curves (see _low_fly).
        'low': getattr(bomb, '_bst_ball_game', None) is not None,
        'pingpong': (prev.get('pingpong', False)
                     or getattr(bomb, '_bst_ball_game', None) is not None),
        'dir': direction,
        'vel': tuple(c * speed0 for c in direction),
        'last': bnode.position,
        'slow': 0,
        'avoid_until': 0.0,
        'avoid_dir': direction,
        'attempt': 0,
        'tour': list(tour or []),
        'touring': tour is not None,
        'tour_owner': sender if tour is not None else None,
        'ice_owner': getattr(bomb, '_bst_ice_owner', None),
        'ice_route': list(getattr(bomb, '_bst_ice_route', [])),
    }
    bomb._bst_homing = state  # type: ignore[attr-defined]
    _speed_label(bomb, speed0)

    def _stop() -> None:
        bomb._bst_flight = None  # type: ignore[attr-defined]

    def _step() -> None:
        state['time'] += _TICK
        if not bnode or getattr(bomb, '_exploded', False):
            _stop()
            return
        tnow = state['time']
        bpos = bnode.position
        if state.get('panda') is not None:
            _panda_step(bomb, state)
            return
        target = state['target']
        # Speeds up the whole flight.
        state['speed'] = speed = min(DEFLECT_MAX_SPEED,
                                     state['speed'] + IMPACT_ACCEL * _TICK)
        _speed_label(bomb, speed)

        if target is None:
            if tnow > 2.0:
                _stop()  # Let physics take over.
                return
            fdir = state['dir']
        else:
            victim = target.getdelegate(Spaz) if target else None
            if victim is None or not victim.is_alive() or (
                tnow > IMPACT_FLIGHT_TIME
            ):
                if getattr(bomb, '_bst_ice_orb', False):
                    _ice_orb_advance(bomb, None, freeze=False)
                    return
                if state.get('touring'):
                    _impact_tour_hit(bomb, None)
                    return
                _stop()
                if getattr(bomb, '_bst_ice_orb', False):
                    bomb.handlemessage(bs.DieMessage())
                else:
                    bomb.handlemessage(ExplodeMessage())
                return
            tpos = target.position_center
            want, dist = _norm([a - b for a, b in zip(tpos, bpos)])
            # Ball-game bots see it coming and time their swing.
            ready = getattr(victim, 'bsm_ball_incoming', None)
            if ready is not None:
                ready(bomb, dist, speed)
            if state.get('low'):
                # The ball game counts only what physically happens: a real
                # fist on the ball (Spaz punch message) or a real bump (its
                # impact). This is just a backstop.
                if dist < 0.4:
                    _stop()
                    bomb.handlemessage(ExplodeMessage())
                    return
                _pingpong_fly(bomb, bnode, state, want, speed)
                return
            # It goes off when it physically touches them (see
            # _patched_bomb_handle_impact); this is only a backstop - which
            # checks the whole path since last tick, so a fast bomb can't
            # skip past them.
            # Fist or body - whichever it meets first along its path since
            # the last tick (so it can't skip past them at any speed).
            body_t = _seg_hit_t(state['last'], bpos, tpos, 0.7)
            if (getattr(victim, '_ab_active', False)
                    and (dist < 0.55 or body_t is not None)):
                if getattr(bomb, '_bst_ice_orb', False):
                    _ice_orb_advance(bomb, target, freeze=False)
                    return
                if state.get('touring'):
                    _impact_tour_hit(bomb, target, damage=False)
                    return
            if _try_contact_deflect(bomb, state['last'], bpos, body_t):
                return  # Knocked back.
            if dist < 0.55 or body_t is not None:
                if getattr(bomb, '_bst_ice_orb', False):
                    _ice_orb_advance(bomb, target, freeze=True)
                    return
                if state.get('touring'):
                    _impact_tour_hit(bomb, target)
                    return
                _stop()
                _snd('big_impact', 1.0, bpos)
                bomb.handlemessage(ExplodeMessage())
                return
            # Aim a little above their middle so the line clears slopes
            # (domes like Doom Shroom).
            want, _ = _norm((tpos[0] - bpos[0], tpos[1] + 0.25 - bpos[1],
                             tpos[2] - bpos[2]))
            if state.get('pingpong'):
                _pingpong_fly(bomb, bnode, state, want, speed)
                return

            # Truly stuck (barely moving for a while)? Try going over,
            # under or around it, a different way each time.
            _, moved = _norm([a - b for a, b in zip(bpos, state['last'])])
            _, speed_now = _norm(state['vel'])
            if tnow > 0.15 and moved < speed_now * _TICK * 0.35:
                state['slow'] += 1
            else:
                state['slow'] = 0
            if state['slow'] >= 4 and tnow >= state['avoid_until']:
                dirs = _avoid_dirs(want)
                state['avoid_dir'] = dirs[state['attempt'] % len(dirs)]
                state['attempt'] += 1
                state['avoid_until'] = tnow + 0.15
                state['slow'] = 0
            fdir = state['avoid_dir'] if tnow < state['avoid_until'] else want
            if tnow < state.get('route_turn_until', 0.0):
                fdir = state['route_turn_dir']
            # Scraping the floor: just lift off it a bit and slide along.
            if bs.time() - getattr(bomb, '_bst_bump_time', -9.0) < 0.12:
                fdir, _ = _norm((fdir[0], fdir[1] + 0.35, fdir[2]))
            state['dir'] = fdir

        state['last'] = bpos
        # Turn smoothly instead of snapping to the new heading.
        goal = tuple(c * speed for c in fdir)
        steer = IMPACT_TOUR_STEER if state.get('touring') else IMPACT_STEER
        vel = tuple(v + (g - v) * steer
                    for v, g in zip(state['vel'], goal))
        state['vel'] = vel
        bnode.velocity = vel
        bs.emitfx(position=bpos, velocity=tuple(-c * 2.0 for c in fdir),
                  count=2, scale=0.5, spread=0.1, chunk_type='spark')

    # Kept on the bomb (which the game keeps alive) so it can't be
    # garbage-collected mid-flight.
    bomb._bst_flight = bs.Timer(  # type: ignore[attr-defined]
        _TICK, _step, repeat=True
    )
    _step()
    if target is not None:
        _track_ball(bomb)  # Light up who it's after and who's next.


def _impact_tour_hit(bomb: Bomb, target: bs.Node | None,
                     damage: bool = True) -> None:
    """Tag one fighter and send a full-charge impact bomb to the next."""
    state = getattr(bomb, '_bst_homing', None)
    if state is None or not bomb.node:
        return
    if target is not None and target and damage:
        direction, _ = _norm(state.get('vel', (0.0, 1.0, 0.0)))
        _route_blast(bomb, target.position_center, direction, ice=False)
        target.handlemessage(bs.HitMessage(
            pos=target.position_center,
            source_player=bs.existing(bomb.get_source_player(bs.Player)),
            force_direction=direction,
            flat_damage=ROUTE_KILL_DAMAGE,
            hit_type='explosion',
            hit_subtype='impact',
        ))
    elif target is not None and target:
        _ring(target.position_center, (1.0, 0.45, 0.15), 2.2, 0.2)
        _snd('shield_hit', 0.8, target.position_center)

    next_target = _next_impact_target(state)
    if next_target is None:
        state['touring'] = False
        bomb._bst_flight = None  # type: ignore[attr-defined]
        bomb.handlemessage(bs.DieMessage())
        return
    state.update({
        'target': next_target,
        'time': 0.0,
        'last': bomb.node.position,
        'slow': 0,
        'avoid_until': 0.0,
        'attempt': 0,
    })
    _start_route_turn(bomb, state, next_target)
    _snd('activate_beep', 0.7, next_target.position_center)


def _next_impact_target(state: dict) -> bs.Node | None:
    """Take the next living enemy left in a full-charge impact tour."""
    target = state.pop('tour_resume', None)
    victim = target.getdelegate(Spaz) if target else None
    if victim is not None and victim.is_alive():
        return target
    route = state.setdefault('tour', [])
    while route:
        target = route.pop(0)
        victim = target.getdelegate(Spaz) if target else None
        if victim is not None and victim.is_alive():
            return target
    return None


def _start_route_turn(bomb: Bomb, state: dict, target: bs.Node) -> None:
    """Make a clearly visible side-step before homing onto the next target."""
    if not bomb.node or not target:
        return
    toward, length = _norm([
        target.position_center[k] - bomb.node.position[k] for k in range(3)
    ])
    if length < 1e-4:
        return
    side, _ = _perp_basis(toward)
    sign = -1.0 if state.get('route_turn_side', 1.0) > 0.0 else 1.0
    turn, _ = _norm((side[0] * sign + toward[0] * 0.15,
                     0.45 + toward[1] * 0.15,
                     side[2] * sign + toward[2] * 0.15))
    speed = state.get('speed', IMPACT_SPEED)
    velocity = tuple(component * speed for component in turn)
    state['dir'] = turn
    state['vel'] = velocity
    state['route_turn_dir'] = turn
    state['route_turn_until'] = ROUTE_TURN_TIME
    state['route_turn_side'] = sign
    bomb.node.velocity = velocity


def _route_blast(bomb: Bomb, position: Sequence[float],
                 direction: Sequence[float], ice: bool) -> None:
    """A real blast at a route stop, offset so it spares its projectile."""
    source = bomb.get_source_player(bs.Player)
    # Leave the blast just behind the projectile. Its diameter remains large
    # enough to cover the fighter it touched without catching the projectile
    # as it immediately banks away.
    center = tuple(position[k] - direction[k] * 0.45 for k in range(3))
    Blast(
        position=center,
        velocity=tuple(direction[k] * 2.0 for k in range(3)),
        blast_radius=ROUTE_BLAST_RADIUS,
        blast_type='ice' if ice else 'impact',
        source_player=source,
        hit_type='explosion',
        hit_subtype='ice' if ice else 'impact',
    ).autoretain()


def _try_contact_deflect(bomb: Bomb, last: Sequence[float],
                         bpos: Sequence[float],
                         body_t: float | None = None) -> bool:
    """Its target returns the ball if they're punching (within
    DEFLECT_WINDOW) and it meets them on its way since the last tick:

    * on normal maps it has to touch their fist (FIST_RADIUS around it);
    * on Happy Thoughts, where fists in mid-air are hard to line up, a
      small zone around the fighter (FLY_DEFLECT_ZONE) is enough.

    Checked along the whole path, so it works at any speed, any number of
    times."""
    state = getattr(bomb, '_bst_homing', None)
    if state is None or getattr(bomb, '_bst_flight', None) is None:
        return False
    target = state.get('target')
    spaz = target.getdelegate(Spaz) if target else None
    if spaz is None or not spaz.is_alive() or not spaz.node:
        return False
    since = bs.time() * 1000.0 - getattr(spaz, 'last_punch_time_ms', -9999)
    if since > DEFLECT_WINDOW * 1000.0:
        return False
    if getattr(spaz, 'bsm_ball_incoming', None) is not None:
        return False  # Ball-game bots decide for themselves.
    if getattr(spaz, 'fly', False):
        hit_t = _seg_hit_t(last, bpos, target.position_center,
                           FLY_DEFLECT_ZONE)
    else:
        # Where the fist is: out in front of them. (The engine's own
        # punch_position is gone - with a warning - once the punch ends.)
        look = _look_dir(spaz)
        center = target.position_center
        fist = tuple(center[k] + look[k] * 0.55 for k in range(3))
        hit_t = _seg_hit_t(last, bpos, fist, FIST_RADIUS)
        if body_t is None:
            body_t = _seg_hit_t(last, bpos, center, 0.7)
        # Coming at them from the front while they punch: the fist is in
        # its way, whatever the height it drops in at.
        come, clen = _norm([a - b for a, b in zip(last, center)])
        if (body_t is not None and clen > 1e-4
                and sum(come[k] * look[k] for k in range(3)) > 0.5
                and (hit_t is None or hit_t > body_t)):
            hit_t = body_t
    # It has to meet the fist (or zone) before it meets the body.
    if hit_t is None or (body_t is not None and hit_t > body_t):
        return False
    _deflect_homing(spaz, bomb)
    return True


def _deflect_homing(spaz: Spaz, bomb: Bomb) -> None:
    """Its target punched the homing bomb: on like a ball to the next one
    round (back at the sender when it's just the two of them)."""
    state = bomb._bst_homing  # type: ignore[attr-defined]
    node = spaz.node
    if getattr(bomb, '_bst_ice_orb', False):
        owner = state.get('ice_owner')
        if node == owner:
            back_to = state.pop('ice_resume', None)
            victim = back_to.getdelegate(Spaz) if back_to else None
            if victim is None or not victim.is_alive():
                back_to = _next_ice_target(state)
        else:
            state['ice_resume'] = _next_ice_target(state)
            back_to = owner
    elif state.get('touring'):
        owner = state.get('tour_owner')
        if node == owner:
            back_to = _next_impact_target(state)
        else:
            state['tour_resume'] = _next_impact_target(state)
            back_to = owner
    else:
        back_to = _next_in_round(state, node)
    bpos = bomb.node.position
    if state.get('low') and back_to is not None:
        heading = _hit_heading(spaz, back_to, bpos, min(
            DEFLECT_MAX_SPEED, state['speed'] * DEFLECT_SPEEDUP))
    elif back_to is not None:
        heading, _ = _norm([a - b for a, b in zip(back_to.position_center,
                                                  bpos)])
    else:
        heading, _ = _norm(node.punch_velocity)
        bomb._bst_levitate = False  # type: ignore[attr-defined]
    speed = min(DEFLECT_MAX_SPEED, state['speed'] * DEFLECT_SPEEDUP)
    state.update({
        'target': back_to,
        'sender': node,
        'speed': speed,
        'time': 0.0,
        'dir': heading,
        'vel': tuple(c * speed for c in heading),  # Bounces right back.
        'slow': 0,
        'avoid_until': 0.0,
        'attempt': 0,
        'pingpong': (not getattr(bomb, '_bst_ice_orb', False)
                     and not state.get('touring')),
        'deflects': state.get('deflects', 0) + 1,
    })
    # The deflector is now the one it won't go off on, and gets the credit.
    bomb.owner = node
    if spaz.source_player is not None:
        bomb._source_player = spaz.source_player  # type: ignore[attr-defined]
    bomb.node.velocity = state['vel']
    _let_go(state, bomb)  # Knocked out of the rider's hands.

    if ((getattr(bomb, '_bst_ice_orb', False) or state.get('touring'))
            and back_to is None):
        bomb._bst_flight = None  # type: ignore[attr-defined]
        if getattr(bomb, '_bst_ice_orb', False):
            bomb.handlemessage(bs.DieMessage())
        else:
            bomb.handlemessage(ExplodeMessage())
        return

    if (not getattr(bomb, '_bst_ice_orb', False)
            and not state.get('touring')
            and speed >= PANDA_SPEED and back_to is not None
            and not state.get('panda_done')):
        _start_panda(spaz, bomb, state)
        return

    _flash(bpos, _bright(_color(spaz), 2.0), 0.6, 1.0, 1.5, 0.15)
    # A clean, showy return: sparks fanned along the new heading and a ring
    # of them around it, the air rippling.
    bs.emitfx(position=bpos, velocity=tuple(c * 12.0 for c in heading),
              count=30, scale=1.0, spread=0.15, chunk_type='spark')
    side, up = _perp_basis(heading)
    for i in range(16):
        ang = 2.0 * math.pi * i / 16
        out = tuple(side[k] * math.cos(ang) + up[k] * math.sin(ang)
                    for k in range(3))
        bs.emitfx(position=bpos,
                  velocity=tuple(out[k] * 7.0 + heading[k] * 2.0
                                 for k in range(3)),
                  count=1, scale=0.8, spread=0.0, chunk_type='spark')
    bs.emitfx(position=bpos, emit_type='distortion', spread=0.8)
    _shake(0.8)
    _seq(bpos, (0, 'punch_strong01', 1.0), (0, 'impact_hard', 0.8),
         (0.02, 'swip2', 0.9))
    if back_to is not None:
        _snd('activate_beep', 0.8, back_to.position)


def _unleash(node: bs.Node) -> None:
    """Bombs are capped at about 10 m/s by the engine (prop max_speed):
    lift it for anything we fly ourselves, or it never gets faster."""
    try:
        node.max_speed = 200.0
    except Exception:
        pass


def _speed_label(bomb: Bomb, speed: float) -> None:
    """Its speed over the ball, all the way."""
    text = f'{speed:.0f} м/с'
    label = getattr(bomb, '_bst_speed_text', None)
    try:
        if label is None or not label:
            bnode = bomb.node
            above = bs.newnode('math', owner=bnode, attrs={
                'input1': (0.0, 0.6, 0.0), 'operation': 'add'})
            bnode.connectattr('position', above, 'input2')
            label = bs.newnode('text', owner=bnode, attrs={
                'text': text, 'in_world': True, 'h_align': 'center',
                'flatness': 1.0, 'shadow': 1.0, 'scale': 0.011,
                'color': _speed_color(speed)})
            above.connectattr('output', label, 'position')
            bomb._bst_speed_text = label  # type: ignore[attr-defined]
        elif label.text != text:
            label.text = text
            label.color = _speed_color(speed)
    except Exception:
        pass  # Only a label: never in the way of the ball.


def _speed_color(speed: float) -> tuple[float, float, float]:
    """White when slow, through yellow to red at top speed."""
    frac = max(0.0, min(1.0, (speed - IMPACT_SPEED)
                        / (DEFLECT_MAX_SPEED - IMPACT_SPEED)))
    return (1.0, 1.0 - 0.75 * frac, 1.0 - frac)


def _live_fighters() -> list[bs.Node]:
    out = []
    for node in bs.getnodes():
        if not node or node.getnodetype() != 'spaz':
            continue
        spaz = node.getdelegate(Spaz)
        if spaz is not None and spaz.is_alive():
            out.append(node)
    return out


def _next_in_round(state: dict, after: bs.Node) -> bs.Node | None:
    """Who the ball goes to once `after` returns it: the next one round
    (1 → 2 → 3 → … → 1), skipping the dead and the deflector's own team.
    With two fighters that's simply back and forth."""
    order: list = state.setdefault('order', [])
    if after not in order:
        order.append(after)
    # Newcomers join the round in random order (not just the nearest).
    rest = [n for n in _live_fighters() if n not in order]
    random.shuffle(rest)
    order.extend(rest)
    me = after.getdelegate(Spaz)
    start = order.index(after)
    for step in range(1, len(order)):
        node = order[(start + step) % len(order)]
        other = node.getdelegate(Spaz) if node else None
        if other is None or not other.is_alive():
            continue
        if me is None or _is_enemy(me, other):
            return node
    return None


# The ball's current target's name pulses red, the next one round (who
# should get ready) glows yellow. One keeper per game looks after all balls
# and puts names back once nobody's after them.
_MARK_TARGET = ((1.0, 0.15, 0.1), (1.0, 0.65, 0.55))
_MARK_NEXT = (1.0, 0.85, 0.15)
_MARK_TICK = 0.1


def _track_ball(bomb: Bomb) -> None:
    try:
        activity = bs.getactivity()
        keeper = activity.customdata.get('bsm_ball_marks')
        if keeper is None:
            keeper = {'balls': [], 'orig': {}, 'time': 0.0, 'timer': None}
            activity.customdata['bsm_ball_marks'] = keeper
        if not any(ref() is bomb for ref in keeper['balls']):
            keeper['balls'].append(weakref.ref(bomb))
        if keeper['timer'] is None:
            keeper['timer'] = bs.Timer(
                _MARK_TICK, bs.CallStrict(_marks_tick, keeper), repeat=True)
        _marks_tick(keeper)
    except Exception:
        pass  # Only cosmetics: never in the way of the ball itself.


def _marks_tick(keeper: dict) -> None:
    keeper['time'] += _MARK_TICK
    roles: dict = {}
    balls = []
    for ref in keeper['balls']:
        bomb = ref()
        state = getattr(bomb, '_bst_homing', None)
        if (state is None or not bomb.node
                or getattr(bomb, '_exploded', False)
                or getattr(bomb, '_bst_flight', None) is None):
            continue
        balls.append(ref)
        target = state.get('target')
        if not target:
            continue
        upcoming = _next_in_round(state, target)
        if upcoming and upcoming not in roles:
            roles[upcoming] = 'next'
        roles[target] = 'target'
    keeper['balls'] = balls
    orig = keeper['orig']
    wave = 0.5 + 0.5 * math.sin(keeper['time'] * 14.0)
    hot, soft = _MARK_TARGET
    for node, role in roles.items():
        if node not in orig:
            orig[node] = (node.name, node.name_color)
            if not node.name:
                node.name = '●'  # Nameless (bots): a dot to light up.
        node.name_color = (tuple(h + (s - h) * wave for h, s in zip(hot, soft))
                           if role == 'target' else _MARK_NEXT)
    for node in list(orig):
        if node in roles:
            continue
        name, color = orig.pop(node)
        if node:
            node.name = name
            node.name_color = color
    if not balls and not orig:
        keeper['timer'] = None


def _seg_hit_t(a: Sequence[float], b: Sequence[float], p: Sequence[float],
               radius: float) -> float | None:
    """How far along a-b (0..1) it first comes within radius of p, if at
    all."""
    d = [b[k] - a[k] for k in range(3)]
    f = [a[k] - p[k] for k in range(3)]
    qa = sum(c * c for c in d)
    qc = sum(c * c for c in f) - radius * radius
    if qc <= 0.0:
        return 0.0  # Already inside at the start.
    if qa < 1e-12:
        return None
    qb = 2.0 * sum(d[k] * f[k] for k in range(3))
    disc = qb * qb - 4.0 * qa * qc
    if disc < 0.0:
        return None
    t = (-qb - math.sqrt(disc)) / (2.0 * qa)
    return t if 0.0 <= t <= 1.0 else None


def _seg_dist(a: Sequence[float], b: Sequence[float],
              p: Sequence[float]) -> float:
    """Distance from point p to the segment a-b."""
    ab = [b[k] - a[k] for k in range(3)]
    ap = [p[k] - a[k] for k in range(3)]
    len2 = sum(c * c for c in ab)
    t = 0.0 if len2 < 1e-9 else max(0.0, min(1.0, sum(
        ab[k] * ap[k] for k in range(3)) / len2))
    return math.dist(p, [a[k] + ab[k] * t for k in range(3)])


def _turn_toward(cur: Sequence[float], want: Sequence[float],
                 max_angle: float) -> tuple[float, float, float]:
    """Rotate a heading toward another by at most max_angle radians."""
    cos = max(-1.0, min(1.0, sum(a * b for a, b in zip(cur, want))))
    angle = math.acos(cos)
    if angle <= max_angle:
        return tuple(want)
    frac = max_angle / angle
    return _norm([a + (b - a) * frac for a, b in zip(cur, want)])[0]


def _perp_basis(fwd: Sequence[float]) -> tuple[tuple, tuple]:
    side, slen = _norm((-fwd[2], 0.0, fwd[0]))
    if slen < 1e-4:
        side = (1.0, 0.0, 0.0)
    up = (side[1] * fwd[2] - side[2] * fwd[1],
          side[2] * fwd[0] - side[0] * fwd[2],
          side[0] * fwd[1] - side[1] * fwd[0])
    return side, up


def _ball_turn_rate(speed: float) -> float:
    return max(BALL_TURN, speed / BALL_TURN_RADIUS)


def _arc_heading(start: Sequence[float], toward: bs.Node,
                 wish: Sequence[float], speed: float) -> tuple:
    """The way the ball leaves (wish), but never so far off that its soft
    arc can't reach the target."""
    aim, dist = _norm((toward.position[0] - start[0], 0.0,
                       toward.position[2] - start[2]))
    wish, wlen = _norm((wish[0], 0.0, wish[2]))
    if dist < 1e-4:
        return wish if wlen > 1e-4 else (1.0, 0.0, 0.0)
    if wlen < 1e-4:
        return aim
    # An arc of radius R through a target d away leaving at angle a to it
    # needs d >= 2 R sin(a); keep a margin.
    radius = speed / _ball_turn_rate(speed)
    limit = math.asin(min(1.0, 0.45 * dist / radius))
    diff = math.atan2(aim[0] * wish[2] - aim[2] * wish[0],
                      aim[0] * wish[0] + aim[2] * wish[2])
    return _turn_flat(aim, max(-limit, min(limit, diff)))


def _hit_heading(spaz: Spaz, toward: bs.Node, start: Sequence[float],
                 speed: float) -> tuple:
    """Ball game: the ball leaves the way it was hit - where a player was
    facing, a bot's somewhat to one side - and curves round to the next
    one from there."""
    if getattr(spaz, 'bsm_team', None) is None:
        wish = _look_dir(spaz)
    else:
        pos = spaz.node.position
        wish = _turn_flat(
            _norm((toward.position[0] - pos[0], 0.0,
                   toward.position[2] - pos[2]))[0],
            math.radians(random.uniform(-BALL_HIT_SPREAD, BALL_HIT_SPREAD)))
    return _arc_heading(start, toward, wish, speed)


def _catch(spaz: Spaz, bomb: Bomb) -> None:
    """Ball game: someone caught it - it flies on to the next one round
    after them, hauling them along to smash it into them."""
    state = bomb._bst_homing  # type: ignore[attr-defined]
    node = spaz.node
    bnode = bomb.node
    if state.get('rider') == node:
        return
    onward = _next_in_round(state, node)
    if onward is None:
        return
    _let_go(state, bomb)  # Snatched from whoever was riding it.
    if node.hold_node != bnode:
        spaz._pick_up(bnode)
    speed = state['speed']
    heading = _hit_heading(spaz, onward, bnode.position, speed)
    state.update({
        'target': onward,
        'sender': node,
        'rider': node,
        'deflects': state.get('deflects', 0) + 1,
        'time': 0.0,
        'dir': heading,
        'vel': tuple(c * speed for c in heading),
        'last': bnode.position,
    })
    bomb.owner = node
    if spaz.source_player is not None:
        bomb._source_player = spaz.source_player  # type: ignore[attr-defined]
    bnode.velocity = state['vel']
    pos = bnode.position
    bs.emitfx(position=pos, velocity=tuple(c * 6.0 for c in heading),
              count=20, scale=0.8, spread=0.3, chunk_type='spark')
    _popup_text('ПОЙМАЛ!', node.position, _bright(_color(spaz), 1.0))
    _seq(pos, (0, 'swip2', 0.9), (0, 'impact_hard', 0.6),
         (0.05, 'activate_beep', 0.7))


def _let_go(state: dict, bomb: Bomb) -> None:
    """Whoever was riding the ball lets go of it."""
    rider = state.get('rider')
    state['rider'] = None
    if rider and bomb.node and rider.hold_node == bomb.node:
        rider.hold_node = None


def _turn_flat(vec: Sequence[float], angle: float) -> tuple:
    """A level heading turned by angle radians."""
    ca, sa = math.cos(angle), math.sin(angle)
    return (vec[0] * ca - vec[2] * sa, 0.0, vec[0] * sa + vec[2] * ca)


def _low_fly(bomb: Bomb, bnode: bs.Node, state: dict, speed: float) -> None:
    """The ball game's ball: glides at chest height (never up high) and
    swings round to its target in a soft arc."""
    target = state['target']
    bpos = bnode.position
    rider = state.get('rider')
    if rider is not None and (not rider or rider.hold_node != bnode):
        state['rider'] = rider = None  # Thrown or dropped: flies on alone.
    if rider is not None:
        speed *= BALL_RIDE_BOOST  # Hauling someone along.
    tpos = target.position_center
    cur = state['dir']
    cur, clen = _norm((cur[0], 0.0, cur[2]))
    want, wlen = _norm((tpos[0] - bpos[0], 0.0, tpos[2] - bpos[2]))
    if clen < 1e-4:
        cur = want
    if wlen > 1e-4:
        # Signed angle to the target, turned by no more than the soft rate
        # (quicker only if it got past them or is against a wall).
        diff = math.atan2(cur[0] * want[2] - cur[2] * want[0],
                          cur[0] * want[0] + cur[2] * want[2])
        rate = _ball_turn_rate(speed)
        if abs(diff) > math.pi / 2.0 or bs.time() - getattr(
                bomb, '_bst_bump_time', -9.0) < 0.15:
            rate *= 2.0
        step = rate * _TICK
        cur = _turn_flat(cur, max(-step, min(step, diff)))
    state['dir'] = cur
    # Height: eases to the target's chest, gently.
    climb = max(-3.0, min(3.0, (tpos[1] + 0.1 - bpos[1]) * 4.0))
    state['spin'] = state.get('spin', 0.0) + SPIRAL_RATE * _TICK
    wobble = math.sin(state['spin']) * SPIRAL_RADIUS * SPIRAL_RATE * 0.5
    vel = (cur[0] * speed - cur[2] * wobble, climb,
           cur[2] * speed + cur[0] * wobble)
    state['vel'] = vel
    state['last'] = bpos
    bnode.velocity = vel
    bs.emitfx(position=bpos, velocity=tuple(-c * 3.0 for c in cur),
              count=2 + int(speed / 8.0), scale=1.0, spread=0.12,
              chunk_type='spark')
    if int(state['spin'] * 3) % 2 == 0:
        bs.emitfx(position=bpos, velocity=(0, 0.5, 0), count=1, scale=0.7,
                  spread=0.05, chunk_type='sweat')


def _pingpong_fly(bomb: Bomb, bnode: bs.Node, state: dict,
                  want: Sequence[float], speed: float) -> None:
    """A knocked-back ball: smooth turns only, a gentle even spiral, big
    sparks. Bumping into floors/walls just eases it upward."""
    if state.get('low') and state.get('target') is not None:
        _low_fly(bomb, bnode, state, speed)
        return
    # Faster ball, tighter turns (so it never sails past at 40+ m/s); on
    # the final approach it simply flies straight in - it's lined up by then.
    turn = max(PINGPONG_TURN, speed / 3.0) * _TICK
    target = state['target']
    near = target is not None and math.dist(
        target.position_center, bnode.position) < speed * 0.3
    heading = tuple(want) if near else _turn_toward(state['dir'], want, turn)
    if bs.time() - getattr(bomb, '_bst_bump_time', -9.0) < 0.15:
        # Against a wall or the floor (even on the final approach): ease up
        # and over it.
        climb, _ = _norm((heading[0], heading[1] + 0.8, heading[2]))
        heading = climb if near else _turn_toward(heading, climb, turn)
    state['dir'] = heading
    state['spin'] = state.get('spin', 0.0) + SPIRAL_RATE * _TICK
    side, up = _perp_basis(heading)
    ca, sa = math.cos(state['spin']), math.sin(state['spin'])
    swirl = SPIRAL_RADIUS * SPIRAL_RATE
    vel = tuple(heading[k] * speed + (side[k] * -sa + up[k] * ca) * swirl
                for k in range(3))
    state['vel'] = vel
    state['last'] = bnode.position
    bnode.velocity = vel
    bpos = bnode.position
    # The faster it goes, the thicker its trail.
    bs.emitfx(position=bpos, velocity=tuple(-c * 3.0 for c in heading),
              count=2 + int(speed / 8.0), scale=1.0, spread=0.12,
              chunk_type='spark')
    if int(state['spin'] * 3) % 2 == 0:
        bs.emitfx(position=bpos, velocity=(0, 0.5, 0), count=1, scale=0.7,
                  spread=0.05, chunk_type='sweat')


def _cone_blast(bomb: Bomb) -> None:
    """A ball that's been knocked back and forth goes off as a powerful
    blast cone in the direction it flew, at whoever failed to return it."""
    bomb._exploded = True  # pylint: disable=protected-access
    bomb._bst_flight = None  # type: ignore[attr-defined]
    bnode = bomb.node
    if not bnode:
        return
    state = bomb._bst_homing  # type: ignore[attr-defined]
    pos = bnode.position
    # Level on the ground: a ball that dives in from above still blasts on
    # past them, not into the floor. (In mid-air on Happy Thoughts it
    # keeps the angle it flew in at.)
    fly = state.get('dir', (1.0, 0.0, 0.0))
    target = state.get('target')
    victim = target.getdelegate(Spaz) if target else None
    tilt = 1.0 if getattr(victim, 'fly', False) else 0.0
    fwd, flen = _norm((fly[0], fly[1] * tilt, fly[2]))
    if flen < 0.2:
        fwd = (1.0, 0.0, 0.0)
    damage = CONE_DAMAGE + _bomb_charge(bomb)
    min_cos = math.cos(math.radians(CONE_ANGLE / 2.0))
    source = bomb.get_source_player(bs.Player)
    sender = state.get('sender')
    for other in bs.getnodes():
        if (not other or other == sender
                or other.getnodetype() not in ('spaz', 'prop', 'bomb')
                or other == bnode):
            continue
        opos = (other.position_center if other.getnodetype() == 'spaz'
                else other.position)
        to, dist = _norm([a - b for a, b in zip(opos, pos)])
        inside = dist < 0.8 or (
            dist <= CONE_LENGTH
            and sum(a * b for a, b in zip(to, fwd)) >= min_cos)
        if not inside:
            continue
        power = 1.0 - 0.5 * min(1.0, dist / CONE_LENGTH)
        push = fwd if dist < 0.8 else to
        other.handlemessage(
            'impulse', opos[0], opos[1], opos[2], 0.0, 0.0, 0.0,
            1800.0 * power, 120.0 * power, 0.0, 0,
            push[0], push[1] + 0.35, push[2],
        )
        if other.getnodetype() == 'spaz':
            other.handlemessage(
                bs.HitMessage(
                    pos=opos,
                    source_player=bs.existing(source),
                    force_direction=push,
                    flat_damage=damage * power,
                    hit_type='explosion',
                    hit_subtype='normal',
                )
            )
    # Fire rolling down the cone, growing as it goes.
    for i in range(6):
        along = 0.4 + i * CONE_LENGTH / 6.0
        bs.timer(0.025 * i, bs.CallStrict(
            _cone_fire, tuple(pos[k] + fwd[k] * along for k in range(3)),
            0.5 + 0.22 * i))
    side, up = _perp_basis(fwd)
    spread = math.tan(math.radians(CONE_ANGLE / 2.0))
    for _ in range(14):
        ang = random.uniform(0.0, 2.0 * math.pi)
        rad = random.uniform(0.0, spread)
        ray = _norm([fwd[k] + (side[k] * math.cos(ang) + up[k]
                               * math.sin(ang)) * rad for k in range(3)])[0]
        bs.emitfx(position=pos, velocity=tuple(c * 22.0 for c in ray),
                  count=6, scale=1.1, spread=0.05, chunk_type='spark')
    bs.emitfx(position=pos, emit_type='distortion', spread=2.0)
    scorch = bs.newnode('scorch', attrs={'position': pos, 'size': 1.2,
                                         'big': False})
    bs.animate(scorch, 'presence', {3.0: 1.0, 10.0: 0.0})
    bs.timer(10.0, scorch.delete)
    _shake(3.0)
    _seq(pos, (0, 'explosion01', 1.0), (0, 'big_impact', 1.0),
         (0.03, 'explosion03', 0.9), (0.05, 'orchestra_hit_big1', 0.9),
         (0.08, 'big_impact2', 0.8), (0.12, 'gong', 0.6),
         (0.2, 'debris_fall', 0.6))
    bomb.handlemessage(bs.DieMessage())


def _cone_fire(pos: Sequence[float], radius: float) -> None:
    expl = bs.newnode('explosion', attrs={'position': pos, 'radius': radius})
    bs.timer(1.0, expl.delete)


def _start_panda(spaz: Spaz, bomb: Bomb, state: dict) -> None:
    """"Inner peace": time slows, the bomb flows around the deflector in a
    wide circle and is sent back (Kung Fu Panda 2's cannonball catch)."""
    node = spaz.node
    gnode = bs.getactivity().globalsnode
    state['panda_done'] = True
    panda = {
        'time': 0.0,
        'spaz': node,
        'ang': math.atan2(bomb.node.position[2] - node.position[2],
                          bomb.node.position[0] - node.position[0]),
        'gnode': gnode,
        'slow': True,
        'bomb': weakref.ref(bomb),
    }
    state['panda'] = panda
    _slowmo_on(gnode)
    # Never knocks the deflector over while it circles them.
    try:
        ghost = _PandaFactory.get().no_fighters
        bomb.node.materials = bomb.node.materials + (ghost,)
        panda['ghost'] = ghost
    except Exception:
        pass
    # However the bomb ends (even blown up mid-move), time goes back to
    # normal right after the animation.
    bs.timer(PANDA_TIME + 0.15, bs.CallStrict(_end_panda_slowmo, panda))
    col = _bright(_color(spaz), 1.0)
    # A calm ring of light opening around them.
    ring = bs.newnode('locator', attrs={
        'shape': 'circleOutline', 'position': node.position, 'color': col,
        'opacity': 0.0, 'draw_beauty': False, 'additive': True})
    bs.animate_array(ring, 'size', 1, {0: [0.5], PANDA_TIME: [3.2]})
    bs.animate(ring, 'opacity', {0: 0.0, 0.1: 0.6, PANDA_TIME: 0.0})
    bs.timer(PANDA_TIME + 0.05, ring.delete)
    _seq(node.position, (0, 'hiss', 0.6), (0, 'swish', 0.8),
         (0.1, 'ding_small_high', 0.5), (0.3, 'swip', 0.6),
         (0.5, 'swip2', 0.6))


class _PandaFactory:
    """Per-activity material: the circling ball passes through fighters."""

    _STORENAME = 'bsm_panda_factory'

    def __init__(self) -> None:
        shared = SharedObjects.get()
        self.no_fighters = bs.Material()
        self.no_fighters.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False),
            ),
        )

    @classmethod
    def get(cls) -> _PandaFactory:
        activity = bs.getactivity()
        factory = activity.customdata.get(cls._STORENAME)
        if factory is None:
            factory = cls()
            activity.customdata[cls._STORENAME] = factory
        return factory


def _end_panda_slowmo(panda: dict) -> None:
    if panda.get('slow'):
        panda['slow'] = False
        _slowmo_off(panda['gnode'])


def _end_panda(state: dict) -> None:
    """Finish a panda move: time back to normal, the ball solid again."""
    panda = state.get('panda')
    state['panda'] = None
    if panda is None:
        return
    _end_panda_slowmo(panda)
    bomb = panda['bomb']()
    ghost = panda.get('ghost')
    if bomb is not None and bomb.node and ghost is not None:
        try:
            bomb.node.materials = tuple(m for m in bomb.node.materials
                                        if m is not ghost)
        except Exception:
            pass


def _panda_step(bomb: Bomb, state: dict) -> None:
    panda = state['panda']
    bnode = bomb.node
    node = panda['spaz']
    panda['time'] += _TICK
    tnow = panda['time']
    if not node or tnow >= PANDA_TIME:
        # Release: back at the sender, a bit harder (it keeps its speed).
        _end_panda(state)
        target = state['target']
        bpos = bnode.position
        if target:
            heading, _ = _norm([a - b for a, b in
                                zip(target.position_center, bpos)])
        else:
            heading = state['dir']
        speed = min(DEFLECT_MAX_SPEED, state['speed'] * 1.1)
        state['speed'] = speed
        state['dir'] = heading
        state['vel'] = tuple(c * speed for c in heading)
        state['time'] = 0.0
        bnode.velocity = state['vel']
        bs.emitfx(position=bpos, velocity=tuple(c * 10.0 for c in heading),
                  count=40, scale=0.9, spread=0.2, chunk_type='spark')
        bs.emitfx(position=bpos, emit_type='distortion', spread=1.2)
        _shake(1.5)
        _seq(bpos, (0, 'gong', 1.0), (0, 'super_punch', 1.0),
             (0.02, 'orchestra_hit_big2', 0.8), (0.03, 'swip2', 1.0))
        return
    # One flowing circle around them, rising and falling like a wave.
    center = node.position_center
    rate = 2.0 * math.pi / PANDA_TIME
    panda['ang'] += rate * _TICK
    ang = panda['ang']
    radius = 1.8
    goal = (center[0] + math.cos(ang) * radius,
            center[1] + 0.3 + 0.4 * math.sin(ang * 2.0),
            center[2] + math.sin(ang) * radius)
    # Ride the circle smoothly: its own tangent speed plus a soft pull
    # back onto it.
    tangent = (-math.sin(ang) * radius * rate,
               0.8 * math.cos(ang * 2.0) * rate,
               math.cos(ang) * radius * rate)
    bpos = bnode.position
    bnode.velocity = tuple(t + (g - p) * 4.0
                           for t, g, p in zip(tangent, goal, bpos))
    # A flowing ribbon behind it.
    bs.emitfx(position=bpos, velocity=(0, 0.3, 0), count=2, scale=0.7,
              spread=0.05, chunk_type='sweat')
    bs.emitfx(position=bpos, velocity=(0, 0.2, 0), count=1, scale=0.5,
              spread=0.05, chunk_type='spark')


def _shell_pop(shell: Bomb, at: Sequence[float] | None = None) -> None:
    """A mini shell hits: half a health bar off whoever it got, with a
    small, tidy blast (no big shock wave)."""
    if getattr(shell, '_exploded', False) or not shell.node:
        return
    shell._exploded = True  # pylint: disable=protected-access
    shell._bst_flight = None  # type: ignore[attr-defined]
    pos = tuple(at) if at is not None else shell.node.position
    source = shell.get_source_player(bs.Player)
    owner = shell.owner
    for node in bs.getnodes():
        if not node or node == owner or node.getnodetype() != 'spaz':
            continue
        away, dist = _norm([a - b for a, b in zip(node.position_center,
                                                  pos)])
        if dist > SHOT_BLAST_RADIUS:
            continue
        node.handlemessage(
            bs.HitMessage(
                pos=node.position_center,
                source_player=bs.existing(source),
                force_direction=away,
                flat_damage=SHOT_DAMAGE,
                hit_type='explosion',
                hit_subtype='normal',
            )
        )
        node.handlemessage(
            'impulse', pos[0], pos[1], pos[2], 0.0, 0.0, 0.0,
            250.0, 20.0, 0.0, 0, away[0], away[1] + 0.3, away[2],
        )
    expl = bs.newnode('explosion', attrs={'position': pos, 'radius': 0.45})
    bs.timer(1.0, expl.delete)
    bs.emitfx(position=pos, velocity=(0, 2, 0), count=15, scale=0.6,
              spread=0.3, chunk_type='spark')
    _snd('explosion01', 0.6, pos)
    _snd('impact_hard', 0.8, pos)
    shell.handlemessage(bs.DieMessage())


def _bomb_to_shots(spaz: Spaz, bomb: Bomb) -> None:
    """Charged punch on our flying bomb: it breaks into mini shells."""
    charge = _bomb_charge(bomb) or Spaz.bsm_take_charge(spaz)
    bpos = bomb.node.position
    bomb.handlemessage(bs.DieMessage())  # Consumed, never goes off.
    old_count = spaz._bst_shots
    spaz._bst_shots = min(SHOT_MAX, old_count + SHOT_COUNT)
    added = spaz._bst_shots - old_count
    if charge >= MAX_CHARGE_TRIGGER:
        spaz._bst_homing_shots += added
    spaz._bst_shot_charge += charge
    _update_counter(spaz)

    bs.emitfx(position=bpos, velocity=(0, 3, 0), count=15, scale=0.7,
              spread=0.4, chunk_type='metal')
    bs.emitfx(position=bpos, velocity=(0, 4, 0), count=25, scale=0.8,
              spread=0.5, chunk_type='spark')
    _flash(bpos, _bright(_color(spaz), 1.5), 0.6, 1.0, 1.5, 0.2)
    _snd('metal_hit', 1.0, bpos)
    _snd('cork_pop', 0.8, bpos)
    _snd('powerup01', 0.7, bpos)
    label = 'САМОНАВОДКА' if charge >= MAX_CHARGE_TRIGGER else 'СНАРЯДЫ'
    _popup_text(f'{label} x{added}', spaz.node.position,
                _bright(_color(spaz), 1.0))


def _fire_shot(spaz: Spaz) -> None:
    """Fire one mini shell; full-charge shells home smoothly on enemies."""
    node = spaz.node
    spaz._bst_shots -= 1
    homing = spaz._bst_homing_shots > 0
    if homing:
        spaz._bst_homing_shots -= 1
    _update_counter(spaz)

    facing = _look_dir(spaz)
    center = node.position_center
    start = (center[0] + facing[0] * 0.8, center[1] + 0.2 + facing[1] * 0.8,
             center[2] + facing[2] * 0.8)
    vel = tuple(c * SHOT_SPEED for c in facing)
    shot = Bomb(
        position=start,
        velocity=vel,
        bomb_type='impact',
        blast_radius=2.0 / 0.7,  # Impact bombs shrink theirs; keep it full.
        bomb_scale=0.5,
        source_player=spaz.source_player,
        owner=node,
    ).autoretain()
    # Goes off on touching anything right away (not after arming).
    shot._add_material(  # pylint: disable=protected-access
        BombFactory.get().land_mine_blast_material
    )
    shot._bst_shell = True  # type: ignore[attr-defined]

    snode = shot.node
    _unleash(snode)
    col = _bright(_color(spaz), 1.0)
    # Glowing core in the shooter's color.
    glow = bs.newnode('light', owner=snode, attrs={
        'color': col, 'radius': 0.12, 'intensity': 0.8,
        'height_attenuated': False, 'volume_intensity_scale': 0.3})
    snode.connectattr('position', glow, 'position')
    # A double helix of sparks spun around the flight line.
    side, slen = _norm((-facing[2], 0.0, facing[0]))
    if slen < 1e-4:
        side = (1.0, 0.0, 0.0)
    up = (side[1] * facing[2] - side[2] * facing[1],
          side[2] * facing[0] - side[0] * facing[2],
          side[0] * facing[1] - side[1] * facing[0])
    # Flown from the shooter's middle, so someone standing right up close
    # (between them and the muzzle) is hit too.
    state = {
        'time': 0.0,
        'last': center,
        'heading': facing,
        'target': _homing_shot_target(spaz, start, facing) if homing else None,
    }

    def _step() -> None:
        state['time'] += _TICK
        if not snode or getattr(shot, '_exploded', False):
            shot._bst_flight = None  # type: ignore[attr-defined]
            return
        if state['time'] > SHOT_LIFETIME:
            shot._bst_flight = None  # type: ignore[attr-defined]
            shot.handlemessage(ExplodeMessage())
            return
        pos = snode.position
        heading = state['heading']
        target = state['target']
        victim = target.getdelegate(Spaz) if target else None
        if homing and (victim is None or not victim.is_alive()):
            target = _homing_shot_target(spaz, pos, heading)
            state['target'] = target
        if target is not None:
            want, _ = _norm([target.position_center[k] - pos[k]
                             for k in range(3)])
            heading = _turn_toward(
                heading, want, HOMING_SHOT_TURN * _TICK
            )
            state['heading'] = heading
        # The game only lets a fresh bomb go off on contact after 0.2 s
        # (4 m at this speed), so hits are checked here, along the whole
        # way since last tick, from the very first moment.
        hit = _shell_victim(state['last'], pos, node)
        if hit is not None:
            _shell_pop(shot, hit)
            return
        _, moved = _norm([a - b for a, b in zip(pos, state['last'])])
        if state['time'] > _TICK * 1.5 and moved < SHOT_SPEED * _TICK * 0.3:
            _shell_pop(shot)  # Stopped dead: into a wall right away.
            return
        state['last'] = pos
        snode.velocity = tuple(c * SHOT_SPEED for c in heading)
        spin = state['time'] * 30.0
        for phase, chunk in ((0.0, 'spark'), (math.pi, 'sweat')):
            ca, sa = math.cos(spin + phase), math.sin(spin + phase)
            off = tuple((side[k] * ca + up[k] * sa) * 0.18 for k in range(3))
            bs.emitfx(position=tuple(pos[k] + off[k] for k in range(3)),
                      velocity=tuple(off[k] * 4.0 for k in range(3)),
                      count=1, scale=0.45, spread=0.0, chunk_type=chunk)
        if int(state['time'] / _TICK) % 4 == 0:
            bs.emitfx(position=pos, count=1, emit_type='tendrils',
                      tendril_type='thin_smoke')

    shot._bst_flight = bs.Timer(  # type: ignore[attr-defined]
        _TICK, _step, repeat=True
    )
    # Muzzle: a little ring of sparks around the barrel.
    for i in range(10):
        ang = 2.0 * math.pi * i / 10
        out = tuple(side[k] * math.cos(ang) + up[k] * math.sin(ang)
                    for k in range(3))
        bs.emitfx(position=start,
                  velocity=tuple(out[k] * 5.0 + facing[k] * 2.0
                                 for k in range(3)),
                  count=1, scale=0.5, spread=0.0, chunk_type='spark')
    _flash(start, col, 0.4, 0.6, 1.0, 0.1)
    _snd('laser', 0.6, start)
    _snd('swip2', 0.8, start)
    _snd('cork_pop', 0.6, start)
    _step()  # Point blank: hits whoever is right in front at once.


def _homing_shot_target(spaz: Spaz, origin: Sequence[float],
                        heading: Sequence[float]) -> bs.Node | None:
    """Prefer an enemy in front; fall back to the nearest enemy on the map."""
    candidates = []
    for target in _live_fighters():
        other = target.getdelegate(Spaz)
        if other is None or not _is_enemy(spaz, other):
            continue
        toward, dist = _norm([target.position_center[k] - origin[k]
                              for k in range(3)])
        dot = sum(toward[k] * heading[k] for k in range(3))
        candidates.append((dot < 0.35, dist, -dot, target))
    return min(candidates, default=(True, 0.0, 0.0, None))[-1]


def _shell_victim(a: Sequence[float], b: Sequence[float],
                  owner: bs.Node) -> tuple | None:
    """Where along a-b the shell first meets a fighter (not its shooter)."""
    best_t: float | None = None
    for node in _live_fighters():
        if node == owner:
            continue
        center = node.position_center
        hit_t = _seg_hit_t(a, b, center, SHOT_HIT_RADIUS)
        if hit_t == 0.0 and sum((center[k] - a[k]) * (b[k] - a[k])
                                for k in range(3)) < 0.0:
            continue  # Hugging the shooter from behind: not in the way.
        if hit_t is not None and (best_t is None or hit_t < best_t):
            best_t = hit_t
    if best_t is None:
        return None
    return tuple(a[k] + (b[k] - a[k]) * best_t for k in range(3))


def _kick_mine(spaz: Spaz, mine: Bomb) -> None:
    """Kicked our charged mine before it armed: mine a much bigger area."""
    mine._bst_mine_spread = False  # type: ignore[attr-defined]
    pos = mine.node.position
    mine.node.velocity = (0.0, 3.0, 0.0)  # A little hop.
    bs.emitfx(position=pos, velocity=(0, 4, 0), count=20, scale=0.7,
              spread=0.4, chunk_type='spark')
    _snd('punch_strong01', 1.0, pos)
    _snd('metal_hit', 0.8, pos)
    _spread_mines(mine, big=True)


def _spread_mines(mine: Bomb, big: bool = False) -> None:
    """A charged mine lays an even ring of mines around itself, one by one.
    Kicked (super-charged): once the ring is down, each of its mines tosses
    two more further out, again one by one. Mines that drop off a ledge or
    into the void are scrapped (and a scrapped one tosses nothing)."""
    if not mine.node:
        return
    pos = mine.node.position
    source = mine.get_source_player(bs.Player)
    owner = mine.owner
    base = random.uniform(0.0, 2.0 * math.pi)
    ring = [(base + 2.0 * math.pi * i / MINE_RING, MINE_RING_DIST)
            for i in range(MINE_RING)]
    laid: list[Bomb] = []

    def _children() -> None:
        # Second wave (kicked only), still strictly one at a time.
        num = 0
        for parent in laid:
            if not parent.node:
                continue
            ppos = parent.node.position
            out = math.atan2(ppos[2] - pos[2], ppos[0] - pos[0])
            for j in range(MINE_CHILDREN):
                spread = (j - (MINE_CHILDREN - 1) / 2.0) * 0.6  # ~+-17 deg.
                bs.timer(num * MINE_SEQ_DELAY, bs.CallStrict(
                    _toss_mine, ppos, out + spread, MINE_CHILD_DIST, source,
                    owner, None))
                num += 1

    for i, (ang, dist) in enumerate(ring):
        bs.timer(i * MINE_SEQ_DELAY, bs.CallStrict(
            _toss_mine, pos, ang, dist, source, owner, laid))
    if big:
        # After the whole ring has landed and settled.
        bs.timer(MINE_RING * MINE_SEQ_DELAY + 1.0, _children)
    bs.emitfx(position=pos, velocity=(0, 3, 0), count=12 if not big else 25,
              scale=0.6, spread=0.4, chunk_type='metal')


def _toss_mine(origin: Sequence[float], ang: float, dist: float,
               source: Any, owner: Any, laid: list | None) -> None:
    """Toss one mine to land ~dist away; scrap it if it falls off."""
    flight = 0.55
    speed = dist / flight
    extra = Bomb(
        position=(origin[0], origin[1] + 0.5, origin[2]),
        velocity=(math.cos(ang) * speed, 3.5, math.sin(ang) * speed),
        bomb_type='land_mine',
        source_player=source,
        owner=owner,
    ).autoretain()
    _snd('cork_pop', 0.8, origin)

    def _settle() -> None:
        if not extra.node:
            return
        epos = extra.node.position
        fell = epos[1] < origin[1] - 1.2
        slid = math.hypot(epos[0] - origin[0], epos[2] - origin[2]) > dist + 1.5
        if fell or slid:
            # Off the edge: no place for a mine here.
            bs.emitfx(position=epos, velocity=(0, 1, 0), count=6,
                      scale=0.5, spread=0.2, chunk_type='spark')
            extra.handlemessage(bs.DieMessage())
            return
        extra.arm()
        _snd('bomb_drop01', 0.5, epos)
        if laid is not None:
            laid.append(extra)

    bs.timer(flight + 0.45, _settle)


# ------------------------------- Beads ------------------------------------
# Tentacles are chains of small glowing bubbles: 'shield' nodes, the same
# thing a shield powerup draws. The game itself moves shields around every
# frame, so they can be placed freely and are always visible.

# Falls back to slime particles if beads can't be placed.
_BEADS_OK = [True]


def _bead(pos: Sequence[float], radius: float,
          owner: bs.Node | None = None) -> bs.Node | None:
    if not _BEADS_OK[0]:
        return None
    try:
        return bs.newnode(
            'shield',
            owner=owner,
            attrs={'position': pos, 'radius': radius, 'color': _SLIME},
        )
    except Exception:
        _BEADS_OK[0] = False
        return None


def _place(node: bs.Node | None, pos: Sequence[float]) -> None:
    if node is None or not node or not _BEADS_OK[0]:
        return
    try:
        node.position = pos
    except Exception:
        _BEADS_OK[0] = False


def _draw_tentacle(beads: list, pts: list, slime: bool) -> None:
    """Pose a bead tentacle (or spray slime along it as a fallback)."""
    if _BEADS_OK[0]:
        for bead, pos in zip(beads, pts):
            _place(bead, pos)
    elif slime:
        for pos in pts:
            bs.emitfx(position=pos, velocity=(0, 0, 0), count=1, scale=0.35,
                      spread=0.0, chunk_type='slime')


def _tentacle_beads(base: Sequence[float], segments: int, thick: float,
                    thin: float, owner: bs.Node | None) -> list:
    """Thick at the root, thin at the tip."""
    return [_bead(base, thick + (thin - thick) * i / max(segments - 1, 1),
                  owner=owner) for i in range(segments)]


def _delete_all(nodes: list) -> None:
    for node in nodes:
        if node:
            node.delete()


def _tentacle_curve(base: Sequence[float], tip: Sequence[float],
                    phase: float, amp: float, segments: int) -> list[tuple]:
    """Points along a wriggling tentacle from base to tip."""
    vec = [b - a for a, b in zip(base, tip)]
    side, slen = _norm((-vec[2], 0.0, vec[0]))
    if slen < 1e-4:
        side = (1.0, 0.0, 0.0)
    pts = []
    for i in range(segments):
        frac = (i + 1) / segments
        bend = math.sin(frac * math.pi)  # Pinned at both ends.
        wave = math.sin(phase + frac * 5.0) * amp * bend
        lift = math.cos(phase * 0.7 + frac * 4.0) * amp * 0.5 * bend
        pts.append(tuple(base[k] + vec[k] * frac + side[k] * wave
                         + (lift if k == 1 else 0.0) for k in range(3)))
    return pts


# -------------------------- Sticky bomb + charge --------------------------

_TENTACLES = 3
_SEGMENTS = 6


def _tentacle_targets(spaz: Spaz, origin: Sequence[float]) -> list:
    """All living enemies within tentacle reach."""
    found = []
    for node in bs.getnodes():
        if not node or node.getnodetype() != 'spaz':
            continue
        other = node.getdelegate(Spaz)
        if other is None or not other.is_alive() or not _is_enemy(spaz, other):
            continue
        _, dist = _norm([a - b for a, b in zip(node.position_center, origin)])
        if dist <= TENTACLE_RANGE + 0.5:  # Reach to their body, not middle.
            found.append(node)
    return found


def _stop_tentacle(bomb: Bomb) -> None:
    bomb._bst_tentacle_timer = None  # type: ignore[attr-defined]
    for tent in getattr(bomb, '_bst_tentacles', []):
        _delete_all(tent)
    bomb._bst_tentacles = []  # type: ignore[attr-defined]


def _pose_tentacles(bomb: Bomb, bnode: bs.Node, bpos: Sequence[float],
                    victims: list, grabbed: dict, tnow: float) -> None:
    """Every tentacle holds a victim (spare ones double up), or they all
    feel around while nobody is caught."""
    tentacles = bomb._bst_tentacles
    while len(tentacles) < len(victims):  # One tentacle per victim.
        tentacles.append(
            _tentacle_beads(bnode.position, _SEGMENTS, 0.17, 0.07, bnode)
        )
    for k, tent in enumerate(tentacles):
        ang = tnow * 1.5 + k * 2.0 * math.pi / max(len(tentacles), 1)
        if victims:
            node = victims[k % len(victims)]
            reeled = grabbed[node]
            tpos = node.position_center
            wrap = 0.35 if reeled else 0.25
            tip = (tpos[0] + math.cos(ang * 2.0) * wrap,
                   tpos[1] + 0.25 * math.sin(ang * 3.0),
                   tpos[2] + math.sin(ang * 2.0) * wrap)
            amp = 0.18 if reeled else 0.3
        else:
            tip = (bpos[0] + math.cos(ang) * 0.7,
                   bpos[1] + 0.55 + 0.2 * math.sin(tnow * 3.0 + k),
                   bpos[2] + math.sin(ang) * 0.7)
            amp = 0.15
        pts = _tentacle_curve(bpos, tip, tnow * 10.0 + k * 2.0, amp,
                              _SEGMENTS)
        _draw_tentacle(tent, pts,
                       bool(victims) and int(tnow / _TICK) % 2 == 0)


def _start_tentacle(bomb: Bomb) -> None:
    """Thrown charged sticky bomb: writhing tentacles that grab every enemy
    in reach and reel them in."""
    bnode = bomb.node
    if not bnode or getattr(bomb, '_exploded', False):
        return
    _stop_tentacle(bomb)
    start = bnode.position

    try:
        bomb._bst_tentacles = [  # type: ignore[attr-defined]
            _tentacle_beads(start, _SEGMENTS, 0.17, 0.07, bnode)
            for _ in range(_TENTACLES)
        ]
    except Exception:
        _BEADS_OK[0] = False
        bomb._bst_tentacles = []  # type: ignore[attr-defined]
    # Grabbed enemies, in order of capture: node -> reeled in yet?
    grabbed: dict = {}
    state = {'time': 0.0}
    _snd('sticky_impact', 0.6, start)

    def _step() -> None:
        state['time'] += _TICK
        tnow = state['time']
        spaz = bomb._bst_tentacle_owner()
        if spaz is None or not bnode or getattr(bomb, '_exploded', False):
            _stop_tentacle(bomb)
            return
        bpos = bnode.position

        # Let go of the dead; grab everyone (new) in reach.
        for node in list(grabbed):
            victim = node.getdelegate(Spaz) if node else None
            if victim is None or not victim.is_alive():
                del grabbed[node]
        for node in _tentacle_targets(spaz, bpos):
            if node not in grabbed:
                grabbed[node] = False
                _snd('sticky_impact', 1.0, bpos)
                _snd('splatter', 0.8, node.position)
                _snd('swip', 0.8, bpos)
                bs.emitfx(position=node.position_center, velocity=(0, 2, 0),
                          count=12, scale=0.6, spread=0.3,
                          chunk_type='slime')
        victims = list(grabbed)

        # Bomb and victims pull on each other (before any visuals, so a
        # drawing hiccup can never stop it). Equal and opposite impulses:
        # the physics divides by mass, so the light bomb moves the most.
        for node in victims:
            if grabbed[node]:
                continue
            tpos = node.position_center
            pull, dist = _norm([a - b for a, b in zip(bpos, tpos)])
            if dist < 0.9:
                grabbed[node] = True  # Got them: hold on until it blows.
                _snd('sticky_impact', 1.0, bpos)
                continue
            node.handlemessage(
                'impulse', tpos[0], tpos[1], tpos[2], 0.0, 0.0, 0.0,
                TENTACLE_PULL, TENTACLE_PULL * 0.08, 0.0, 0,
                pull[0], pull[1] + 0.3, pull[2],
            )
            bnode.handlemessage(
                'impulse', bpos[0], bpos[1], bpos[2], 0.0, 0.0, 0.0,
                TENTACLE_PULL, TENTACLE_PULL * 0.08, 0.0, 0,
                -pull[0], -pull[1] + 0.1, -pull[2],
            )

        try:
            _pose_tentacles(bomb, bnode, bpos, victims, grabbed, tnow)
        except Exception:
            _BEADS_OK[0] = False  # Fall back to slime particles.

    bomb._bst_tentacle_timer = bs.Timer(  # type: ignore[attr-defined]
        _TICK, _step, repeat=True
    )


# ---------------------------- Tentacle whip -------------------------------

_WHIP_SEGMENTS = 12


def _update_counter(spaz: Spaz) -> None:
    """Whips, then shells, show in the counter over the head (mines once out
    of both) - in the order the bomb button uses them."""
    node = spaz.node
    if not node:
        return
    if spaz._bst_whips > 0:
        node.counter_text = f'x{spaz._bst_whips}'
        node.counter_texture = _classicassets.textures.powerup_sticky_bombs.get()
    elif spaz._bst_ice_orbs > 0:
        node.counter_text = f'x{spaz._bst_ice_orbs}'
        node.counter_texture = _classicassets.textures.powerup_ice_bombs.get()
    elif spaz._bst_shots > 0:
        node.counter_text = f'x{spaz._bst_shots}'
        node.counter_texture = _classicassets.textures.powerup_bomb.get()
    else:
        _orig_set_land_mine_count(spaz, spaz.land_mine_count)


def _wrap_into_whip(spaz: Spaz, bomb: Bomb) -> None:
    """Charged punch on our sticky bomb: it turns into a tentacle whip."""
    charge = _bomb_charge(bomb) or Spaz.bsm_take_charge(spaz)
    bpos = bomb.node.position
    bomb.handlemessage(bs.DieMessage())  # Consumed, never goes off.
    spaz._bst_whips = min(WHIP_MAX, spaz._bst_whips + WHIP_PER_BOMB)
    spaz._bst_whip_charge += charge
    _update_counter(spaz)

    bs.emitfx(position=bpos, velocity=(0, 3, 0), count=20, scale=0.7,
              spread=0.4, chunk_type='slime')
    _flash(bpos, _SLIME, 0.8, 1.2, 1.5, 0.25)
    _snd('sticky_impact', 1.0, bpos)
    _snd('splatter', 0.8, bpos)
    _snd('powerup01', 0.7, bpos)
    _popup_text('ЩУПАЛЬЦЕ!', spaz.node.position, _SLIME)


# Tentacles out right now; each one's victim is taken (see _whip_target).
_WHIPS: list[dict] = []


def _whip_taken(node: bs.Node, mine: dict | None = None) -> bool:
    """Another tentacle is already after (or holding) them."""
    _WHIPS[:] = [whip for whip in _WHIPS if whip.get('claim')]  # Gone ones.
    return any(whip is not mine and whip.get('claim') == node
               for whip in _WHIPS)


def _whip_target(spaz: Spaz, facing: Sequence[float]) -> bs.Node | None:
    """Who the tentacle goes for: the closest enemy in front (horizontal
    cone, any height) nobody else's tentacle has; if all in front are
    taken, the free one nearest to where you look anywhere on the map;
    only if every enemy is taken, the one in front anyway."""
    facing, _ = _norm((facing[0], 0.0, facing[2]))
    origin = spaz.node.position_center
    min_cos = math.cos(math.radians(WHIP_ANGLE))
    cone: list = []
    free: list = []
    for node in bs.getnodes():
        if not node or node.getnodetype() != 'spaz':
            continue
        other = node.getdelegate(Spaz)
        if other is None or not other.is_alive() or not _is_enemy(spaz, other):
            continue
        tpos = node.position_center
        _, dist = _norm([a - b for a, b in zip(tpos, origin)])
        flat, flen = _norm((tpos[0] - origin[0], 0.0, tpos[2] - origin[2]))
        if dist > WHIP_RANGE or flen < 0.01:
            continue
        cos = flat[0] * facing[0] + flat[2] * facing[2]
        taken = _whip_taken(node)
        if cos >= min_cos:
            cone.append((dist / cos, taken, node))
        if not taken:
            # Off to the side counts for more than far away.
            free.append((dist * (2.0 - cos), node))
    for score, taken, node in sorted(cone, key=lambda c: c[0]):
        if not taken:
            return node
    if free:
        return min(free, key=lambda f: f[0])[1]
    return min(cone, key=lambda c: c[0])[2] if cone else None


def _ground_under(pos: Sequence[float]) -> tuple:
    """Just above the floor under a fighter (no ray casts in the game API;
    erring high keeps the tentacle visible instead of inside the floor)."""
    return (pos[0], pos[1] - 0.35, pos[2])


def _whip_curve(base: Sequence[float], tip: Sequence[float], phase: float,
                amp: float, segments: int) -> list[tuple]:
    """A tentacle standing up out of the ground: bulges upward, wriggles."""
    top = max(base[1], tip[1]) + 0.8
    ctrl = (base[0], top, base[2])
    side, slen = _norm((tip[2] - base[2], 0.0, base[0] - tip[0]))
    if slen < 1e-4:
        side = (1.0, 0.0, 0.0)
    pts = []
    for i in range(segments):
        t = (i + 1) / segments
        # Quadratic bezier: base -> (above base) -> tip.
        p = [(1 - t) ** 2 * base[k] + 2 * (1 - t) * t * ctrl[k]
             + t * t * tip[k] for k in range(3)]
        wave = math.sin(phase + t * 6.0) * amp * math.sin(t * math.pi)
        pts.append((p[0] + side[0] * wave, p[1], p[2] + side[2] * wave))
    return pts


_WHIP_BODY = 14  # Beads in the crawling body.
_WHIP_GAP = 0.3  # Spacing between them along the trail (meters).


def _fire_whip(spaz: Spaz) -> None:
    """The bomb button: a tentacle slithers out at your feet and crawls along
    the ground toward the enemy you're looking at (narrow cone, anywhere on
    the map). Whoever it reaches - its target or anyone in the way - it rears
    up under, wraps and slaps four mini sticky bombs on."""
    node = spaz.node
    spaz._bst_whips -= 1
    charge, spaz._bst_whip_charge = spaz._bst_whip_charge, 0.0
    _update_counter(spaz)
    spaz._bst_whip_active = True  # (Any number can be out at once.)

    facing = _look_dir(spaz)
    target = _whip_target(spaz, facing)
    here = node.position
    start = _ground_under((here[0] + facing[0] * 0.8, here[1],
                           here[2] + facing[2] * 0.8))
    straight_end = (start[0] + facing[0] * 8.0, start[1],
                    start[2] + facing[2] * 8.0)
    beads = _tentacle_beads(start, max(_WHIP_BODY, _WHIP_SEGMENTS), 0.45,
                            0.18, None)
    # Just a small glowing dot on its head.
    head_light = bs.newnode('light', attrs={
        'position': start, 'color': _SLIME, 'radius': 0.06,
        'intensity': 0.8, 'height_attenuated': False,
        'volume_intensity_scale': 0.0})
    source = spaz.source_player
    glide = _glider(head_light, start)
    state: dict[str, Any] = {'time': 0.0, 'phase': 'crawl', 'victim': None,
                             'minis': [], 'head': start, 'trail': [start],
                             'crawled': 0.0, 'base': start, 'claim': target}
    _WHIPS.append(state)

    bs.emitfx(position=start, velocity=(0, 4, 0), count=10, scale=0.7,
              spread=0.3, chunk_type='rock')
    bs.emitfx(position=start, count=1, emit_type='tendrils',
              tendril_type='smoke')
    _snd('splatter', 0.8, start)
    _snd('swip2', 0.8, node.position)

    def _finish() -> None:
        if state in _WHIPS:
            _WHIPS.remove(state)
        timers = spaz._bst_whip_timers
        if state.get('timer') in timers:
            timers.remove(state['timer'])
        state['timer'] = None
        spaz._bst_whip_active = bool(timers)
        _delete_all(beads)
        if head_light:
            head_light.delete()

    def _slime_body(pts: list) -> None:
        """Slime all along the body: visible even if the beads aren't."""
        for pos in pts[::2]:
            bs.emitfx(position=pos, velocity=(0.0, 0.6, 0.0), count=1,
                      scale=0.55, spread=0.04, chunk_type='slime')

    def _dodged(victim_node: bs.Node) -> str | None:
        """Jumping over it or parrying it beats the tentacle."""
        victim = victim_node.getdelegate(Spaz)
        if victim is None:
            return None
        if getattr(victim, '_ab_active', False):
            return 'parry'
        since_jump = bs.time() * 1000.0 - getattr(victim, 'last_jump_time_ms',
                                                  -9999)
        if since_jump < 700 or victim_node.velocity[1] > 2.0:
            return 'jump'
        return None

    def _latch(victim_node: bs.Node) -> None:
        dodge = _dodged(victim_node)
        if dodge is not None:
            # Grabs air (or bounces off the shield) and sinks back.
            vpos = victim_node.position_center
            if dodge == 'parry':
                _snd('block', 1.0, vpos)
                _snd('shield_hit', 0.8, vpos)
            else:
                _snd('swip', 0.8, vpos)
            bs.emitfx(position=vpos, velocity=(0, 2, 0), count=8, scale=0.5,
                      spread=0.3, chunk_type='slime')
            state['phase'] = 'flail'
            state['flail_until'] = state['time'] + 0.4
            return
        state['phase'] = 'hold'
        state['victim'] = victim_node
        state['claim'] = victim_node
        state['hold_until'] = state['time'] + WHIP_FUSE + 0.45
        vpos = victim_node.position_center
        bs.emitfx(position=vpos, velocity=(0, 3, 0), count=20, scale=0.7,
                  spread=0.4, chunk_type='slime')
        _snd('splatter', 1.0, vpos)
        _snd('sticky_impact', 1.0, vpos)
        _snd('cork_pop', 1.0, vpos)
        # Four mini sticky bombs slapped onto them; they ride along on the
        # victim until they go off.
        blast = 1.2 + min(1.0, charge / 1000.0)  # Charge widens them.
        for i in range(4):
            ang = i * math.pi / 2 + math.pi / 4
            off = (math.cos(ang) * 0.35, 0.15 * (1 if i % 2 else -1),
                   math.sin(ang) * 0.35)
            mini = Bomb(
                position=tuple(vpos[k] + off[k] for k in range(3)),
                velocity=(0.0, 0.0, 0.0),
                bomb_type='sticky',
                blast_radius=blast,
                bomb_scale=0.5,
                source_player=source,
                owner=node,
            ).autoretain()
            state['minis'].append((mini, off))
            bs.timer(WHIP_FUSE + 0.1 * i,
                     bs.WeakCallStrict(mini.handlemessage, ExplodeMessage()))

    def _rear_up(victim: bs.Node | None) -> None:
        state['phase'] = 'rise'
        state['rise_at'] = state['time']
        state['base'] = state['head']
        state['rise_victim'] = victim
        bs.emitfx(position=state['head'], velocity=(0, 6, 0), count=12,
                  scale=0.8, spread=0.4, chunk_type='rock')
        _snd('impact_hard', 0.9, state['head'])

    def _body_along_trail() -> list[tuple]:
        """Beads laid back along the path the head took, wriggling."""
        trail = state['trail']
        pts = []
        idx = len(trail) - 1
        carry = 0.0
        prev = trail[idx]
        tnow = state['time']
        for i in range(len(beads)):
            want = i * _WHIP_GAP
            while idx > 0 and carry < want:
                seg = math.dist(trail[idx], trail[idx - 1])
                if carry + seg >= want:
                    frac = (want - carry) / max(seg, 1e-6)
                    prev = tuple(trail[idx][k] + (trail[idx - 1][k]
                                 - trail[idx][k]) * frac for k in range(3))
                    break
                carry += seg
                idx -= 1
                prev = trail[idx]
            # Side-to-side slither and a hump off the ground.
            wave = math.sin(tnow * 10.0 - i * 0.7) * 0.18
            pts.append((prev[0] + facing[2] * wave, prev[1] + 0.15
                        + 0.08 * abs(math.sin(tnow * 8.0 - i * 0.5)),
                        prev[2] - facing[0] * wave))
        return pts

    def _step() -> None:
        state['time'] += _TICK
        tnow = state['time']
        phase = state['phase']
        if phase == 'crawl':
            victim = target.getdelegate(Spaz) if target else None
            homing = victim is not None and victim.is_alive()
            goal = (_ground_under(target.position) if homing
                    else straight_end)
            move, dist = _norm([a - b for a, b in zip(goal, state['head'])])
            step = WHIP_CRAWL_SPEED * _TICK
            head = goal if dist <= step else tuple(
                state['head'][k] + move[k] * step for k in range(3))
            state['crawled'] += min(step, dist)
            state['head'] = head
            state['trail'].append(head)
            if len(state['trail']) > 200:
                state['trail'] = state['trail'][-200:]
            # Grab whoever it reaches first (its target or anyone en route
            # no other tentacle has).
            for vnode in _tentacle_targets(spaz, head):
                if vnode != target and _whip_taken(vnode, state):
                    continue
                if math.hypot(vnode.position[0] - head[0],
                              vnode.position[2] - head[2]) < 1.0:
                    _rear_up(vnode)
                    break
            else:
                if (not homing and dist <= step) or tnow > WHIP_CRAWL_TIME:
                    _rear_up(None)
            if state['phase'] == 'crawl':
                try:
                    body = _body_along_trail()
                    _draw_tentacle(beads, body, False)
                    _glide_to(glide, head)
                    if int(tnow / _TICK) % 2 == 0:
                        _slime_body(body)
                except Exception:
                    _BEADS_OK[0] = False
                if int(tnow / _TICK) % 3 == 0:
                    bs.emitfx(position=head, velocity=(0, 1, 0), count=3,
                              scale=0.6, spread=0.15, chunk_type='slime')
                    _snd('sticky_impact', 0.2, head)
                return
            phase = state['phase']
        base = state['base']
        if phase == 'rise':
            grow = min(1.0, (tnow - state['rise_at']) / 0.25)
            victim = state.get('rise_victim')
            goal = (victim.position_center if victim
                    else (base[0], base[1] + WHIP_HEIGHT, base[2]))
            tip = tuple(base[k] + (goal[k] - base[k]) * grow
                        for k in range(3))
            if grow >= 1.0:
                alive = victim.getdelegate(Spaz) if victim else None
                if alive is not None and alive.is_alive():
                    _latch(victim)
                else:
                    state['phase'] = 'flail'
                    state['flail_until'] = tnow + 0.6
        elif phase == 'hold':
            vnode = state['victim']
            vpos = vnode.position_center if vnode else (
                base[0], base[1] + WHIP_HEIGHT * 0.6, base[2])
            tip = (vpos[0] + 0.25 * math.cos(tnow * 8.0), vpos[1] + 0.2,
                   vpos[2] + 0.25 * math.sin(tnow * 8.0))
            for mini, off in state['minis']:
                if mini.node and vnode:
                    goal = tuple(vpos[k] + off[k] for k in range(3))
                    mini.node.velocity = tuple(
                        (g - p) * 15.0 for g, p in zip(goal, mini.node.position))
            if tnow >= state['hold_until'] or not vnode:
                state['phase'] = 'sink'
                state['sink_from'] = tip
                state['sink_at'] = tnow
                _snd('swip', 0.8, base)
        elif phase == 'flail':
            tip = (base[0] + 0.8 * math.cos(tnow * 6.0),
                   base[1] + WHIP_HEIGHT * (0.8 + 0.1 * math.sin(tnow * 9)),
                   base[2] + 0.8 * math.sin(tnow * 6.0))
            if tnow >= state['flail_until']:
                state['phase'] = 'sink'
                state['sink_from'] = tip
                state['sink_at'] = tnow
        else:  # Sinking back into the ground.
            frac = min(1.0, (tnow - state['sink_at']) / 0.3)
            src = state['sink_from']
            tip = tuple(src[k] + (base[k] - src[k]) * frac for k in range(3))
            if frac >= 1.0:
                _finish()
                return
        amp = 0.35 if state['phase'] in ('rise', 'flail') else 0.15
        try:
            pts = _whip_curve(base, tip, tnow * 12.0, amp, len(beads))
            _draw_tentacle(beads, pts, False)
            _glide_to(glide, tip)
            if int(tnow / _TICK) % 2 == 0:  # Always visible, even w/o beads.
                _slime_body(pts)
        except Exception:
            _BEADS_OK[0] = False  # Visuals must never stop the whip.

    # Each tentacle has its own timer, kept on the fighter.
    state['timer'] = bs.Timer(_TICK, _wcall(lambda s: _step(), spaz),
                              repeat=True)
    spaz._bst_whip_timers.append(state['timer'])
    _step()


def _glider(node: bs.Node, start: Sequence[float]) -> dict:
    """Moves a node's position smoothly between our 30 ms ticks: the engine
    interpolates along curves we only re-aim each tick (no new nodes)."""
    glide: dict[str, Any] = {'node': node, 'last': tuple(start),
                             'curves': None}
    try:
        gnode = bs.getactivity().globalsnode
        combine = bs.newnode('combine', owner=node, attrs={'size': 3})
        curves = []
        for i in range(3):
            curve = bs.newnode('animcurve', owner=node, name='Driving')
            gnode.connectattr('time', curve, 'in')
            curve.times = [0]
            curve.values = [start[i]]
            curve.connectattr('out', combine, f'input{i}')
            curves.append(curve)
        combine.connectattr('output', node, 'position')
        glide['curves'] = curves
    except Exception:
        glide['curves'] = None  # Then it just jumps tick to tick.
    return glide


def _glide_to(glide: dict, pos: Sequence[float]) -> None:
    node = glide['node']
    if not node:
        return
    curves = glide['curves']
    if curves is None:
        node.position = tuple(pos)
        return
    now = int(bs.time() * 1000.0)
    step = int(_TICK * 1000.0)
    for i, curve in enumerate(curves):
        curve.times = [0, step]
        curve.values = [glide['last'][i], pos[i]]
        curve.offset = now
    glide['last'] = tuple(pos)


# ---------------------------- Nuclear suicide -----------------------------

_QTE_KEYS = {
    'jump': ('button_jump', 'ПРЫЖОК', (0.3, 1.0, 0.3)),
    'punch': ('button_punch', 'УДАР', (1.0, 0.85, 0.2)),
    'bomb': ('button_bomb', 'БОМБА', (1.0, 0.3, 0.25)),
    'pickup': ('button_pick_up', 'СХВАТИТЬ', (0.35, 0.6, 1.0)),
}


def _screen_text(text: str, pos: tuple, color: Sequence[float],
                 scale: float) -> bs.Node:
    return bs.newnode(
        'text',
        attrs={
            'text': text,
            'position': pos,
            'h_attach': 'center',
            'v_attach': 'center',
            'h_align': 'center',
            'v_align': 'center',
            'color': (color[0], color[1], color[2], 1.0),
            'scale': scale,
            'shadow': 1.0,
            'flatness': 1.0,
        },
    )


def _start_nuke_qte(spaz: Spaz) -> None:
    """The cursed one parried their own curse: a QTE decides the nuke."""
    node = spaz.node
    node.invincible = True  # Nothing may set the curse off mid-QTE.
    spaz._curse_timer = None  # pylint: disable=protected-access
    node.curse_death_time = 0
    keys = [random.choice(list(_QTE_KEYS)) for _ in range(NUKE_QTE_KEYS)]
    qte: dict[str, Any] = {'keys': keys, 'idx': 0, 'nodes': [],
                           'time': 0.0, 'done': False}
    spaz._bst_qte = qte

    head = _screen_text('СПАРИРОВАЛ ПРОКЛЯТИЕ! ЖМИ!', (0, 170),
                        (1.0, 0.35, 0.25), 1.4)
    timer_text = _screen_text('', (0, 125), (1.0, 1.0, 1.0), 1.1)
    qte['fixed'] = [head, timer_text]
    _seq(node.position, (0, 'alarm', 0.7), (0, 'orchestra_hit3', 0.8),
         (0.05, 'shield_hit', 0.8))
    _show_qte_key(spaz)

    def _tick() -> None:
        if qte['done']:
            return
        qte['time'] += 0.05
        left = NUKE_QTE_TIME - qte['time']
        timer_text.text = f'{max(0.0, left):.1f}'
        if left <= 0:
            _qte_finish(spaz, success=False)

    qte['timer'] = bs.Timer(0.05, _wcall(lambda s: _tick(), spaz),
                            repeat=True)


def _show_qte_key(spaz: Spaz) -> None:
    qte = spaz._bst_qte
    for old in qte['nodes']:
        if old:
            old.delete()
    key = qte['keys'][qte['idx']]
    tex_name, label, color = _QTE_KEYS[key]
    # A big glow in the button's color behind it: readable at a glance.
    glow = bs.newnode(
        'image',
        attrs={
            'texture': _classicassets.textures.light_soft.get(),
            'position': (0, 0),
            'scale': (10, 10),
            'attach': 'center',
            'absolute_scale': True,
            'color': color,
        },
    )
    bs.animate_array(glow, 'scale', 2,
                     {0: (10, 10), 0.1: (520, 520), 0.18: (440, 440)})
    img = bs.newnode(
        'image',
        attrs={
            'texture': getattr(_classicassets.textures, tex_name).get(),
            'position': (0, 0),
            'scale': (10, 10),
            'attach': 'center',
            'absolute_scale': True,
            'color': tuple(0.5 + 0.5 * c for c in color),  # Tinted.
        },
    )
    bs.animate_array(img, 'scale', 2,
                     {0: (10, 10), 0.08: (230, 230), 0.14: (190, 190)})
    text = _screen_text(label, (0, -130), color, 1.6)
    step = _screen_text(f'{qte["idx"] + 1} / {NUKE_QTE_KEYS}', (0, -175),
                        (0.8, 0.8, 0.8), 0.9)
    qte['nodes'] = [glow, img, text, step]
    _snd('race_beep1', 0.8)


def _qte_input(spaz: Spaz, key: str) -> None:
    qte = spaz._bst_qte
    if qte is None or qte['done']:
        return
    if key != qte['keys'][qte['idx']]:
        _qte_finish(spaz, success=False)
        return
    qte['idx'] += 1
    _snd('ding_small_high', 0.9)
    if qte['idx'] >= NUKE_QTE_KEYS:
        _qte_finish(spaz, success=True)
    else:
        _show_qte_key(spaz)


def _qte_finish(spaz: Spaz, success: bool) -> None:
    qte = spaz._bst_qte
    if qte is None or qte['done']:
        return
    qte['done'] = True
    qte['timer'] = None
    for old in qte['nodes'] + qte['fixed']:
        if old:
            old.delete()
    node = spaz.node
    if not success:
        spaz._bst_qte = None
        _snd('boo', 0.6)
        if node:
            node.invincible = False
            _orig_curse_explode(spaz)
        return
    _snd('race_beep2', 1.0)
    _start_nuke(spaz)


def _start_nuke(spaz: Spaz) -> None:
    """Alarm and countdown; slow-mo and a close-up for the last second."""
    node = spaz.node
    activity = bs.getactivity()
    gnode = activity.globalsnode
    saved = {
        'tint': tuple(gnode.tint),
        'slow': gnode.slow_motion,
        'aoi': tuple(gnode.area_of_interest_bounds),
        'focus': {},
    }
    text = _screen_text('ЯДЕРНЫЙ ЗАРЯД', (0, 150), (1.0, 0.25, 0.15), 1.8)
    count = _screen_text(f'{NUKE_COUNTDOWN:.1f}', (0, 80), (1.0, 1.0, 1.0),
                         2.2)
    light = bs.newnode(
        'light',
        owner=node,
        attrs={'color': (1.0, 0.15, 0.05), 'radius': 0.3,
               'height_attenuated': False, 'volume_intensity_scale': 0.6},
    )
    node.connectattr('position_center', light, 'position')
    bs.animate(light, 'intensity', {0: 0.5, 0.25: 2.0, 0.5: 0.5}, loop=True)
    bs.animate(light, 'radius', {0: 0.3, NUKE_COUNTDOWN: 1.4})
    _seq(node.position, (0, 'alarm', 1.0), (0, 'announce_three', 1.0),
         (NUKE_COUNTDOWN - 2.0, 'announce_two', 1.0),
         (NUKE_COUNTDOWN - 1.0, 'announce_one', 1.0),
         (NUKE_COUNTDOWN - 1.0, 'laser', 0.8))
    state = {'time': 0.0}

    def _tick() -> None:
        state['time'] += 0.05
        tnow = state['time']
        if not node or not spaz.is_alive():
            # They died before it went off: put the world back.
            holder.clear()
            _restore_world(gnode, saved)
            gnode.tint = saved['tint']
            text.delete()
            count.delete()
            spaz._bst_qte = None
            return
        # Exact time to the blast (game time, so slow-mo slows it too).
        count.text = f'{max(0.0, NUKE_COUNTDOWN - tnow):.1f}'
        # The world goes red as it builds.
        red = min(1.0, tnow / NUKE_COUNTDOWN)
        orig = saved['tint']
        gnode.tint = (orig[0] * (1.0 + 0.5 * red), orig[1] * (1.0 - 0.45 * red),
                      orig[2] * (1.0 - 0.55 * red))
        # Energy sucked into them from all around.
        pos = node.position_center
        ang = tnow * 9.0
        out = (math.cos(ang) * 2.0, 0.6 * math.sin(ang * 1.7),
               math.sin(ang) * 2.0)
        bs.emitfx(position=tuple(pos[k] + out[k] for k in range(3)),
                  velocity=tuple(-out[k] * 3.0 for k in range(3)),
                  count=3, scale=0.7, spread=0.05, chunk_type='spark')
        if int(tnow * 20) % 5 == 0:
            _snd('tick', 0.7, pos)
        if tnow >= NUKE_COUNTDOWN - NUKE_SLOWMO and not saved.get('zoomed'):
            saved['zoomed'] = True
            _nuke_close_up(gnode, node, saved)
        if tnow >= NUKE_COUNTDOWN:
            holder.clear()
            text.delete()
            count.delete()
            _detonate(spaz, gnode, saved)

    holder = [bs.Timer(0.05, _tick, repeat=True)]
    _NUKE_TIMERS.append(holder)


# Running nuke countdowns (nothing else in the game holds on to them).
_NUKE_TIMERS: list[list] = []


def _nuke_close_up(gnode: bs.Node, node: bs.Node, saved: dict) -> None:
    """The very last moment: slow motion and the camera closing in."""
    try:
        _slowmo_on(gnode)
        saved['slow_held'] = True
    except Exception:
        pass
    try:
        pos = node.position
        gnode.area_of_interest_bounds = (pos[0] - 2.5, pos[1] - 1.5,
                                         pos[2] - 2.5, pos[0] + 2.5,
                                         pos[1] + 2.5, pos[2] + 2.5)
        for other in bs.getnodes():
            if other and other != node and other.getnodetype() == 'spaz':
                saved['focus'][other] = other.is_area_of_interest
                other.is_area_of_interest = False
    except Exception:
        pass
    bs.emitfx(position=node.position_center, emit_type='distortion',
              spread=2.0)
    _seq(node.position, (0, 'orchestra_hit_big2', 0.8), (0, 'hiss', 0.8))


def _restore_world(gnode: bs.Node, saved: dict) -> None:
    if saved.pop('slow_held', False):
        _slowmo_off(gnode)
    try:
        gnode.area_of_interest_bounds = saved['aoi']
        for other, val in saved['focus'].items():
            if other:
                other.is_area_of_interest = val
    except Exception:
        pass


def _detonate(spaz: Spaz, gnode: bs.Node, saved: dict) -> None:
    """The nuke: blinding flash, a mushroom cloud, fire across the map, and
    everyone on it gone (unless they parry the blast)."""
    node = spaz.node
    _restore_world(gnode, saved)
    if not node:
        gnode.tint = saved['tint']
        return
    center = node.position
    source = spaz.source_player
    bounds = saved['aoi']

    # Blinding flash fading back to the normal light.
    orig = saved['tint']
    flash = (orig[0] * 3.0, orig[1] * 2.6, orig[2] * 2.2)
    steps = 20
    for i in range(steps + 1):
        frac = i / steps
        tint = tuple(f + (o - f) * frac for f, o in zip(flash, orig))
        bs.timer(0.1 * i, bs.CallStrict(setattr, gnode, 'tint', tint))

    # Fireball, then fire rolling out across the whole map.
    core = bs.newnode('explosion', attrs={'position': center, 'radius': 6.0,
                                         'big': True})
    bs.timer(2.0, core.delete)
    for i in range(14):
        epos = (random.uniform(bounds[0], bounds[3]),
                center[1] + random.uniform(-0.5, 1.5),
                random.uniform(bounds[2], bounds[5]))
        delay = 0.08 + 0.04 * i
        bs.timer(delay, bs.CallStrict(_nuke_fire, epos))
    # Mushroom cloud: a rising column with a cap.
    for i in range(12):
        bs.timer(0.05 * i, bs.CallStrict(
            bs.emitfx, position=(center[0], center[1] + 0.8 * i, center[2]),
            count=3, emit_type='tendrils', tendril_type='smoke'))
    for i in range(10):
        ang = 2.0 * math.pi * i / 10
        bs.timer(0.6, bs.CallStrict(
            bs.emitfx, position=(center[0] + math.cos(ang) * 2.5,
                                 center[1] + 9.0,
                                 center[2] + math.sin(ang) * 2.5),
            count=2, emit_type='tendrils', tendril_type='smoke'))
    # Shock ring rolling over the ground, debris everywhere.
    for delay, opacity in ((0.0, 0.8), (0.12, 0.5)):
        ring = bs.newnode(
            'locator',
            attrs={'shape': 'circleOutline', 'position': center,
                   'color': (1.0, 0.6, 0.3), 'opacity': 0.0,
                   'draw_beauty': False, 'additive': True},
        )
        bs.animate_array(ring, 'size', 1,
                         {0: [0.5], delay: [0.5], delay + 1.2: [60.0]})
        bs.animate(ring, 'opacity', {0: 0.0, delay: opacity,
                                     delay + 1.2: 0.0})
        bs.timer(delay + 1.3, ring.delete)
    bs.emitfx(position=center, emit_type='distortion', spread=12.0)
    for chunk, count in (('spark', 150), ('rock', 40), ('metal', 30)):
        bs.emitfx(position=center, velocity=(0, 12, 0), count=count,
                  scale=1.2, spread=4.0, chunk_type=chunk)
    scorch = bs.newnode('scorch', attrs={'position': center, 'size': 5.0,
                                         'big': True})
    bs.animate(scorch, 'presence', {6.0: 1.0, 20.0: 0.0})
    bs.timer(20.0, scorch.delete)
    bs.camerashake(10.0)
    _seq(center, (0, 'explosion01', 1.0), (0, 'explosion03', 1.0),
         (0, 'big_impact', 1.0), (0, 'orchestra_hit_big1', 1.0),
         (0.06, 'explosion05', 1.0), (0.1, 'big_impact2', 1.0),
         (0.15, 'explosion02', 1.0), (0.2, 'orchestra_hit_big2', 0.9),
         (0.25, 'cymbal', 0.8), (0.3, 'gong', 1.0), (0.4, 'explosion04', 0.9),
         (0.6, 'debris_fall', 1.0), (0.9, 'wood_debris_fall', 0.9),
         (1.2, 'gong', 0.6))

    # Everyone on the map is swept away by the wave as it reaches them.
    for other in bs.getnodes():
        if not other or other.getnodetype() not in ('spaz', 'prop', 'bomb'):
            continue
        opos = other.position
        away, dist = _norm([a - b for a, b in zip(opos, center)])
        if dist < 0.01:
            away = (0.0, 1.0, 0.0)
        delay = min(1.0, dist / 30.0)
        bs.timer(delay, bs.CallStrict(_nuke_hit, other, center, away,
                                      source))
    # The bomber goes with it.
    node.invincible = False
    spaz._bst_qte = None
    spaz._cursed = False  # pylint: disable=protected-access
    spaz.shatter(extreme=True)
    spaz.handlemessage(bs.DieMessage())


def _nuke_fire(pos: Sequence[float]) -> None:
    expl = bs.newnode('explosion', attrs={'position': pos, 'radius': 2.5,
                                         'big': True})
    bs.timer(1.5, expl.delete)
    _snd(random.choice(('explosion01', 'explosion02', 'explosion03',
                        'explosion04', 'explosion05')), 0.7, pos)


def _nuke_hit(other: bs.Node, center: Sequence[float],
              away: Sequence[float], source: Any) -> None:
    if not other:
        return
    opos = other.position
    other.handlemessage(
        'impulse', opos[0], opos[1], opos[2], 0.0, 0.0, 0.0,
        3000.0, 200.0, 0.0, 0, away[0], away[1] + 0.6, away[2],
    )
    if other.getnodetype() == 'spaz':
        other.handlemessage(
            bs.HitMessage(
                pos=opos,
                source_player=bs.existing(source),
                force_direction=away,
                flat_damage=10000.0,
                hit_type='explosion',
                hit_subtype='normal',
            )
        )


# --------------------------- Ice bomb + charge ----------------------------


def _absorb_ice_bomb(spaz: Spaz, bomb: Bomb) -> None:
    """Charged punch on our ice bomb: it shatters into ice fists."""
    charge = _bomb_charge(bomb) or Spaz.bsm_take_charge(spaz)
    bpos = bomb.node.position
    bomb.handlemessage(bs.DieMessage())  # Consumed, never goes off.

    bs.emitfx(position=bpos, velocity=(0, 4, 0), count=30, scale=0.8,
              spread=0.5, chunk_type='ice')
    bs.emitfx(position=bpos, emit_type='distortion', spread=1.0 * FX_STRENGTH)
    _flash(bpos, _ICE, 1.2, 2.0, 3.0, 0.4)
    _ring(spaz.node.position, _ICE, 3.0, 0.35)
    _shake(1.0)
    _snd('shatter', 1.0, bpos)
    _snd('freeze', 1.0, bpos)
    _snd('hiss', 0.8, bpos)
    _snd('orchestra_hit3', 0.8, bpos)

    duration = min(ICE_FISTS_MAX_TIME,
                   ICE_FISTS_TIME + charge * ICE_FISTS_PER_CHARGE)
    _give_ice_fists(spaz, duration)
    if charge >= MAX_CHARGE_TRIGGER:
        spaz._bst_ice_orbs = min(ICE_ORB_MAX, spaz._bst_ice_orbs + 1)
        _update_counter(spaz)
        _popup_text('ЛЕДЯНОЙ ЗАРЯД x1', spaz.node.position, _ICE)


def _fire_ice_orb(spaz: Spaz) -> None:
    """Fire the full-charge ice reward through every enemy in sequence."""
    node = spaz.node
    spaz._bst_ice_orbs -= 1
    _update_counter(spaz)
    facing = _look_dir(spaz)
    center = node.position_center
    start = tuple(center[k] + facing[k] * 0.9 for k in range(3))
    route = _enemy_route(spaz, start)
    target = route.pop(0) if route else None
    orb = Bomb(
        position=start,
        velocity=tuple(c * ICE_ORB_SPEED for c in facing),
        bomb_type='impact',
        blast_radius=0.1,
        bomb_scale=0.6,
        source_player=spaz.source_player,
        owner=node,
    ).autoretain()
    orb._bst_ice_orb = True  # type: ignore[attr-defined]
    orb._bst_levitate = True  # type: ignore[attr-defined]
    orb._bst_ice_owner = node  # type: ignore[attr-defined]
    orb._bst_ice_route = route  # type: ignore[attr-defined]
    orb.arm()
    _start_homing(orb, node, target, facing)
    state = orb._bst_homing  # type: ignore[attr-defined]
    state['speed'] = ICE_ORB_SPEED
    state['vel'] = tuple(c * ICE_ORB_SPEED for c in facing)
    orb.node.velocity = state['vel']
    _flash(start, _ICE, 0.7, 1.1, 2.0, 0.2)
    _ring(start, _ICE, 2.0, 0.25)
    _seq(start, (0, 'freeze', 0.9), (0, 'laser', 0.7),
         (0.02, 'swip2', 0.8))


def _next_ice_target(state: dict) -> bs.Node | None:
    """Take the next still-living target from an ice orb's route."""
    route = state.setdefault('ice_route', [])
    while route:
        target = route.pop(0)
        victim = target.getdelegate(Spaz) if target else None
        if victim is not None and victim.is_alive():
            return target
    return None


def _ice_orb_advance(orb: Bomb, target: bs.Node | None,
                     freeze: bool) -> None:
    """Freeze or skip the current target, then continue through the route."""
    state = getattr(orb, '_bst_homing', None)
    if state is None or not orb.node:
        return
    if target is not None and target and freeze:
        direction, _ = _norm(state.get('vel', (0.0, 1.0, 0.0)))
        _route_blast(orb, target.position_center, direction, ice=True)
    elif target is not None and target:
        _ring(target.position_center, _ICE, 2.2, 0.2)
        _snd('shield_hit', 0.7, target.position_center)

    next_target = state.pop('ice_resume', None)
    victim = next_target.getdelegate(Spaz) if next_target else None
    if victim is None or not victim.is_alive():
        next_target = _next_ice_target(state)
    if next_target is None:
        orb._bst_flight = None  # type: ignore[attr-defined]
        orb.handlemessage(bs.DieMessage())
        return
    state.update({
        'target': next_target,
        'time': 0.0,
        'last': orb.node.position,
        'slow': 0,
        'avoid_until': 0.0,
        'attempt': 0,
        'pingpong': False,
    })
    _start_route_turn(orb, state, next_target)
    _snd('activate_beep', 0.65, next_target.position_center)


def _give_ice_fists(spaz: Spaz, duration: float) -> None:
    node = spaz.node
    now = bs.time()
    spaz._bst_ice_until = max(spaz._bst_ice_until, now + duration)
    if not spaz._bst_ice_nodes:
        light = bs.newnode(
            'light',
            owner=node,
            attrs={
                'color': _ICE,
                'radius': 0.2,
                'height_attenuated': False,
                'volume_intensity_scale': 0.3,
            },
        )
        node.connectattr('position_center', light, 'position')
        bs.animate(light, 'intensity', {0: 0.6, 0.5: 1.2, 1.0: 0.6},
                   loop=True)
        spaz._bst_ice_nodes = [light]
        # Frosty look for the duration.
        spaz._bst_old_highlight = node.highlight
        node.highlight = (0.6, 0.9, 1.5)
    spaz._bst_ice_fx_timer = bs.Timer(
        0.15, _wcall(_ice_fists_tick, spaz), repeat=True
    )
    spaz._bst_ice_timer = bs.Timer(
        spaz._bst_ice_until - now, _wcall(_end_ice_fists, spaz)
    )
    _popup_text('ЛЕДЯНЫЕ КУЛАКИ!', node.position, _ICE)


def _ice_fists_tick(spaz: Spaz) -> None:
    node = spaz.node
    if node:
        bs.emitfx(position=node.punch_position, velocity=(0, 1, 0), count=1,
                  scale=0.4, spread=0.1, chunk_type='ice')


def _end_ice_fists(spaz: Spaz) -> None:
    spaz._bst_ice_until = 0.0
    spaz._bst_ice_fx_timer = None
    spaz._bst_ice_timer = None
    for gnode in spaz._bst_ice_nodes:
        if gnode:
            gnode.delete()
    spaz._bst_ice_nodes = []
    node = spaz.node
    if node:
        if spaz._bst_old_highlight is not None:
            node.highlight = spaz._bst_old_highlight
        _snd('hiss', 0.6, node.position)
    spaz._bst_old_highlight = None


def _ice_fists_active(spaz: Spaz) -> bool:
    return getattr(spaz, '_bst_ice_until', 0.0) > bs.time()


def _ice_punch(victim_node: bs.Node) -> None:
    pos = victim_node.position_center
    victim_node.handlemessage(bs.FreezeMessage(time=ICE_FISTS_FREEZE))
    bs.emitfx(position=pos, velocity=(0, 3, 0), count=15, scale=0.6,
              spread=0.4, chunk_type='ice')
    _flash(pos, _ICE, 0.7, 1.0, 1.8, 0.25)
    _seq(pos, (0, 'freeze', 1.0), (0, 'impact_hard2', 0.7),
         (0.03, 'ding_small_high', 0.4), (0.03, 'shatter', 0.3))


# --------------------------- Thrown ice bomb ------------------------------


def _ice_burst(thrower: bs.Node | None, bomb: Bomb, blast: Blast) -> None:
    """Our charged ice bomb blew up: a spray of mini ice bombs."""
    if not blast.node:
        return
    pos = blast.node.position
    source = bomb.get_source_player(bs.Player)
    _seq(pos, (0, 'cork_pop', 1.0), (0.06, 'cork_pop', 0.8),
         (0.12, 'cork_pop', 0.7), (0, 'orchestra_hit2', 0.7))
    base = random.uniform(0, 2 * math.pi)
    for i in range(ICE_MINI_BOMBS):
        ang = base + 2 * math.pi * i / max(1, ICE_MINI_BOMBS)
        # A gentle toss (lands ~2 m out), standard ice-bomb blast radius.
        mini = Bomb(
            position=(pos[0], pos[1] + 0.4, pos[2]),
            velocity=(math.cos(ang) * 2.5, 4.0, math.sin(ang) * 2.5),
            bomb_type='ice',
            bomb_scale=0.75,
            source_player=source,
            owner=thrower,
        ).autoretain()
        glow = bs.newnode(
            'light',
            owner=mini.node,
            attrs={
                'color': _ICE,
                'radius': 0.12,
                'intensity': 0.6,
                'height_attenuated': False,
                'volume_intensity_scale': 0.3,
            },
        )
        mini.node.connectattr('position', glow, 'position')
        boom_at = ICE_MINI_DELAY + ICE_MINI_STAGGER * i
        bs.timer(boom_at,
                 bs.WeakCallStrict(mini.handlemessage, ExplodeMessage()))
        _seq(pos, (boom_at - 0.25, 'tick', 0.6))  # Tick-tick... boom.


# ------------------------------ Ball game ---------------------------------

# Bot levels: name, how far off their swing at the ball can be (seconds,
# doubles at top speed), how briskly they move about, how often they swing
# at someone close by.
_BOT_LEVELS = (
    ('Лёгкие', 0.25, 0.45, 0.06),
    ('Средние', 0.14, 0.6, 0.1),
    ('Сложные', 0.06, 0.75, 0.15),
    ('Безумные', 0.02, 0.9, 0.2),
)
_BOT_NAMES = ('Вася', 'Маша', 'Кузя', 'Глаша', 'Боря', 'Дуся', 'Тоша',
              'Фрося', 'Гоша', 'Нюша', 'Сеня', 'Зина')
_BOT_LOOKS = (
    ('Spaz', (0.9, 0.3, 0.2), (1.0, 0.8, 0.3)),
    ('Zoe', (0.3, 0.6, 1.0), (1.0, 1.0, 1.0)),
    ('Kronk', (0.3, 0.8, 0.3), (0.9, 0.9, 0.2)),
    ('Mel', (1.0, 0.5, 0.8), (0.4, 0.2, 0.6)),
    ('Jack Morgan', (0.8, 0.6, 0.2), (0.2, 0.2, 0.2)),
    ('Frosty', (0.6, 0.9, 1.0), (0.3, 0.5, 1.0)),
    ('Bones', (0.9, 0.9, 0.9), (0.5, 0.2, 0.9)),
    ('Agent Johnson', (0.3, 0.3, 0.35), (1.0, 0.3, 0.3)),
    ('Pixel', (1.0, 0.8, 0.2), (0.2, 0.9, 0.9)),
    ('Bernard', (0.6, 0.4, 0.2), (0.9, 0.6, 0.3)),
)


class _BallArena(FootballStadium):
    """The stadium by night: the biggest flat field in the game, lit up
    for a ball match."""

    name = 'BSM Арена'

    @classmethod
    def get_play_types(cls) -> list[str]:
        return ['bsm_ball', 'melee', 'keep_away', 'team_flag']

    def __init__(self) -> None:
        super().__init__()
        gnode = bs.getactivity().globalsnode
        gnode.tint = (0.75, 0.8, 1.0)
        gnode.ambient_color = (0.8, 0.85, 1.1)
        gnode.vignette_outer = (0.4, 0.42, 0.55)
        gnode.vignette_inner = (0.95, 0.95, 1.0)
        # Floodlights round the field.
        for xpos in (-9.0, 0.0, 9.0):
            for zpos in (-4.0, 4.8):
                bs.newnode('light', attrs={
                    'position': (xpos, 6.0, zpos), 'radius': 0.9,
                    'intensity': 0.35, 'color': (0.8, 0.85, 1.0),
                    'height_attenuated': False,
                    'volume_intensity_scale': 0.1})


def _ball_slots(count: int) -> list[tuple[float, float, float]]:
    """Places evenly round an oval in the middle of the field."""
    return [(math.cos(2.0 * math.pi * i / count + math.pi) * 7.0, 0.5,
             0.4 + math.sin(2.0 * math.pi * i / count + math.pi) * 3.2)
            for i in range(max(1, count))]


def _hearts(lives: int) -> str:
    return '♥' * max(0, lives)


class _BallBot(Spaz):
    """A ball-game bot: strolls about its spot and, when the ball comes at
    it, tries to punch it on - how well depends on its level and the speed
    of the ball."""

    def __init__(self, level: int, name: str, look: tuple,
                 home: Sequence[float], lives: int) -> None:
        super().__init__(color=look[1], highlight=look[2], character=look[0],
                         start_invincible=False, can_accept_powerups=False)
        self.bsm_team = object()  # Everyone's opponent.
        self.lives = lives
        self.bsm_spec = (level, name, look, tuple(home))  # To come back as.
        self.bsm_out = False  # Knocked out of the match by the game itself.
        self._level = _BOT_LEVELS[level]
        self._home = tuple(home)
        self._goal = tuple(home)
        self._goal_time = 0.0
        self._leg: tuple | None = None
        self._swing_at = BALL_SWING_LEAD
        self._swung = False
        self.node.name = name
        self.node.name_color = _bright(look[1], 1.0)
        self.handlemessage(bs.StandMessage(self._home,
                                           random.uniform(0.0, 360.0)))
        self._think_timer = bs.Timer(0.1, _wcall(_BallBot._think, self),
                                     repeat=True)

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage) and self.is_alive():
            result = super().handlemessage(msg)
            game = BallGame.current()
            if game is not None and not self.bsm_out:
                game.bsm_bot_down(self)  # Beaten up: costs a life.
            return result
        return super().handlemessage(msg)

    def _move(self, vec: Sequence[float], speed: float) -> None:
        self.on_move_left_right(vec[0] * speed)
        self.on_move_up_down(-vec[2] * speed)

    def _think(self) -> None:
        node = self.node
        if not node or not self.is_alive() or self.frozen:
            return
        pos = node.position
        ball = BallGame.ball_after(self)
        if ball is not None:
            # It's coming at us: face it, ready to swing.
            # Keep turned to it (a little step its way) to meet it with
            # the fist.
            to, dist = _norm((ball[0] - pos[0], 0.0, ball[2] - pos[2]))
            self._move(to, 0.25 if dist > 3.0 else 0.12)
            return
        # Someone right up close: turn on them and have a swing.
        foes = [n for n in _live_fighters() if n != node
                and math.dist(n.position, pos) < 1.4]
        if foes:
            foe = min(foes, key=lambda n: math.dist(n.position, pos))
            to, _ = _norm((foe.position[0] - pos[0], 0.0,
                           foe.position[2] - pos[2]))
            self._move(to, 0.3)
            if random.random() < self._level[3]:
                self._swing()
            return
        now = bs.time()
        if now > self._goal_time or math.dist(pos, self._goal) < 0.4:
            # Somewhere new near our spot (now and then just stand still).
            ang = random.uniform(0.0, 2.0 * math.pi)
            rad = random.uniform(0.0, 1.6)
            self._goal = (self._home[0] + math.cos(ang) * rad, self._home[1],
                          self._home[2] + math.sin(ang) * rad)
            self._goal_time = now + random.uniform(1.0, 2.5)
        to, dist = _norm((self._goal[0] - pos[0], 0.0,
                          self._goal[2] - pos[2]))
        self._move(to, self._level[2] if dist > 0.4 else 0.0)

    def _swing(self) -> None:
        if self.node and self.is_alive():
            self.on_punch_press()
            bs.timer(0.1, _wcall(Spaz.on_punch_release, self))

    def bsm_ball_incoming(self, bomb: Bomb, dist: float,
                          speed: float) -> None:
        """The ball is on its way to us: swing so the fist meets it. Only a
        real hit knocks it on (the engine's punch); the level sets how well
        the swing is timed, the faster the ball the harder."""
        if (not self.node or not self.is_alive() or self.frozen
                or self.node.knockout > 0.0):
            return
        state = bomb._bst_homing  # type: ignore[attr-defined]
        leg = (id(bomb), state.get('deflects', 0))
        if self._leg != leg:
            # A new approach: how far off this swing will be.
            frac = max(0.0, min(1.0, (speed - IMPACT_SPEED)
                                / (DEFLECT_MAX_SPEED - IMPACT_SPEED)))
            spread = self._level[1] * (1.0 + frac)
            self._leg = leg
            self._swing_at = BALL_SWING_LEAD + random.uniform(-spread, spread)
            self._swung = False
        if not self._swung and dist / max(speed, 1.0) <= self._swing_at:
            self._swung = True
            self._swing()


class _BallPlayer(bs.Player['_BallTeam']):
    """A player in the ball game."""

    def __init__(self) -> None:
        self.lives = 0
        self.slot: tuple | None = None


class _BallTeam(bs.Team[_BallPlayer]):
    """A team in the ball game."""

    def __init__(self) -> None:
        self.score = 0


class BallGame(bs.TeamGameActivity[_BallPlayer, _BallTeam]):
    """Dodgeball the BSM way: the ball flies round from one to the next,
    faster and faster; punch it on or lose a life."""

    name = 'Мячик'
    description = ('Отбивай мяч кулаком — он летит дальше по кругу и '
                   'разгоняется. Пропустил — минус жизнь.')
    allow_mid_activity_joins = False

    _current: weakref.ref | None = None

    @classmethod
    def get_available_settings(
        cls, sessiontype: type[bs.Session]
    ) -> list[bs.Setting]:
        return [
            bs.IntSetting('Боты', default=3, min_value=0, max_value=10),
            bs.IntChoiceSetting(
                'Сложность ботов',
                choices=[(level[0], i) for i, level in
                         enumerate(_BOT_LEVELS)],
                default=1),
            bs.IntSetting('Жизни', default=BALL_LIVES, min_value=1,
                          max_value=10),
            bs.BoolSetting('Epic Mode', default=False),
        ]

    @classmethod
    def supports_session_type(cls, sessiontype: type[bs.Session]) -> bool:
        return issubclass(sessiontype, (bs.DualTeamSession,
                                        bs.FreeForAllSession))

    @classmethod
    def get_supported_maps(cls, sessiontype: type[bs.Session]) -> list[str]:
        return [_BallArena.name, 'Football Stadium']

    @classmethod
    def current(cls) -> BallGame | None:
        game = cls._current() if cls._current is not None else None
        return None if game is None or game.expired else game

    @classmethod
    def ball_after(cls, bot: _BallBot) -> tuple | None:
        """Where the ball is, if it's flying at this bot."""
        game = cls._current() if cls._current is not None else None
        ball = game._ball if game is not None else None
        state = getattr(ball, '_bst_homing', None)
        if state is None or not ball.node or state.get('target') != bot.node:
            return None
        return ball.node.position

    def __init__(self, settings: dict):
        super().__init__(settings)
        self._bot_count = int(settings.get('Боты', 3))
        self._level = int(settings.get('Сложность ботов', 1))
        self._lives = int(settings.get('Жизни', BALL_LIVES))
        self._epic = bool(settings.get('Epic Mode', False))
        self.slow_motion = self._epic
        self.default_music = (bs.MusicType.EPIC if self._epic
                              else bs.MusicType.SPORTS)
        self._bots: list[_BallBot] = []
        self._ball: Bomb | None = None
        self._serve_timer: bs.Timer | None = None
        self._tick_timer: bs.Timer | None = None
        self._out = 0  # How many have been knocked out so far.
        self._ended = False
        self._slots: list = []
        self._scoreboard = Scoreboard()

    def get_instance_description(self) -> str | Sequence:
        return self.description

    def get_instance_description_short(self) -> str | Sequence:
        return 'отбивай мяч дальше по кругу'

    def on_player_join(self, player: _BallPlayer) -> None:
        if self.has_begun():
            player.lives = 0  # Sits this match out.
            bs.broadcastmessage(f'{player.getname()}: дождись следующего '
                                f'матча', color=(1.0, 1.0, 0.4))
            return
        player.lives = self._lives
        self.spawn_player(player)

    def on_player_leave(self, player: _BallPlayer) -> None:
        super().on_player_leave(player)
        bs.timer(0.1, bs.WeakCallStrict(self._check_end))

    def _slot(self) -> tuple:
        if not self._slots:
            total = len(self.session.sessionplayers) + self._bot_count
            self._slots = _ball_slots(total)
            random.shuffle(self._slots)
        return self._slots.pop()

    def spawn_player(self, player: _BallPlayer) -> bs.Actor:
        if player.slot is None:
            player.slot = self._slot()
        spaz = self.spawn_player_spaz(player, player.slot)
        # No bombs: fists, and 'pick up' to catch the ball and ride it.
        spaz.connect_controls_to_player(enable_bomb=False)
        spaz.set_score_text(_hearts(player.lives), color=(1.0, 0.3, 0.3))
        return spaz

    def on_begin(self) -> None:
        super().on_begin()
        BallGame._current = weakref.ref(self)
        names = random.sample(_BOT_NAMES, min(len(_BOT_NAMES),
                                              self._bot_count))
        for i in range(self._bot_count):
            look = _BOT_LOOKS[i % len(_BOT_LOOKS)]
            name = names[i] if i < len(names) else f'Бот {i + 1}'
            bot = _BallBot(self._level, name, look, self._slot(), self._lives)
            bot.set_score_text(_hearts(bot.lives), color=(1.0, 0.3, 0.3))
            self._bots.append(bot)
        self._update_scoreboard()
        self._serve_timer = bs.Timer(2.0, bs.WeakCallStrict(self._serve))
        self._tick_timer = bs.Timer(0.5, bs.WeakCallStrict(self._tick),
                                    repeat=True)

    def _fighters(self) -> list[Spaz]:
        out: list[Spaz] = [bot for bot in self._bots
                           if bot.node and bot.is_alive()]
        for player in self.players:
            actor = player.actor
            if (player.lives > 0 and isinstance(actor, Spaz) and actor.node
                    and actor.is_alive()):
                out.append(actor)
        return out

    def _serve(self) -> None:
        self._serve_timer = None
        if self._ended:
            return
        fighters = self._fighters()
        if len(fighters) < 2:
            self._check_end()
            return
        target = random.choice(fighters)
        start = (0.0, 1.2, 0.4)  # Low, from the middle of the field.
        ball = Bomb(position=start, velocity=(0.0, 0.0, 0.0),
                    bomb_type='impact', bomb_scale=1.2).autoretain()
        ball._bst_levitate = True  # type: ignore[attr-defined]
        ball._bst_ball_game = weakref.ref(self)  # type: ignore[attr-defined]
        ball.arm()
        light = bs.newnode('light', owner=ball.node, attrs={
            'color': (1.0, 0.9, 0.6), 'radius': 0.15, 'intensity': 0.7,
            'height_attenuated': False, 'volume_intensity_scale': 0.2})
        ball.node.connectattr('position', light, 'position')
        self._ball = ball
        aim, _ = _norm((target.node.position[0] - start[0], 0.0,
                        target.node.position[2] - start[2]))
        # Served a little to one side: it curves in.
        heading = _arc_heading(start, target.node, _turn_flat(
            aim, math.radians(random.uniform(-30.0, 30.0))), IMPACT_SPEED)
        _start_homing(ball, None, target.node, heading)
        bs.emitfx(position=start, velocity=(0.0, 2.0, 0.0), count=30,
                  scale=0.8, spread=0.6, chunk_type='spark')
        _seq(start, (0, 'ref_whistle', 0.8), (0.05, 'activate_beep', 0.7))

    def bsm_ball_hit(self, ball: Bomb) -> None:
        """The ball went off: whoever didn't return it loses a life."""
        state = getattr(ball, '_bst_homing', None) or {}
        ball._exploded = True  # pylint: disable=protected-access
        ball._bst_flight = None  # type: ignore[attr-defined]
        if ball is self._ball:
            self._ball = None
        pos = ball.node.position if ball.node else (0.0, 1.0, 0.4)
        victim: Spaz | None = None
        target = state.get('target')
        spaz = target.getdelegate(Spaz) if target else None
        if (spaz is not None and spaz.is_alive()
                and math.dist(target.position_center, pos) < 2.0):
            victim = spaz
        else:
            # It went off on someone else who got in its way.
            near = [s for s in self._fighters() if s.node != ball.owner
                    and math.dist(s.node.position_center, pos) < 1.3]
            if near:
                victim = min(near, key=lambda s: math.dist(
                    s.node.position_center, pos))
        expl = bs.newnode('explosion', attrs={'position': pos,
                                               'radius': 0.9})
        bs.timer(1.0, expl.delete)
        bs.emitfx(position=pos, velocity=(0.0, 3.0, 0.0), count=40,
                  scale=1.0, spread=0.6, chunk_type='spark')
        _shake(1.5)
        _seq(pos, (0, 'explosion01', 0.8), (0, 'big_impact', 0.9),
             (0.05, 'score_hit01', 0.7))
        if ball.node:
            ball.handlemessage(bs.DieMessage())
        if victim is not None:
            self._lose_life(victim, state.get('dir', (0.0, 0.0, 1.0)))
        if not self._ended:
            self._serve_timer = bs.Timer(BALL_SERVE_DELAY,
                                         bs.WeakCallStrict(self._serve))

    def _lose_life(self, spaz: Spaz, push: Sequence[float]) -> None:
        node = spaz.node
        pos = node.position_center
        node.handlemessage('impulse', pos[0], pos[1], pos[2], 0.0, 0.0, 0.0,
                           600.0, 60.0, 0.0, 0, push[0], push[1] + 0.4,
                           push[2])
        node.handlemessage('knockout', 300.0)
        player = spaz.getplayer(_BallPlayer) if isinstance(
            spaz, PlayerSpaz) else None
        lives = self._spend_life(spaz, player)
        spaz.set_score_text(_hearts(lives) or 'ВЫБЫЛ', color=(1.0, 0.3, 0.3),
                            flash=True)
        if lives <= 0:
            if isinstance(spaz, _BallBot):
                spaz.bsm_out = True
            bs.timer(0.8, _wcall(BallGame._knock_out, spaz))

    def _spend_life(self, spaz: Spaz | None,
                    player: _BallPlayer | None) -> int:
        """One life off (ball missed or beaten up); lives left."""
        if player is not None:
            player.lives -= 1
            lives = player.lives
        else:
            spaz.lives = getattr(spaz, 'lives', 1) - 1  # type: ignore
            lives = spaz.lives  # type: ignore[attr-defined]
        if spaz is not None and spaz.node:
            _popup_text('-1 ♥', spaz.node.position, (1.0, 0.3, 0.3))
        if lives <= 0:
            self._out += 1
            if player is not None:
                player.team.score = max(player.team.score, self._out)
            _snd('boo', 0.6)
        else:
            _snd('cheer', 0.4)
        self._update_scoreboard()
        bs.timer(1.0, bs.WeakCallStrict(self._check_end))
        return lives

    @staticmethod
    def _knock_out(spaz: Spaz) -> None:
        if spaz.node and spaz.is_alive():
            spaz.handlemessage(bs.DieMessage())

    def bsm_bot_down(self, bot: _BallBot) -> None:
        """A bot was beaten up: a life off, back on its spot if it's got
        any left."""
        if self._ended or bot.lives <= 0:
            return
        if self._spend_life(bot, None) > 0:
            bs.timer(2.0, _wcall(self._bot_back, bot))

    def _bot_back(self, bot: _BallBot) -> None:
        if self._ended or bot not in self._bots:
            return
        level, name, look, home = bot.bsm_spec
        fresh = _BallBot(level, name, look, home, bot.lives)
        fresh.set_score_text(_hearts(fresh.lives), color=(1.0, 0.3, 0.3))
        self._bots[self._bots.index(bot)] = fresh

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.PlayerDiedMessage):
            super().handlemessage(msg)
            player = msg.getplayer(_BallPlayer)
            # Beaten up (the game's own knock-out leaves no lives): costs
            # a life, then back in if any are left.
            if (player.lives > 0 and not self._ended
                    and self._spend_life(player.actor if isinstance(
                        player.actor, Spaz) else None, player) > 0):
                self.respawn_player(player)
            bs.timer(0.1, bs.WeakCallStrict(self._check_end))
            return None
        return super().handlemessage(msg)

    def _tick(self) -> None:
        # A ball lost off the map (or anything else): serve a new one.
        if (not self._ended and self._serve_timer is None
                and (self._ball is None or not self._ball.node)):
            self._ball = None
            self._serve_timer = bs.Timer(BALL_SERVE_DELAY,
                                         bs.WeakCallStrict(self._serve))
        self._check_end()

    def _check_end(self) -> None:
        if self._ended or not self.has_begun():
            return
        humans = [p for p in self.players if p.lives > 0]
        bots = [b for b in self._bots if b.lives > 0]  # (Or coming back.)
        teams = {p.team for p in humans}
        sides = len(teams) + len(bots)
        # Over when one side is left - or when every human is out.
        if sides <= 1 or (self.players and not humans):
            self._ended = True
            bs.timer(1.0, bs.WeakCallStrict(self.end_game))

    def _update_scoreboard(self) -> None:
        for team in self.teams:
            self._scoreboard.set_team_value(
                team, sum(max(0, p.lives) for p in team.players),
                self._lives * max(1, len(team.players)))

    def end_game(self) -> None:
        if self._ball is not None and self._ball.node:
            self._ball.handlemessage(bs.DieMessage())
        results = bs.GameResults()
        for team in self.teams:
            alive = any(p.lives > 0 for p in team.players)
            results.set_team_score(team, team.score + (100 if alive else 0))
        self.end(results=results)


# ------------------------------- Patches ----------------------------------


def _patched_init(self: Spaz, *args: Any, **kwargs: Any) -> None:
    _orig_init(self, *args, **kwargs)
    self._bst_ice_until = 0.0
    self._bst_ice_nodes: list[bs.Node] = []
    self._bst_ice_timer: bs.Timer | None = None
    self._bst_ice_fx_timer: bs.Timer | None = None
    self._bst_old_highlight: Any = None
    self._bst_whips = 0
    self._bst_whip_charge = 0.0
    self._bst_whip_active = False
    self._bst_whip_timers: list[bs.Timer] = []
    self._bst_shots = 0
    self._bst_homing_shots = 0
    self._bst_shot_charge = 0.0
    self._bst_ice_orbs = 0
    self._bst_qte: dict | None = None


def _patched_handlemessage(self: Spaz, msg: Any) -> Any:
    if not hasattr(self, '_bst_ice_until'):
        return _orig_handlemessage(self, msg)

    if isinstance(msg, PunchHitMessage) and self.node:
        try:
            hit = bs.getcollision().opposingnode
        except bs.NotFoundError:
            hit = None
        fresh = hit is not None and hit not in self._punched_nodes

        bomb = hit.getdelegate(Bomb) if fresh else None

        # Ping-pong: the homing bomb's target knocks it back at the sender.
        # (In the ball game anyone but its rider can: a real fist on it.)
        homing = getattr(bomb, '_bst_homing', None)
        if (
            homing is not None
            and getattr(bomb, '_bst_flight', None) is not None
            and (
                (homing['target'] is not None
                 and homing['target'] == self.node)
                or (homing.get('low') and homing.get('rider') != self.node)
            )
        ):
            self._punched_nodes.add(hit)
            _deflect_homing(self, bomb)
            return None

        # Kicking our own charged mine (before it arms): the big minefield.
        if (
            bomb is not None
            and bomb.bomb_type == 'land_mine'
            and getattr(bomb, '_bst_mine_spread', False)
            and _is_own_bomb(self, bomb)
        ):
            self._punched_nodes.add(hit)
            _kick_mine(self, bomb)
            return None

        # Charged punch on our own flying normal bomb: mini shells.
        if (
            bomb is not None
            and bomb.bomb_type == 'normal'
            and _is_own_bomb(self, bomb)
            and (_charged(self) or _bomb_charge(bomb) > 0)
            and _norm(bomb.node.velocity)[1] > 1.5
        ):
            self._punched_nodes.add(hit)
            _bomb_to_shots(self, bomb)
            return None

        # Charged punch on our own impact/ice/sticky bomb.
        if (
            bomb is not None
            and bomb.bomb_type in ('impact', 'ice', 'sticky')
            and _is_own_bomb(self, bomb)
            and (_charged(self) or _bomb_charge(bomb) > 0)
        ):
            self._punched_nodes.add(hit)
            if bomb.bomb_type == 'impact':
                _launch_impact_bomb(self, bomb)
            elif bomb.bomb_type == 'ice':
                _absorb_ice_bomb(self, bomb)
            else:
                _wrap_into_whip(self, bomb)
            return None

        # Ice fists: whoever we punch freezes.
        if fresh and _ice_fists_active(self):
            result = _orig_handlemessage(self, msg)
            victim = hit.getdelegate(Spaz) if hit else None
            if (
                hit in self._punched_nodes
                and victim is not None
                and victim is not self
            ):
                _ice_punch(hit)
            return result

    if isinstance(msg, bs.DieMessage) and self._bst_ice_nodes:
        _end_ice_fists(self)
    if isinstance(msg, bs.DieMessage):
        qte = self._bst_qte
        if qte is not None and not qte['done']:
            # Died mid-QTE (fell off, etc.): just clear the prompts.
            qte['done'] = True
            qte['timer'] = None
            for old in qte['nodes'] + qte['fixed']:
                if old:
                    old.delete()
            self._bst_qte = None

    return _orig_handlemessage(self, msg)


def _patched_drop_bomb(self: Spaz) -> Bomb | None:
    if getattr(self, '_bst_whips', 0) > 0 and self.node and not self.frozen:
        _fire_whip(self)  # No cooldown: as many at once as you've got.
        # Not a bomb: other plugins/games shouldn't treat it as one.
        return None
    if getattr(self, '_bst_ice_orbs', 0) > 0 and self.node and not self.frozen:
        _fire_ice_orb(self)
        return None
    if getattr(self, '_bst_shots', 0) > 0 and self.node and not self.frozen:
        _fire_shot(self)
        return None
    # Checked before the call: Absorb Shield may spend the charge inside it.
    charged = _charged(self)
    bomb = _orig_drop_bomb(self)
    if bomb is not None and bomb.bomb_type == 'sticky' and charged:
        # Lashes out at enemies once thrown (see _start_tentacle).
        bomb._bst_tentacle_owner = weakref.ref(self)  # type: ignore[attr-defined]
    if bomb is not None and bomb.bomb_type == 'land_mine' and charged:
        bomb._bst_mine_spread = True  # type: ignore[attr-defined]
    if bomb is not None and bomb.bomb_type == 'ice' and charged:
        thrower = self.node
        bomb.add_explode_callback(
            lambda bmb, blast: _ice_burst(thrower, bmb, blast)
        )
    return bomb


def _patched_set_land_mine_count(self: Spaz, count: int) -> None:
    _orig_set_land_mine_count(self, count)
    if (getattr(self, '_bst_whips', 0) > 0
            or getattr(self, '_bst_ice_orbs', 0) > 0
            or getattr(self, '_bst_shots', 0) > 0):
        _update_counter(self)


def _patched_bomb_handlemessage(self: Bomb, msg: Any) -> Any:
    homing = getattr(self, '_bst_homing', None)
    if (isinstance(msg, bs.HitMessage)
            and (getattr(self, '_bst_ice_orb', False)
                 or bool(homing and homing.get('touring')))):
        # Route-stop blasts must hit nearby fighters and props, but never
        # knock their own carrier out of its multi-target flight.
        return None
    if isinstance(msg, ExplodeMessage) and getattr(self, '_bst_ice_orb', False):
        if self.node:
            pos = self.node.position
            bs.emitfx(position=pos, velocity=(0, 3, 0), count=16, scale=0.6,
                      spread=0.4, chunk_type='ice')
            _snd('shatter', 0.8, pos)
        self._bst_flight = None  # type: ignore[attr-defined]
        self.handlemessage(bs.DieMessage())
        return None
    if isinstance(msg, ExplodeMessage) and getattr(self, '_bst_shell', False):
        _shell_pop(self)
        return None
    game_ref = getattr(self, '_bst_ball_game', None)
    if game_ref is not None:
        # The ball game's ball: punches and blasts don't set it off; when
        # it goes off, the game sorts out who missed it.
        if isinstance(msg, bs.HitMessage):
            return None
        if isinstance(msg, bs.PickedUpMessage):
            # Anyone may grab it: off it goes with them in tow.
            picker = msg.node
            homing = getattr(self, '_bst_homing', None) or {}
            spaz = picker.getdelegate(Spaz) if picker else None
            if spaz is not None and homing.get('rider') != picker:
                _catch(spaz, self)
            return None
        game = game_ref()
        if (isinstance(msg, ExplodeMessage) and game is not None
                and not getattr(self, '_exploded', False)):
            game.bsm_ball_hit(self)
            return None
    if (
        isinstance(msg, ExplodeMessage)
        and homing is not None
        and homing.get('deflects', 0) >= CONE_AFTER_DEFLECTS
        and not getattr(self, '_exploded', False)
    ):
        _cone_blast(self)
        return None
    result = _orig_bomb_handlemessage(self, msg)
    if isinstance(msg, ArmMessage) and getattr(self, '_bst_mine_spread', False):
        self._bst_mine_spread = False  # type: ignore[attr-defined]
        _spread_mines(self)
    if getattr(self, '_bst_tentacle_owner', None) is not None:
        if isinstance(msg, bs.DroppedMessage):
            _start_tentacle(self)
        elif isinstance(msg, bs.PickedUpMessage):
            _stop_tentacle(self)
    return result


def _patched_bomb_handle_impact(self: Bomb) -> None:
    if getattr(self, '_bst_levitate', False):
        # Homing after our punch: only a fighter (not its owner) sets it
        # off; walls and floors are just obstacles to fly around.
        try:
            node = bs.getcollision().opposingnode
        except bs.NotFoundError:
            return
        if not node or node.getnodetype() != 'spaz' or node == self.owner:
            self._bst_bump_time = bs.time()  # type: ignore[attr-defined]
            return
        homing = getattr(self, '_bst_homing', None)
        # After switching targets the projectile can remain physically
        # touching the previous fighter for another collision tick. Never
        # let that stale contact fall through to Bomb._handle_impact(), which
        # would explode a tour bomb (or delete an ice orb) after its first
        # target.
        routed = (getattr(self, '_bst_ice_orb', False)
                  or bool(homing and homing.get('touring')))
        if routed and (homing is None or node != homing.get('target')):
            self._bst_bump_time = bs.time()  # type: ignore[attr-defined]
            return
        if (homing is not None and node == homing.get('target')
                and not homing.get('low')):
            here = self.node.position
            victim = node.getdelegate(Spaz)
            if getattr(victim, '_ab_active', False):
                if getattr(self, '_bst_ice_orb', False):
                    _ice_orb_advance(self, node, freeze=False)
                    return
                if homing.get('touring'):
                    _impact_tour_hit(self, node, damage=False)
                    return
            if _try_contact_deflect(self, homing.get('last', here), here):
                return  # Met their fist: deflected, not hit.
            if getattr(self, '_bst_ice_orb', False):
                _ice_orb_advance(self, node, freeze=True)
                return
            if homing.get('touring'):
                _impact_tour_hit(self, node)
                return
    _orig_bomb_handle_impact(self)


def _patched_curse_explode(self: Spaz, source_player: Any = None) -> None:
    if getattr(self, '_bst_qte', None) is not None:
        return  # Mid-QTE or mid-countdown: the nuke decides now.
    if (
        self._cursed  # pylint: disable=protected-access
        and self.node
        and getattr(self, '_ab_active', False)  # Parried (Absorb Shield).
        and isinstance(self, PlayerSpaz)
    ):
        _start_nuke_qte(self)
        return
    _orig_curse_explode(self, source_player)


def _qte_press(key: str, orig_name: str) -> Any:
    def _press(self: Spaz) -> None:
        qte = getattr(self, '_bst_qte', None)
        if qte is not None:
            if not qte['done']:
                _qte_input(self, key)
            return  # The QTE (or the countdown) eats the button.
        globals()[orig_name](self)

    return _press


# ba_meta export babase.Plugin
class BoostersPlugin(babase.Plugin):
    """Impact and ice bomb add-ons."""

    def __init__(self) -> None:
        # The mod may be both built into BSM and dropped into mods/;
        # only the first copy patches the game.
        if getattr(Spaz, '_bst_patched', False):
            return
        Spaz._bst_patched = True  # type: ignore[attr-defined]

        global _orig_init, _orig_handlemessage, _orig_drop_bomb
        global _orig_bomb_handle_impact, _orig_bomb_handlemessage
        global _orig_set_land_mine_count, _orig_curse_explode
        global _orig_jump_press, _orig_punch_press, _orig_bomb_press
        global _orig_pickup_press
        _orig_init = Spaz.__init__
        _orig_handlemessage = Spaz.handlemessage
        _orig_drop_bomb = Spaz.drop_bomb
        _orig_bomb_handle_impact = Bomb._handle_impact
        _orig_bomb_handlemessage = Bomb.handlemessage
        _orig_set_land_mine_count = Spaz.set_land_mine_count
        _orig_curse_explode = Spaz.curse_explode
        _orig_jump_press = Spaz.on_jump_press
        _orig_punch_press = Spaz.on_punch_press
        _orig_bomb_press = Spaz.on_bomb_press
        _orig_pickup_press = Spaz.on_pickup_press

        Spaz.__init__ = _patched_init
        Spaz.handlemessage = _patched_handlemessage
        Spaz.drop_bomb = _patched_drop_bomb
        Bomb._handle_impact = _patched_bomb_handle_impact
        Bomb.handlemessage = _patched_bomb_handlemessage
        Spaz.set_land_mine_count = _patched_set_land_mine_count
        Spaz.curse_explode = _patched_curse_explode
        Spaz.on_jump_press = _qte_press('jump', '_orig_jump_press')
        Spaz.on_punch_press = _qte_press('punch', '_orig_punch_press')
        Spaz.on_bomb_press = _qte_press('bomb', '_orig_bomb_press')
        Spaz.on_pickup_press = _qte_press('pickup', '_orig_pickup_press')
        _register_ball_game()


def _register_ball_game() -> None:
    """The ball game and its arena join the game lists (only from the copy
    that patched the game, so they're never listed twice)."""
    try:
        if _BallArena.name not in babase.app.classic.maps:
            bs.register_map(_BallArena)
    except Exception:
        logging.exception('BSM: could not add the ball arena')
    try:
        exports = babase.app.meta.scanresults.exports.setdefault(
            'bascenev1.GameActivity', [])
        path = f'{__name__}.BallGame'
        if path not in exports:
            exports.append(path)
    except Exception:
        logging.exception('BSM: could not add the ball game')
