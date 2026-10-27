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
    прямо и взрывается обо что угодно.

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
  * удар кулаком по своей липкой бомбе — она превращается в щупальце
    (1 шт., до 3). Кнопка «Бомба» выстреливает его из руки вперёд (до 8 м):
    оно доворачивает к ближайшему врагу перед бойцом (до 40°), а если такого
    нет — летит прямо и хватает первого, кого заденет. Пойманного валит с
    ног, на него налепляются 4 липкие мини-бомбы и через 0.8 с взрываются
    прямо на нём; заряд делает их взрывы шире. Потом щупальце втягивается.

Работает и на «Счастливых мыслях»: направления и расстояния считаются в 3D.
Мод нужен только хосту: в сетевой игре всё считается на сервере.
"""

from __future__ import annotations

import math
import random
import weakref
from typing import TYPE_CHECKING

import babase
import bascenev1 as bs
from bascenev1 import _classicassets
from bascenev1lib.actor.bomb import Bomb, BombFactory, ExplodeMessage
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.spaz import PunchHitMessage, Spaz

if TYPE_CHECKING:
    from typing import Any, Sequence

    from bascenev1lib.actor.bomb import Blast

# Версия для автообновления BSM (bsm_updater.py сверяет её с GitHub).
BSM_VERSION = '2.5'

# ------------------------------- Настройки --------------------------------

IMPACT_SPEED = 22.0  # Скорость ударной бомбы после удара (м/с).
IMPACT_FLIGHT_TIME = 4.0  # Сколько она ищет путь к врагу, потом взрывается.
IMPACT_STEER = 0.3  # Плавность разворотов в полёте (1.0 — мгновенно).
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
WHIP_RANGE = 8.0  # Дальность щупальца-предмета (метров).
WHIP_ANGLE = 40.0  # Насколько враг может быть в стороне от взгляда (градусов).
WHIP_SPEED = 30.0  # Скорость вылета щупальца (м/с).
WHIP_FUSE = 0.8  # Через сколько взрываются налепленные мини-бомбы (сек).
WHIP_MAX = 3  # Сколько щупалец можно носить.
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


def _team(spaz: Spaz) -> Any:
    if isinstance(spaz, PlayerSpaz):
        player = spaz.getplayer(bs.Player)
        return player.team if player else None
    return 'bots'


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
    """Closest enemy within the cone of the punch, in full 3D."""
    min_cos = math.cos(math.radians(IMPACT_ANGLE))
    best: bs.Node | None = None
    best_score = 0.0
    for node in bs.getnodes():
        if not node or node.getnodetype() != 'spaz':
            continue
        other = node.getdelegate(Spaz)
        if other is None or not other.is_alive() or not _is_enemy(spaz, other):
            continue
        to, dist = _norm([a - b for a, b in zip(node.position_center,
                                                origin)])
        if dist < 0.01 or dist > IMPACT_RANGE:
            continue
        cos = sum(a * b for a, b in zip(to, direction))
        if cos < min_cos:
            continue
        score = dist / cos  # Close and straight ahead wins.
        if best is None or score < best_score:
            best, best_score = node, score
    return best


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
    target = _find_target(spaz, bnode.position, direction)
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

    state: dict[str, Any] = {
        'time': 0.0,
        'dir': direction,
        'vel': tuple(c * IMPACT_SPEED for c in direction),
        'last': bnode.position,
        'slow': 0,
        'avoid_until': 0.0,
        'avoid_dir': direction,
        'attempt': 0,
    }

    def _stop() -> None:
        bomb._bst_flight = None  # type: ignore[attr-defined]

    def _step() -> None:
        state['time'] += _TICK
        if not bnode or getattr(bomb, '_exploded', False):
            _stop()
            return
        tnow = state['time']
        bpos = bnode.position

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
                _stop()
                bomb.handlemessage(ExplodeMessage())
                return
            tpos = target.position_center
            want, dist = _norm([a - b for a, b in zip(tpos, bpos)])
            # It goes off when it physically touches them (see
            # _patched_bomb_handle_impact); this is only a backstop.
            if dist < 0.55:
                _stop()
                _snd('big_impact', 1.0, bpos)
                bomb.handlemessage(ExplodeMessage())
                return
            # Aim a little above their middle so the line clears slopes
            # (domes like Doom Shroom).
            want, _ = _norm((tpos[0] - bpos[0], tpos[1] + 0.25 - bpos[1],
                             tpos[2] - bpos[2]))

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
            # Scraping the floor: just lift off it a bit and slide along.
            if bs.time() - getattr(bomb, '_bst_bump_time', -9.0) < 0.12:
                fdir, _ = _norm((fdir[0], fdir[1] + 0.35, fdir[2]))
            state['dir'] = fdir

        state['last'] = bpos
        # Turn smoothly instead of snapping to the new heading.
        goal = tuple(c * IMPACT_SPEED for c in fdir)
        vel = tuple(v + (g - v) * IMPACT_STEER
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
    _seq(start, (0, 'sticky_impact', 0.6), (0.05, 'swip', 0.4))

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
                # Lash, slap, squelch.
                _seq(bpos, (0, 'swip', 0.8), (0, 'sticky_impact', 1.0))
                _seq(node.position, (0.04, 'splatter', 0.8),
                     (0.06, 'cork_pop', 0.4))
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
                _seq(bpos, (0, 'sticky_impact', 1.0), (0.03, 'splatter', 0.6))
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

_WHIP_SEGMENTS = 10


def _update_counter(spaz: Spaz) -> None:
    """Whips show in the counter over the head (mines once out of them)."""
    node = spaz.node
    if not node:
        return
    if spaz._bst_whips > 0:
        node.counter_text = f'x{spaz._bst_whips}'
        node.counter_texture = _classicassets.textures.powerup_sticky_bombs.get()
    else:
        _orig_set_land_mine_count(spaz, spaz.land_mine_count)


def _wrap_into_whip(spaz: Spaz, bomb: Bomb) -> None:
    """Charged punch on our sticky bomb: it turns into a tentacle whip."""
    charge = _bomb_charge(bomb) or Spaz.bsm_take_charge(spaz)
    bpos = bomb.node.position
    bomb.handlemessage(bs.DieMessage())  # Consumed, never goes off.
    spaz._bst_whips = min(WHIP_MAX, spaz._bst_whips + 1)
    spaz._bst_whip_charge += charge
    _update_counter(spaz)

    bs.emitfx(position=bpos, velocity=(0, 3, 0), count=20, scale=0.7,
              spread=0.4, chunk_type='slime')
    _flash(bpos, _SLIME, 0.8, 1.2, 1.5, 0.25)
    _seq(bpos, (0, 'sticky_impact', 1.0), (0, 'splatter', 0.8),
         (0.05, 'powerup01', 0.7), (0.1, 'bell_low', 0.4),
         (0.18, 'bell_med', 0.4))
    _popup_text('ЩУПАЛЬЦЕ!', spaz.node.position, _SLIME)


def _whip_target(spaz: Spaz, facing: Sequence[float]) -> bs.Node | None:
    """Closest enemy in front (horizontal cone, any height)."""
    origin = spaz.node.position_center
    min_cos = math.cos(math.radians(WHIP_ANGLE))
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
        if dist > WHIP_RANGE or flen < 0.01:
            continue
        cos = flat[0] * facing[0] + flat[2] * facing[2]
        if cos < min_cos:
            continue
        score = dist / cos
        if best is None or score < best_score:
            best, best_score = node, score
    return best


def _fire_whip(spaz: Spaz) -> None:
    """The bomb button lashes the tentacle out of the fighter's hand."""
    node = spaz.node
    spaz._bst_whips -= 1
    charge, spaz._bst_whip_charge = spaz._bst_whip_charge, 0.0
    _update_counter(spaz)
    spaz._bst_whip_active = True

    facing, flen = _norm((node.position_forward[0] - node.position[0], 0.0,
                          node.position_forward[2] - node.position[2]))
    if flen < 1e-4:
        facing = (1.0, 0.0, 0.0)

    def _base() -> tuple:
        pos = node.position_center
        return (pos[0] + facing[0] * 0.35, pos[1] + 0.15,
                pos[2] + facing[2] * 0.35)

    target = _whip_target(spaz, facing)
    start = _base()
    straight_end = tuple(start[k] + facing[k] * WHIP_RANGE for k in range(3))
    beads = _tentacle_beads(start, _WHIP_SEGMENTS, 0.16, 0.06, node)
    source = spaz.source_player
    state: dict[str, Any] = {'time': 0.0, 'phase': 'out', 'tip': start,
                             'victim': None}
    # The lash: whip crack and a wet whoosh.
    _seq(start, (0, 'swip2', 1.0), (0, 'swish', 0.8), (0.02, 'laser', 0.2),
         (0.03, 'sticky_impact', 0.7))

    def _finish() -> None:
        spaz._bst_whip_active = False
        spaz._bst_whip_timer = None
        _delete_all(beads)

    def _latch(victim_node: bs.Node) -> None:
        state['phase'] = 'hold'
        state['victim'] = victim_node
        state['hold_until'] = state['time'] + WHIP_FUSE + 0.45
        vpos = victim_node.position_center
        victim_node.handlemessage('knockout', (WHIP_FUSE + 0.2) * 1000.0)
        bs.emitfx(position=vpos, velocity=(0, 3, 0), count=20, scale=0.7,
                  spread=0.4, chunk_type='slime')
        _seq(vpos, (0, 'splatter', 1.0), (0, 'sticky_impact', 1.0),
             (0.05, 'cork_pop', 0.9), (0.1, 'cork_pop', 0.7))
        # Countdown ticks before the four minis go off.
        _seq(vpos, (WHIP_FUSE - 0.45, 'tick', 0.8),
             (WHIP_FUSE - 0.3, 'tick', 0.8), (WHIP_FUSE - 0.15, 'warn_beep',
                                               0.7))
        # Four mini sticky bombs slap onto them from all sides.
        blast = 1.2 + min(1.0, charge / 1000.0)  # Charge widens them.
        for i in range(4):
            ang = i * math.pi / 2 + math.pi / 4
            out = (math.cos(ang), 0.0, math.sin(ang))
            mini = Bomb(
                position=(vpos[0] + out[0] * 0.4, vpos[1] + 0.2,
                          vpos[2] + out[2] * 0.4),
                velocity=(-out[0] * 3.0, 0.0, -out[2] * 3.0),
                bomb_type='sticky',
                blast_radius=blast,
                bomb_scale=0.5,
                source_player=source,
                owner=node,
            ).autoretain()
            bs.timer(WHIP_FUSE + 0.1 * i,
                     bs.WeakCallStrict(mini.handlemessage, ExplodeMessage()))

    def _step() -> None:
        state['time'] += _TICK
        tnow = state['time']
        if not node or not spaz.is_alive():
            _finish()
            return
        base = _base()
        tip = state['tip']
        phase = state['phase']

        if phase == 'out':
            victim = target.getdelegate(Spaz) if target else None
            homing = victim is not None and victim.is_alive()
            goal = target.position_center if homing else straight_end
            move, dist = _norm([a - b for a, b in zip(goal, tip)])
            step = WHIP_SPEED * _TICK
            tip = goal if dist <= step else tuple(
                tip[k] + move[k] * step for k in range(3))
            state['tip'] = tip
            if homing and _norm([a - b for a, b in
                                 zip(target.position_center, tip)])[1] < 0.6:
                _latch(target)
            elif not homing:
                # No aim: grab the first enemy the tip brushes past.
                for vnode in _tentacle_targets(spaz, tip):
                    if _norm([a - b for a, b in
                              zip(vnode.position_center, tip)])[1] < 0.8:
                        _latch(vnode)
                        break
                else:
                    if dist <= step or tnow > 0.8:
                        state['phase'] = 'back'
            if tnow > 0.8 and state['phase'] == 'out':
                state['phase'] = 'back'
        elif phase == 'hold':
            vnode = state['victim']
            if vnode:
                state['tip'] = tip = vnode.position_center
            if tnow >= state['hold_until'] or not vnode:
                state['phase'] = 'back'
                _seq(base, (0, 'swip', 0.8), (0.05, 'sticky_impact', 0.4))
        else:  # Reeling back in.
            move, dist = _norm([a - b for a, b in zip(base, tip)])
            step = WHIP_SPEED * 1.3 * _TICK
            if dist <= step:
                _finish()
                return
            state['tip'] = tip = tuple(tip[k] + move[k] * step
                                       for k in range(3))

        amp = 0.3 if state['phase'] == 'out' else 0.12
        try:
            pts = _tentacle_curve(base, state['tip'], tnow * 14.0, amp,
                                  _WHIP_SEGMENTS)
            _draw_tentacle(beads, pts, True)
            bs.emitfx(position=state['tip'], velocity=(0, -1, 0), count=1,
                      scale=0.4, spread=0.05, chunk_type='slime')
        except Exception:
            _BEADS_OK[0] = False  # Visuals must never stop the whip.

    spaz._bst_whip_timer = bs.Timer(_TICK, _wcall(lambda s: _step(), spaz),
                                    repeat=True)
    _step()


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
    _seq(bpos, (0, 'shatter', 1.0), (0, 'freeze', 1.0), (0, 'hiss', 0.8),
         (0, 'orchestra_hit3', 0.8), (0.1, 'bell_high', 0.5),
         (0.2, 'ding_small_high', 0.5))

    duration = min(ICE_FISTS_MAX_TIME,
                   ICE_FISTS_TIME + charge * ICE_FISTS_PER_CHARGE)
    _give_ice_fists(spaz, duration)


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
        _seq(node.position, (0, 'hiss', 0.6), (0, 'laser_reverse', 0.3))
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
    self._bst_whip_timer: bs.Timer | None = None


def _patched_handlemessage(self: Spaz, msg: Any) -> Any:
    if not hasattr(self, '_bst_ice_until'):
        return _orig_handlemessage(self, msg)

    if isinstance(msg, PunchHitMessage) and self.node:
        try:
            hit = bs.getcollision().opposingnode
        except bs.NotFoundError:
            hit = None
        fresh = hit is not None and hit not in self._punched_nodes

        # Charged punch on our own impact/ice bomb.
        bomb = hit.getdelegate(Bomb) if fresh else None
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

    return _orig_handlemessage(self, msg)


def _patched_drop_bomb(self: Spaz) -> Bomb | None:
    if getattr(self, '_bst_whips', 0) > 0 and self.node and not self.frozen:
        if not self._bst_whip_active:
            _fire_whip(self)
        # Not a bomb: other plugins/games shouldn't treat it as one.
        return None
    # Checked before the call: Absorb Shield may spend the charge inside it.
    charged = _charged(self)
    bomb = _orig_drop_bomb(self)
    if bomb is not None and bomb.bomb_type == 'sticky' and charged:
        # Lashes out at enemies once thrown (see _start_tentacle).
        bomb._bst_tentacle_owner = weakref.ref(self)  # type: ignore[attr-defined]
    if bomb is not None and bomb.bomb_type == 'ice' and charged:
        thrower = self.node
        bomb.add_explode_callback(
            lambda bmb, blast: _ice_burst(thrower, bmb, blast)
        )
    return bomb


def _patched_set_land_mine_count(self: Spaz, count: int) -> None:
    _orig_set_land_mine_count(self, count)
    if getattr(self, '_bst_whips', 0) > 0:
        _update_counter(self)


def _patched_bomb_handlemessage(self: Bomb, msg: Any) -> Any:
    result = _orig_bomb_handlemessage(self, msg)
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
    _orig_bomb_handle_impact(self)


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
        global _orig_set_land_mine_count
        _orig_init = Spaz.__init__
        _orig_handlemessage = Spaz.handlemessage
        _orig_drop_bomb = Spaz.drop_bomb
        _orig_bomb_handle_impact = Bomb._handle_impact
        _orig_bomb_handlemessage = Bomb.handlemessage
        _orig_set_land_mine_count = Spaz.set_land_mine_count

        Spaz.__init__ = _patched_init
        Spaz.handlemessage = _patched_handlemessage
        Spaz.drop_bomb = _patched_drop_bomb
        Bomb._handle_impact = _patched_bomb_handle_impact
        Bomb.handlemessage = _patched_bomb_handlemessage
        Spaz.set_land_mine_count = _patched_set_land_mine_count
