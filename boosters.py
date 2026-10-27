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
  * брошенная заряженная липкая бомба, как только рядом (до 5 м) окажется
    враг, выстреливает в него щупальцем из слизи и подтягивает к себе,
    пока он не прилипнет;
  * удар кулаком по своей липкой бомбе — она сворачивается в сеть (1 шт.).
    Сеть достаётся и бросается кнопкой «Бомба», как обычная бомба, летит
    без самонаводки и раскрывается при касании пола или врага (или через
    1.4 с в воздухе): большая паутина ловит врагов (валит с ног и стягивает
    к центру), а через 1.6 с взрываются 4 липкие мини-бомбы на её углах.
    Заряд делает их взрывы шире.

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
from bascenev1lib.actor.bomb import (
    Bomb,
    BombFactory,
    ExplodeMessage,
    SplatMessage,
)
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
ICE_MINI_DELAY = 0.7  # Через сколько после основной взрывается первая...
ICE_MINI_STAGGER = 0.2  # ...и с каким шагом остальные (сек).
TENTACLE_RANGE = 5.0  # Дальность щупальца заряженной липкой бомбы (метров).
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
                  count=2, scale=0.5, spread=0.1, chunk_type='spark')

    # Kept on the bomb (which the game keeps alive) so it can't be
    # garbage-collected mid-flight.
    bomb._bst_flight = bs.Timer(  # type: ignore[attr-defined]
        _TICK, _step, repeat=True
    )
    _step()


# -------------------------- Sticky bomb + charge --------------------------


def _find_tentacle_target(spaz: Spaz, origin: Sequence[float]) -> Any:
    best = None
    for node in bs.getnodes():
        if not node or node.getnodetype() != 'spaz':
            continue
        other = node.getdelegate(Spaz)
        if other is None or not other.is_alive() or not _is_enemy(spaz, other):
            continue
        _, dist = _norm([a - b for a, b in zip(node.position_center, origin)])
        if dist <= TENTACLE_RANGE and (best is None or dist < best[0]):
            best = (dist, node)
    return best[1] if best else None


def _start_tentacle(bomb: Bomb) -> None:
    """Thrown charged sticky bomb: lash an enemy and reel them in."""
    bnode = bomb.node
    if not bnode or getattr(bomb, '_exploded', False):
        return
    state: dict[str, Any] = {'time': 0.0, 'target': None, 'latched': 0.0}

    def _stop() -> None:
        bomb._bst_tentacle_timer = None  # type: ignore[attr-defined]

    def _draw(bpos: Sequence[float], tpos: Sequence[float]) -> None:
        """A wriggling rope of slime from the bomb to the victim."""
        vec = [b - a for a, b in zip(bpos, tpos)]
        side, slen = _norm((-vec[2], 0.0, vec[0]))
        if slen < 1e-4:
            side = (1.0, 0.0, 0.0)
        segments = 7
        phase = state['time'] * 14.0
        for i in range(1, segments):
            frac = i / segments
            # Wave strongest mid-way, pinned at both ends.
            wiggle = math.sin(phase + frac * 6.0) * 0.25 * math.sin(
                frac * math.pi
            )
            pos = tuple(bpos[k] + vec[k] * frac + side[k] * wiggle
                        for k in range(3))
            bs.emitfx(position=pos, velocity=(0, 0, 0), count=1, scale=0.35,
                      spread=0.0, chunk_type='slime')

    def _step() -> None:
        state['time'] += _TICK
        spaz = bomb._bst_tentacle_owner()
        if spaz is None or not bnode or getattr(bomb, '_exploded', False):
            _stop()
            return
        bpos = bnode.position
        target = state['target']
        victim = target.getdelegate(Spaz) if target else None
        if victim is None or not victim.is_alive():
            if state['latched']:
                _stop()  # Our catch is gone; one lash per bomb.
                return
            target = _find_tentacle_target(spaz, bpos)
            if target is None:
                return
            state['target'] = target
            state['latched'] = state['time']
            _snd('sticky_impact', 1.0, bpos)
            _snd('splatter', 0.8, target.position)
            _snd('swip', 0.8, bpos)
            bs.emitfx(position=target.position_center, velocity=(0, 2, 0),
                      count=12, scale=0.6, spread=0.3, chunk_type='slime')
        tpos = target.position_center
        pull, dist = _norm([a - b for a, b in zip(bpos, tpos)])
        if dist < 0.9:
            _stop()  # Reeled in: the bomb's own stickiness does the rest.
            _snd('sticky_impact', 1.0, bpos)
            return
        target.handlemessage(
            'impulse', tpos[0], tpos[1], tpos[2], 0.0, 0.0, 0.0,
            TENTACLE_PULL, TENTACLE_PULL * 0.08, 0.0, 0,
            pull[0], pull[1] + 0.15, pull[2],
        )
        if int(state['time'] / _TICK) % 2 == 0:
            _draw(bpos, tpos)

    bomb._bst_tentacle_timer = bs.Timer(  # type: ignore[attr-defined]
        _TICK, _step, repeat=True
    )


# ------------------------------ Charged net -------------------------------


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


def _draw_net_in_hand(spaz: Spaz) -> Bomb:
    """The bomb button pulls out a net instead of a bomb."""
    node = spaz.node
    spaz._bst_nets -= 1
    charge, spaz._bst_net_charge = spaz._bst_net_charge, 0.0
    _update_counter(spaz)

    pos = node.position_forward
    net = Bomb(
        position=(pos[0], pos[1], pos[2]),
        velocity=node.velocity,
        bomb_type='sticky',
        bomb_scale=0.9,
        source_player=spaz.source_player,
        owner=node,
    ).autoretain()
    net._bst_net = {  # type: ignore[attr-defined]
        'owner': weakref.ref(spaz),
        'charge': charge,
        'deployed': False,
        'thrown': False,
    }
    bnode = net.node
    light = bs.newnode(
        'light',
        owner=bnode,
        attrs={
            'color': _NET_COLOR,
            'radius': 0.15,
            'height_attenuated': False,
            'volume_intensity_scale': 0.3,
        },
    )
    bnode.connectattr('position', light, 'position')
    bs.animate(light, 'intensity', {0: 0.3, 0.4: 0.8, 0.8: 0.3}, loop=True)

    def _drip() -> None:
        if bnode:
            bs.emitfx(position=bnode.position, velocity=(0, -1, 0), count=1,
                      scale=0.4, spread=0.05, chunk_type='slime')

    net._bst_drip = bs.Timer(0.2, _drip, repeat=True)  # type: ignore
    spaz._pick_up(bnode)
    _snd('sticky_impact', 0.6, pos)
    return net


def _net_thrown(net: Bomb) -> None:
    """Fly freely; open on touching floor/fighter, or after a while."""
    info = net._bst_net  # type: ignore[attr-defined]
    info['thrown'] = True
    bnode = net.node
    state = {'time': 0.0}

    def _step() -> None:
        state['time'] += _TICK
        if not bnode or info['deployed']:
            net._bst_net_timer = None  # type: ignore[attr-defined]
            return
        if state['time'] > 1.4:
            _deploy_net(net)

    net._bst_net_timer = bs.Timer(  # type: ignore[attr-defined]
        _TICK, _step, repeat=True
    )


def _strand(start: Sequence[float], end: Sequence[float],
            points: int) -> None:
    """A strand of slime from start to end."""
    for i in range(1, points + 1):
        frac = i / (points + 1)
        bs.emitfx(position=tuple(start[k] + (end[k] - start[k]) * frac
                                 for k in range(3)),
                  velocity=(0, 0, 0), count=1, scale=0.3, spread=0.0,
                  chunk_type='slime')


def _deploy_net(net: Bomb) -> None:
    """The net bursts open: catches enemies, then its corner bombs go off."""
    info = net._bst_net  # type: ignore[attr-defined]
    if info['deployed'] or not net.node:
        return
    info['deployed'] = True
    net._bst_net_timer = None  # type: ignore[attr-defined]
    net._bst_drip = None  # type: ignore[attr-defined]
    center = net.node.position
    vel = net.node.velocity
    net.handlemessage(bs.DieMessage())

    owner_spaz = info['owner']()
    owner_node = net.owner
    source = net.get_source_player(bs.Player)
    radius = NET_RADIUS

    # Burst open: splat, then web rings flung out from the middle.
    bs.emitfx(position=center, velocity=(0, 4, 0), count=30, scale=0.8,
              spread=0.6, chunk_type='slime')
    bs.emitfx(position=center, emit_type='distortion',
              spread=0.8 * FX_STRENGTH)
    _snd('splatter', 1.0, center)
    _snd('sticky_impact', 1.0, center)
    _snd('swip2', 0.8, center)
    web: list[bs.Node] = []
    for frac, delay in ((1.0, 0.0), (0.66, 0.04), (0.33, 0.08)):
        ring = bs.newnode(
            'locator',
            attrs={
                'shape': 'circleOutline',
                'position': center,
                'color': _NET_COLOR,
                'opacity': 0.55,
                'draw_beauty': False,
                'additive': True,
            },
        )
        size = radius * 2.0 * frac
        bs.animate_array(ring, 'size', 1,
                         {0: [0.1], delay: [0.1], delay + 0.18: [size * 1.08],
                          delay + 0.26: [size]})
        web.append(ring)
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
    bs.animate_array(floor, 'size', 1, {0: [0.1], 0.2: [radius * 2.0]})
    web.append(floor)

    # Four weighted corners: mini sticky bombs, square to the throw.
    yaw = math.atan2(vel[2], vel[0]) if abs(vel[0]) + abs(vel[2]) > 0.1 else 0
    corners = []
    minis = []
    blast = 1.3 + min(1.0, info['charge'] / 1000.0)  # Charge widens them.
    for i in range(4):
        ang = yaw + math.pi / 4 + i * math.pi / 2
        cpos = (center[0] + math.cos(ang) * radius * 0.85, center[1] + 0.3,
                center[2] + math.sin(ang) * radius * 0.85)
        corners.append(cpos)
        _strand(center, cpos, 4)  # Flung out along a strand.
        minis.append(
            Bomb(
                position=cpos,
                velocity=(0.0, -1.0, 0.0),
                bomb_type='sticky',
                blast_radius=blast,
                bomb_scale=0.55,
                source_player=source,
                owner=owner_node,
            ).autoretain()
        )
    _snd('cork_pop', 1.0, center)

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
        state['time'] += 0.1
        # Shimmering web: spokes and the edge between the corner bombs.
        tick = int(state['time'] * 10 + 0.5)
        if tick % 2 == 0:
            for i in range(4):
                _strand(center, corners[i], 3)
                _strand(corners[i], corners[(i + 1) % 4], 3)
        for ring in web:
            if ring:
                ring.opacity = (0.12 if ring is floor else
                                0.4 + 0.15 * math.sin(state['time'] * 9.0))
        # Catch anyone inside (also those walking in) and reel them in.
        for node in bs.getnodes():
            if not node or node.getnodetype() != 'spaz' or not _is_target(
                node
            ):
                continue
            tpos = node.position_center
            dx, dz = center[0] - tpos[0], center[2] - tpos[2]
            if math.hypot(dx, dz) > radius or abs(tpos[1] - center[1]) > 1.6:
                continue
            pull, _ = _norm((dx, center[1] - tpos[1], dz))
            if node not in caught:
                caught.add(node)
                left = max(0.2, NET_HOLD - state['time'])
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
        if state['time'] >= NET_HOLD:
            _finish()

    def _finish() -> None:
        holder['timer'] = None
        net._bst_net_web = None  # type: ignore[attr-defined]
        for i, mini in enumerate(minis):
            bs.timer(0.06 * i,
                     bs.WeakCallStrict(mini.handlemessage, ExplodeMessage()))
        for ring in web:
            if ring:
                bs.animate(ring, 'opacity', {0: ring.opacity, 0.2: 0.0})
                bs.timer(0.25, ring.delete)

    # Kept on the (dead) net actor, which our closures keep alive.
    holder = {'timer': bs.Timer(0.1, _step, repeat=True)}
    net._bst_net_web = holder  # type: ignore[attr-defined]
    _NET_WEBS.append(holder)

    def _forget() -> None:
        if holder in _NET_WEBS:
            _NET_WEBS.remove(holder)

    bs.timer(NET_HOLD + 0.5, _forget)


# Open nets' timers (their bomb actor is gone once the net bursts open).
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
            and not hasattr(bomb, '_bst_net')
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
    info = getattr(self, '_bst_net', None)
    if info is not None and not info['deployed']:
        if isinstance(msg, ExplodeMessage):
            # A net never explodes; once thrown, a blast just opens it.
            if info['thrown']:
                _deploy_net(self)
            return None
        if isinstance(msg, bs.DroppedMessage):
            _net_thrown(self)
        elif isinstance(msg, bs.PickedUpMessage):
            info['thrown'] = False
            self._bst_net_timer = None  # type: ignore[attr-defined]
        elif isinstance(msg, SplatMessage) and info['thrown']:
            try:
                other = bs.getcollision().opposingnode
            except bs.NotFoundError:
                other = None
            if other is not None and other == self.owner:
                return None  # Brushing past the thrower doesn't count.
            _deploy_net(self)
            return None
    result = _orig_bomb_handlemessage(self, msg)
    if getattr(self, '_bst_tentacle_owner', None) is not None:
        if isinstance(msg, bs.DroppedMessage):
            _start_tentacle(self)
        elif isinstance(msg, bs.PickedUpMessage):
            self._bst_tentacle_timer = None  # type: ignore[attr-defined]
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
