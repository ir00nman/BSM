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
    волне щита разбрасывает 3 ледяные мини-бомбы, которые взрываются одна за
    другой вскоре после основной.

Липкая бомба, заряжен:
  * брошенная заряженная липкая бомба шевелит щупальцами из слизи и
    хватает ВСЕХ врагов в радиусе 3.5 м (и тех, кто зайдёт позже) — на
    каждого своё щупальце; подтягивает их к бомбе, пока не прилипнут, а
    потом обвивает;
  * удар кулаком по своей липкой бомбе — она сворачивается в сеть (1 шт.):
    комок сети с 4 грузиками-мини-бомбами. Сеть достаётся и бросается
    кнопкой «Бомба», как обычная бомба, летит без самонаводки и
    раскрывается при касании пола или врага (или через 1.4 с в воздухе):
    паутина из нитей ловит врагов (валит с ног и стягивает к центру), а
    через 1.6 с взрываются 4 липкие мини-бомбы на её углах. Заряд делает
    их взрывы шире.

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
from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, Sequence

    from bascenev1lib.actor.bomb import Blast

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
TENTACLE_PULL = 90.0  # Сила, с которой щупальце подтягивает врага.
NET_RADIUS = 2.5  # Радиус раскрытой сети (метров).
NET_HOLD = 1.6  # Сколько сеть держит, пока не рванут мини-бомбы (сек).
NET_PULL = 220.0  # Как сильно сеть стягивает пойманных к центру.
NET_MAX = 3  # Сколько сетей можно носить.
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

_NET_COLOR = (0.55, 1.0, 0.45)


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
    _snd('super_punch', 1.0, ppos)
    _snd('swip2', 1.0, ppos)
    if target is not None:
        _snd('activate_beep', 0.8, target.position)

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


# ------------------------------- Models -----------------------------------
# Tentacles and nets are built from small slime "beads": prop nodes that
# collide with nothing and are placed by hand every tick.


class _ModelFactory:
    """Per-activity media and materials for bead models and nets."""

    _STORENAME = 'bsm_model_factory'

    def __init__(self) -> None:
        shared = SharedObjects.get()
        self.bead_mesh = _classicassets.meshes.bomb_sticky.get()
        self.bundle_mesh = _classicassets.meshes.shrapnel_slime.get()
        self.slime_tex = _classicassets.textures.bomb_sticky_color.get()
        self.ghost = bs.Material()
        self.ghost.add_actions(
            actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False),
            )
        )
        # Thrown net touching the floor or a fighter.
        self.net = bs.Material()
        self.net.add_actions(
            conditions=(
                ('they_have_material', shared.player_material),
                'or',
                ('they_have_material', shared.footing_material),
            ),
            actions=('message', 'our_node', 'at_connect', _NetTouchMessage()),
        )

    @classmethod
    def get(cls) -> _ModelFactory:
        activity = bs.getactivity()
        factory = activity.customdata.get(cls._STORENAME)
        if factory is None:
            factory = cls()
            activity.customdata[cls._STORENAME] = factory
        return factory


# Falls back to particle strands if the game won't let us move props.
_MODELS_OK = [True]


def _bead(pos: Sequence[float], scale: float,
          owner: bs.Node | None = None) -> bs.Node | None:
    if not _MODELS_OK[0]:
        return None
    factory = _ModelFactory.get()
    return bs.newnode(
        'prop',
        owner=owner,
        attrs={
            'position': pos,
            'velocity': (0.0, 0.0, 0.0),
            'body': 'sphere',
            'body_scale': 0.1,
            'mesh': factory.bead_mesh,
            'mesh_scale': scale,
            'color_texture': factory.slime_tex,
            'shadow_size': 0.0,
            'reflection': 'soft',
            'reflection_scale': [0.4],
            'materials': (factory.ghost,),
        },
    )


def _place(node: bs.Node | None, pos: Sequence[float]) -> None:
    if node is None or not node or not _MODELS_OK[0]:
        return
    try:
        node.position = pos
        node.velocity = (0.0, 0.0, 0.0)
    except Exception:
        _MODELS_OK[0] = False


def _strand(start: Sequence[float], end: Sequence[float],
            points: int) -> None:
    """Particle strand (fallback when bead models aren't available)."""
    for i in range(1, points + 1):
        frac = i / (points + 1)
        bs.emitfx(position=tuple(start[k] + (end[k] - start[k]) * frac
                                 for k in range(3)),
                  velocity=(0, 0, 0), count=1, scale=0.3, spread=0.0,
                  chunk_type='slime')


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
        if dist <= TENTACLE_RANGE:
            found.append(node)
    return found


def _tentacle_curve(base: Sequence[float], tip: Sequence[float],
                    phase: float, amp: float) -> list[tuple]:
    """Points along a wriggling tentacle from base to tip."""
    vec = [b - a for a, b in zip(base, tip)]
    side, slen = _norm((-vec[2], 0.0, vec[0]))
    if slen < 1e-4:
        side = (1.0, 0.0, 0.0)
    pts = []
    for i in range(_SEGMENTS):
        frac = (i + 1) / _SEGMENTS
        bend = math.sin(frac * math.pi)  # Pinned at both ends.
        wave = math.sin(phase + frac * 5.0) * amp * bend
        lift = math.cos(phase * 0.7 + frac * 4.0) * amp * 0.5 * bend
        pts.append(tuple(base[k] + vec[k] * frac + side[k] * wave
                         + (lift if k == 1 else 0.0) for k in range(3)))
    return pts


def _stop_tentacle(bomb: Bomb) -> None:
    bomb._bst_tentacle_timer = None  # type: ignore[attr-defined]
    for tent in getattr(bomb, '_bst_tentacles', []):
        for bead in tent:
            if bead:
                bead.delete()
    bomb._bst_tentacles = []  # type: ignore[attr-defined]


def _start_tentacle(bomb: Bomb) -> None:
    """Thrown charged sticky bomb: writhing tentacles that grab every enemy
    in reach and reel them in."""
    bnode = bomb.node
    if not bnode or getattr(bomb, '_exploded', False):
        return
    _stop_tentacle(bomb)
    start = bnode.position

    def _new_tentacle() -> list:
        # Thick at the root, thin at the tip.
        return [_bead(bnode.position, 0.42 - 0.26 * i / (_SEGMENTS - 1),
                      owner=bnode) for i in range(_SEGMENTS)]

    bomb._bst_tentacles = [  # type: ignore[attr-defined]
        _new_tentacle() for _ in range(_TENTACLES)
    ]
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
        tentacles = bomb._bst_tentacles
        while len(tentacles) < len(victims):  # One tentacle per victim.
            tentacles.append(_new_tentacle())

        # Pose the tentacles: every one holds a victim (spare ones double
        # up), or they all feel around while nobody is caught.
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
            pts = _tentacle_curve(bpos, tip, tnow * 10.0 + k * 2.0, amp)
            if _MODELS_OK[0]:
                for bead, pos in zip(tent, pts):
                    _place(bead, pos)
            elif victims and int(tnow / _TICK) % 2 == 0:
                for pos in pts:
                    bs.emitfx(position=pos, velocity=(0, 0, 0), count=1,
                              scale=0.35, spread=0.0, chunk_type='slime')

        # Reel in everyone not yet stuck to the bomb.
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
                pull[0], pull[1] + 0.15, pull[2],
            )

    bomb._bst_tentacle_timer = bs.Timer(  # type: ignore[attr-defined]
        _TICK, _step, repeat=True
    )


# ------------------------------ Charged net -------------------------------


class _NetTouchMessage:
    """A thrown net touched the floor or a fighter."""


def _update_counter(spaz: Spaz) -> None:
    """Nets show in the counter over the head (mines once out of nets)."""
    node = spaz.node
    if not node:
        return
    if spaz._bst_nets > 0:
        node.counter_text = f'x{spaz._bst_nets}'
        node.counter_texture = _classicassets.textures.powerup_sticky_bombs.get()
    else:
        _orig_set_land_mine_count(spaz, spaz.land_mine_count)


def _wrap_into_net(spaz: Spaz, bomb: Bomb) -> None:
    """Charged punch on our sticky bomb: it folds up into a throwable net."""
    charge = _bomb_charge(bomb) or Spaz.bsm_take_charge(spaz)
    bpos = bomb.node.position
    bomb.handlemessage(bs.DieMessage())  # Consumed, never goes off.
    spaz._bst_nets = min(NET_MAX, spaz._bst_nets + 1)
    spaz._bst_net_charge += charge
    _update_counter(spaz)

    bs.emitfx(position=bpos, velocity=(0, 3, 0), count=20, scale=0.7,
              spread=0.4, chunk_type='slime')
    _flash(bpos, _NET_COLOR, 0.8, 1.2, 1.5, 0.25)
    _snd('sticky_impact', 1.0, bpos)
    _snd('splatter', 0.8, bpos)
    _snd('powerup01', 0.7, bpos)
    _popup_text('СЕТЬ!', spaz.node.position, _NET_COLOR)


class NetBundle(bs.Actor):
    """A folded net with four weights; held and thrown like a bomb."""

    def __init__(self, spaz: Spaz, charge: float):
        super().__init__()
        factory = _ModelFactory.get()
        node = spaz.node
        self.owner = node
        self._owner_ref = weakref.ref(spaz)
        self._source_player = spaz.source_player
        self.charge = charge
        self.thrown = False
        self.deployed = False
        self._flight = 0.0
        self._time = 0.0
        pos = node.position_forward
        self.node = bs.newnode(
            'prop',
            delegate=self,
            attrs={
                'position': pos,
                'velocity': node.velocity,
                'body': 'sphere',
                'body_scale': 1.0,  # Weighs (and throws) like a bomb.
                'mesh': factory.bundle_mesh,
                'mesh_scale': 1.1,
                'color_texture': factory.slime_tex,
                'shadow_size': 0.3,
                'reflection': 'soft',
                'reflection_scale': [0.4],
                'materials': (SharedObjects.get().object_material,
                              factory.net),
            },
        )
        bs.animate(self.node, 'mesh_scale', {0: 0.0, 0.15: 1.3, 0.25: 1.1})
        # Wound-up strands around the core and four dangling weights.
        self._strands = [_bead(pos, 0.16, owner=self.node) for _ in range(6)]
        self._weights = [_bead(pos, 0.24, owner=self.node) for _ in range(4)]
        self._timer = bs.Timer(_TICK, bs.WeakCallStrict(self._step),
                               repeat=True)

    def get_source_player(self, playertype: Any) -> Any:
        player = self._source_player
        if (player is not None and player.exists()
                and isinstance(player, playertype)):
            return player
        return None

    def _step(self) -> None:
        if not self.node or self.deployed:
            return
        self._time += _TICK
        pos = self.node.position
        spin = self._time * 3.0
        for i, bead in enumerate(self._strands):
            ang = spin + i * math.pi / 3
            _place(bead, (pos[0] + math.cos(ang) * 0.28,
                          pos[1] + 0.12 * math.sin(spin * 1.5 + i),
                          pos[2] + math.sin(ang) * 0.28))
        for i, bead in enumerate(self._weights):
            ang = -spin * 0.6 + i * math.pi / 2
            _place(bead, (pos[0] + math.cos(ang) * 0.45,
                          pos[1] - 0.15 + 0.05 * math.sin(spin * 2 + i),
                          pos[2] + math.sin(ang) * 0.45))
        if self.thrown:
            self._flight += _TICK
            if self._flight > 1.4:
                self.deploy()  # Opens in mid-air too (Happy Thoughts).

    def deploy(self) -> None:
        if self.deployed or not self.node:
            return
        self.deployed = True
        self._timer = None
        center = self.node.position
        vel = self.node.velocity
        spaz = self._owner_ref()
        source = self.get_source_player(bs.Player)
        owner = self.owner
        self.node.delete()
        _open_net(center, vel, spaz, owner, source, self.charge)

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.DroppedMessage):
            self.thrown = True
            self._flight = 0.0
            _snd('swip2', 0.8, self.node.position if self.node else None)
        elif isinstance(msg, bs.PickedUpMessage):
            self.thrown = False
        elif isinstance(msg, _NetTouchMessage):
            if self.thrown:
                try:
                    other = bs.getcollision().opposingnode
                except bs.NotFoundError:
                    other = None
                if other is None or other != self.owner:
                    self.deploy()
        elif isinstance(msg, bs.HitMessage):
            if self.thrown:
                self.deploy()
        elif isinstance(msg, bs.OutOfBoundsMessage):
            self.handlemessage(bs.DieMessage())
        elif isinstance(msg, bs.DieMessage):
            self._timer = None
            if self.node:
                self.node.delete()
        else:
            return super().handlemessage(msg)
        return None


def _draw_net_in_hand(spaz: Spaz) -> NetBundle:
    """The bomb button pulls out a net instead of a bomb."""
    spaz._bst_nets -= 1
    charge, spaz._bst_net_charge = spaz._bst_net_charge, 0.0
    _update_counter(spaz)
    net = NetBundle(spaz, charge).autoretain()
    spaz._pick_up(net.node)
    _snd('sticky_impact', 0.6, net.node.position)
    return net


def _open_net(center: Sequence[float], vel: Sequence[float],
              owner_spaz: Spaz | None, owner_node: bs.Node | None,
              source: Any, charge: float) -> None:
    """The net bursts open: a web of strands catches enemies, then the
    corner weights (mini sticky bombs) go off."""
    radius = NET_RADIUS
    yaw = math.atan2(vel[2], vel[0]) if abs(vel[0]) + abs(vel[2]) > 0.1 else 0

    def _at(ang: float, dist: float, lift: float = 0.0) -> tuple:
        return (center[0] + math.cos(ang) * dist, center[1] + 0.1 + lift,
                center[2] + math.sin(ang) * dist)

    # The web: 8 spokes, a middle ring and the rim, all slime strands.
    layout: list[tuple[float, float]] = []  # (angle, distance)
    for i in range(8):
        for frac in (0.3, 0.55, 0.8):
            layout.append((yaw + i * math.pi / 4, radius * frac))
    for i in range(8):
        layout.append((yaw + math.pi / 8 + i * math.pi / 4, radius * 0.55))
    for i in range(16):
        layout.append((yaw + i * math.pi / 8, radius * 0.97))
    beads = [_bead(center, 0.14) for _ in layout]

    floor = bs.newnode(
        'locator',
        attrs={
            'shape': 'circle',
            'position': center,
            'color': _NET_COLOR,
            'opacity': 0.12,
            'draw_beauty': False,
            'additive': True,
        },
    )
    bs.animate_array(floor, 'size', 1, {0: [0.1], 0.25: [radius * 2.0]})

    # Burst open.
    bs.emitfx(position=center, velocity=(0, 4, 0), count=30, scale=0.8,
              spread=0.6, chunk_type='slime')
    bs.emitfx(position=center, emit_type='distortion',
              spread=0.8 * FX_STRENGTH)
    _snd('splatter', 1.0, center)
    _snd('sticky_impact', 1.0, center)
    _snd('swip2', 0.8, center)
    _snd('cork_pop', 1.0, center)

    # The four weights: mini sticky bombs at the corners (on the spokes).
    blast = 1.3 + min(1.0, charge / 1000.0)  # Charge widens them.
    corners = [_at(yaw + math.pi / 4 + i * math.pi / 2, radius * 0.97, 0.2)
               for i in range(4)]
    minis = [
        Bomb(
            position=cpos,
            velocity=(0.0, -1.0, 0.0),
            bomb_type='sticky',
            blast_radius=blast,
            bomb_scale=0.55,
            source_player=source,
            owner=owner_node,
        ).autoretain()
        for cpos in corners
    ]

    caught: set = set()
    state = {'time': 0.0}

    def _is_target(node: bs.Node) -> bool:
        other = node.getdelegate(Spaz)
        if other is None or not other.is_alive() or node == owner_node:
            return False
        if owner_spaz is not None:
            return _is_enemy(owner_spaz, other)
        return True

    def _step() -> None:
        state['time'] += _TICK
        tnow = state['time']
        # Unfold with a little overshoot, then ripple while it holds.
        unfold = min(1.0, tnow / 0.25)
        spread = 1.0 - (1.0 - unfold) ** 3
        if unfold < 1.0:
            spread *= 1.0 + 0.08 * math.sin(unfold * math.pi)
        if _MODELS_OK[0]:
            for bead, (ang, dist) in zip(beads, layout):
                ripple = 0.06 * math.sin(tnow * 8.0 - dist * 3.0)
                _place(bead, _at(ang, dist * spread, ripple))
        elif int(tnow / _TICK) % 6 == 0:
            for i in range(4):
                _strand(center, corners[i], 3)
                _strand(corners[i], corners[(i + 1) % 4], 3)

        # Every 0.1 s: catch anyone inside (walking in too), reel them in.
        if int(tnow / _TICK) % 3 == 0:
            for node in bs.getnodes():
                if (not node or node.getnodetype() != 'spaz'
                        or not _is_target(node)):
                    continue
                tpos = node.position_center
                dx, dz = center[0] - tpos[0], center[2] - tpos[2]
                if (math.hypot(dx, dz) > radius * spread
                        or abs(tpos[1] - center[1]) > 1.6):
                    continue
                pull, _ = _norm((dx, center[1] - tpos[1], dz))
                if node not in caught:
                    caught.add(node)
                    left = max(0.2, NET_HOLD - tnow)
                    node.handlemessage('knockout', left * 1000.0)
                    bs.emitfx(position=tpos, velocity=(0, 2, 0), count=12,
                              scale=0.6, spread=0.3, chunk_type='slime')
                    _snd('sticky_impact', 1.0, tpos)
                    _snd('splatter', 0.6, tpos)
                node.handlemessage(
                    'impulse', tpos[0], tpos[1], tpos[2], 0.0, 0.0, 0.0,
                    NET_PULL, NET_PULL * 0.08, 0.0, 0,
                    pull[0], pull[1] + 0.1, pull[2],
                )
        if tnow >= NET_HOLD:
            _finish()

    def _finish() -> None:
        holder['timer'] = None
        for i, mini in enumerate(minis):
            bs.timer(0.06 * i,
                     bs.WeakCallStrict(mini.handlemessage, ExplodeMessage()))
        for bead in beads:
            if bead:
                bs.animate(bead, 'mesh_scale', {0: 0.14, 0.2: 0.0})
                bs.timer(0.22, bead.delete)
        if floor:
            bs.animate(floor, 'opacity', {0: 0.12, 0.2: 0.0})
            bs.timer(0.25, floor.delete)

    holder = {'timer': bs.Timer(_TICK, _step, repeat=True)}
    _NET_WEBS.append(holder)

    def _forget() -> None:
        if holder in _NET_WEBS:
            _NET_WEBS.remove(holder)

    bs.timer(NET_HOLD + 0.5, _forget)


# Open nets' timers (nothing else in the game holds on to them).
_NET_WEBS: list[dict] = []


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
    _snd('freeze', 1.0, pos)
    _snd('impact_hard2', 0.7, pos)


# --------------------------- Thrown ice bomb ------------------------------


def _ice_burst(thrower: bs.Node | None, bomb: Bomb, blast: Blast) -> None:
    """Our charged ice bomb blew up: a spray of mini ice bombs."""
    if not blast.node:
        return
    pos = blast.node.position
    source = bomb.get_source_player(bs.Player)
    _snd('cork_pop', 1.0, pos)
    _snd('orchestra_hit2', 0.7, pos)
    base = random.uniform(0, 2 * math.pi)
    for i in range(ICE_MINI_BOMBS):
        ang = base + 2 * math.pi * i / max(1, ICE_MINI_BOMBS)
        mini = Bomb(
            position=(pos[0], pos[1] + 0.4, pos[2]),
            velocity=(math.cos(ang) * 6.0, 6.0, math.sin(ang) * 6.0),
            bomb_type='ice',
            blast_radius=1.0,
            bomb_scale=0.55,
            source_player=source,
            owner=thrower,
        ).autoretain()
        bs.timer(ICE_MINI_DELAY + ICE_MINI_STAGGER * i,
                 bs.WeakCallStrict(mini.handlemessage, ExplodeMessage()))


# ------------------------------- Patches ----------------------------------


def _patched_init(self: Spaz, *args: Any, **kwargs: Any) -> None:
    _orig_init(self, *args, **kwargs)
    self._bst_ice_until = 0.0
    self._bst_ice_nodes: list[bs.Node] = []
    self._bst_ice_timer: bs.Timer | None = None
    self._bst_ice_fx_timer: bs.Timer | None = None
    self._bst_old_highlight: Any = None
    self._bst_nets = 0
    self._bst_net_charge = 0.0


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
                _wrap_into_net(self, bomb)
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
    if getattr(self, '_bst_nets', 0) > 0 and self.node and not self.frozen:
        _draw_net_in_hand(self)
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
    if getattr(self, '_bst_nets', 0) > 0:
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
