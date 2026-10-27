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
    волне щита (в 1.7 раза шире обычного взрыва) разбрасывает 3 ледяные
    мини-бомбы, которые взрываются почти сразу после основной.

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

# ------------------------------- Настройки --------------------------------

IMPACT_SPEED = 22.0  # Скорость ударной бомбы после удара (м/с).
IMPACT_FLIGHT_TIME = 4.0  # Сколько она ищет путь к врагу, потом взрывается.
IMPACT_RANGE = 25.0  # Дальность поиска врага для неё (метров).
IMPACT_ANGLE = 45.0  # Насколько враг может быть в стороне от удара (градусов).
ICE_FISTS_TIME = 8.0  # Ледяные кулаки: базовая длительность (сек)...
ICE_FISTS_PER_CHARGE = 0.01  # ...плюс секунд за каждую единицу заряда...
ICE_FISTS_MAX_TIME = 20.0  # ...но не дольше этого.
ICE_FISTS_FREEZE = 3.0  # На сколько секунд замораживает удар ледяным кулаком.
ICE_MINI_BOMBS = 3  # Сколько мини-бомб разбрасывает заряженная ледяная.
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
        vec = [want[i] * 0.25 + side[i] * 0.8 * horiz for i in range(3)]
        vec[1] += 0.9 * vert
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
    _flash(ppos, hot, 1.2, 2.0, 3.0, 0.25)
    _ring(ppos, hot, 3.0, 0.25)
    bs.emitfx(position=ppos, emit_type='distortion', spread=1.0 * FX_STRENGTH)
    bs.emitfx(position=ppos,
              velocity=(direction[0] * 14.0, direction[1] * 14.0 + 1.0,
                        direction[2] * 14.0),
              count=35, scale=0.9, spread=0.15, chunk_type='spark')
    _shake(1.5)
    _snd('super_punch', 1.0, ppos)
    _snd('laser_reverse', 0.9, ppos)
    _snd('swip2', 1.0, ppos)
    _snd('orchestra_hit_big2', 0.7, ppos)
    if target is not None:
        _snd('activate_beep', 0.8, target.position)

    state: dict[str, Any] = {
        'time': 0.0,
        'dir': direction,
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
        tnow = state['time']
        if not bnode or getattr(bomb, '_exploded', False):
            _stop()
            return
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
            want, dist = _norm(
                [a - b for a, b in zip(target.position_center, bpos)]
            )
            if dist < 0.9 + IMPACT_SPEED * _TICK:
                _stop()
                _snd('big_impact', 1.0, bpos)
                bomb.handlemessage(ExplodeMessage())  # Goes off on contact.
                return

            # Stuck against something (barely moving, or bumped it)? Try
            # going over, under or around it, a different way each time.
            _, moved = _norm([a - b for a, b in zip(bpos, state['last'])])
            bumped = bs.time() - getattr(bomb, '_bst_bump_time', -9.0) < 0.1
            if tnow > 0.1 and (moved < IMPACT_SPEED * _TICK * 0.35 or bumped):
                state['slow'] += 1
            else:
                state['slow'] = 0
            if state['slow'] >= 2 and tnow >= state['avoid_until']:
                dirs = _avoid_dirs(want)
                state['avoid_dir'] = dirs[state['attempt'] % len(dirs)]
                state['attempt'] += 1
                state['avoid_until'] = tnow + 0.18
                state['slow'] = 0
            fdir = state['avoid_dir'] if tnow < state['avoid_until'] else want
            state['dir'] = fdir

        state['last'] = bpos
        bnode.velocity = tuple(c * IMPACT_SPEED for c in fdir)
        bs.emitfx(position=bpos, velocity=tuple(-c * 2.0 for c in fdir),
                  count=3, scale=0.6, spread=0.1, chunk_type='spark')
        if random.random() < 0.3:
            bs.emitfx(position=bpos, emit_type='distortion',
                      spread=0.4 * FX_STRENGTH)

    # Kept on the bomb (which the game keeps alive) so it can't be
    # garbage-collected mid-flight.
    bomb._bst_flight = bs.Timer(  # type: ignore[attr-defined]
        _TICK, _step, repeat=True
    )
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
        bs.timer(0.35 + 0.1 * i,
                 bs.WeakCallStrict(mini.handlemessage, ExplodeMessage()))


# ------------------------------- Patches ----------------------------------


def _patched_init(self: Spaz, *args: Any, **kwargs: Any) -> None:
    _orig_init(self, *args, **kwargs)
    self._bst_ice_until = 0.0
    self._bst_ice_nodes: list[bs.Node] = []
    self._bst_ice_timer: bs.Timer | None = None
    self._bst_ice_fx_timer: bs.Timer | None = None
    self._bst_old_highlight: Any = None


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
            and bomb.bomb_type in ('impact', 'ice')
            and _is_own_bomb(self, bomb)
            and (_charged(self) or _bomb_charge(bomb) > 0)
        ):
            self._punched_nodes.add(hit)
            if bomb.bomb_type == 'impact':
                _launch_impact_bomb(self, bomb)
            else:
                _absorb_ice_bomb(self, bomb)
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
    # Checked before the call: Absorb Shield may spend the charge inside it.
    charged = _charged(self)
    bomb = _orig_drop_bomb(self)
    if bomb is not None and bomb.bomb_type == 'ice' and charged:
        thrower = self.node
        bomb.add_explode_callback(
            lambda bmb, blast: _ice_burst(thrower, bmb, blast)
        )
    return bomb


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
        global _orig_bomb_handle_impact
        _orig_init = Spaz.__init__
        _orig_handlemessage = Spaz.handlemessage
        _orig_drop_bomb = Spaz.drop_bomb
        _orig_bomb_handle_impact = Bomb._handle_impact

        Spaz.__init__ = _patched_init
        Spaz.handlemessage = _patched_handlemessage
        Spaz.drop_bomb = _patched_drop_bomb
        Bomb._handle_impact = _patched_bomb_handle_impact
