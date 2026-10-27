# ba_meta require api 9
"""BSM Boosters — усилители для BombSquad 1.8.x.

Ракета (новый ящик-бонус, 1 ракета в ящике, ракеты копятся):
  * зажми «Бомба» — цели (противники вокруг) по очереди подсвечиваются
    кольцом и меткой; отпусти в нужный момент — ракета летит в отмеченную
    цель, доворачивая за ней в любом направлении, в том числе вверх и вниз
    (работает и на «Счастливых мыслях», не только на плоских картах);
  * боеголовка берёт тип бомб бойца: ледяные бомбы — ледяная ракета,
    липкие — липкая и т. д.; заряд щита из Absorb Shield тоже уходит в
    ракету (у ледяной — с морозной волной).

Пинок бомбы: удар кулаком по СВОЕЙ активированной бомбе (горит фитиль,
ударная или мина взведены), когда в направлении удара (до 45°) есть
противник, — бомба летит в него с огромной скоростью и бьёт как болванка.
На время взрыва это не влияет: ударная бомба и мина взрываются от касания,
остальные — по своему фитилю. Заряд щита добавляется к удару. Чужие и
неактивные бомбы, как обычно, просто отлетают.

Все усилители складываются друг с другом и с обычными бонусами.
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
from bascenev1lib.actor.bomb import Blast, Bomb, BombFactory, ExplodeMessage
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.powerupbox import PowerupBox, PowerupBoxFactory
from bascenev1lib.actor.spaz import PunchHitMessage, Spaz
from bascenev1lib.gameutils import SharedObjects

if TYPE_CHECKING:
    from typing import Any, Sequence

# ------------------------------- Настройки --------------------------------

ROCKET_FREQ = 2  # Как часто выпадает ящик с ракетой (у обычных бонусов 1–3).
ROCKET_MAX = 5  # Сколько ракет можно носить.
ROCKET_RANGE = 40.0  # Дальность выбора цели (метров).
ROCKET_CYCLE = 0.5  # Как быстро перебираются цели (сек на цель).
ROCKET_SPEED = 18.0  # Скорость ракеты (м/с).
ROCKET_TURN = 5.0  # Как резко ракета доворачивает за целью (рад/с).
ROCKET_LIFETIME = 5.0  # Через сколько секунд ракета взрывается сама.
ROCKET_BLAST_MULT = 1.0  # Радиус взрыва ракеты относительно бомбы бойца.
ROCKETS_FOR_BOTS = False  # Могут ли боты подбирать ракеты.
KICK_RANGE = 18.0  # Дальность пинка бомбы (метров).
KICK_ANGLE = 45.0  # Насколько цель может быть в стороне от удара (градусов).
KICK_SPEED = 30.0  # Скорость пнутой бомбы (м/с).
KICK_DAMAGE = 450.0  # Урон пнутой бомбы (1000 = полное здоровье).
FX_STRENGTH = 0.5  # Сила вспышек, света и тряски камеры (1.0 = максимум).

# --------------------------------------------------------------------------

_TICK = 0.03

# Captured when the plugin switches on (not at import), so plugins that
# patch the same Spaz methods chain instead of overwriting each other.
_orig_init: Any = None
_orig_handlemessage: Any = None
_orig_bomb_press: Any = None
_orig_bomb_release: Any = None
_orig_set_land_mine_count: Any = None
_orig_box_factory_init: Any = None
_orig_box_init: Any = None


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
    flash = bs.newnode(
        'flash',
        attrs={'position': pos, 'size': size * FX_STRENGTH, 'color': color},
    )
    bs.timer(0.08, flash.delete)
    light = bs.newnode(
        'light',
        attrs={
            'position': pos,
            'color': color,
            'radius': light_radius * FX_STRENGTH,
            'height_attenuated': False,
            'volume_intensity_scale': 0.6,
        },
    )
    bs.animate(light, 'intensity', {0: intensity * FX_STRENGTH, duration: 0})
    bs.timer(duration + 0.05, light.delete)


def _sparks(pos: Sequence[float], count: int,
            vel: Sequence[float] = (0.0, 4.0, 0.0), spread: float = 0.6,
            scale: float = 1.0) -> None:
    bs.emitfx(position=pos, velocity=vel, count=count, scale=scale,
              spread=spread, chunk_type='spark')


def _shake(intensity: float) -> None:
    bs.camerashake(intensity * FX_STRENGTH)


def _norm(vec: Sequence[float]) -> tuple[tuple[float, float, float], float]:
    length = math.sqrt(vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2)
    if length < 1e-4:
        return (0.0, 0.0, 0.0), 0.0
    return (vec[0] / length, vec[1] / length, vec[2] / length), length


def _shielded(spaz: Spaz | None) -> bool:
    """Powerup shield or an Absorb Shield parry: no knockback through it."""
    return spaz is not None and (
        spaz.shield is not None or getattr(spaz, '_ab_active', False)
    )


def _knock(target: bs.Node, pos: Sequence[float], fdir: Sequence[float],
           power: float) -> None:
    """Shove a node; power ~ amount of damage dealt."""
    if target.getnodetype() not in ('spaz', 'prop', 'bomb'):
        return
    k = max(0.4, min(3.0, power / 500.0))
    target.handlemessage(
        'impulse', pos[0], pos[1], pos[2], 0.0, 0.0, 0.0,
        700.0 * k, 60.0 * k, 0.0, 0,
        fdir[0], fdir[1] + 0.3, fdir[2],
    )


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


def _enemies(spaz: Spaz, origin: Sequence[float],
             max_range: float) -> list[tuple[float, bs.Node]]:
    """Living enemies around a point as (distance, node), nearest first."""
    found = []
    for node in bs.getnodes():
        if not node or node.getnodetype() != 'spaz':
            continue
        other = node.getdelegate(Spaz)
        if other is None or not other.is_alive() or not _is_enemy(spaz, other):
            continue
        _, dist = _norm([a - b for a, b in zip(node.position_center, origin)])
        if dist <= max_range:
            found.append((dist, node))
    found.sort(key=lambda item: item[0])
    return found


# ------------------------------- Rocket -----------------------------------


class _RocketImpactMessage:
    """The rocket touched the world or something solid."""


class RocketFactory:
    """Per-activity rocket media and materials."""

    _STORENAME = 'bsm_rocket_factory'

    def __init__(self) -> None:
        shared = SharedObjects.get()
        self.mesh = _classicassets.meshes.impact_bomb.get()
        self.tex = _classicassets.textures.impact_bomb_color_lit.get()
        self.box_tex = _classicassets.textures.powerup_speed.get()
        self.fly_sound = _classicassets.audio.fuse01.get()
        self.material = bs.Material()
        self.material.add_actions(
            conditions=(
                ('they_have_material', shared.footing_material),
                'or',
                ('they_have_material', shared.object_material),
            ),
            actions=(
                ('modify_part_collision', 'physical', False),
                ('message', 'our_node', 'at_connect', _RocketImpactMessage()),
            ),
        )

    @classmethod
    def get(cls) -> RocketFactory:
        activity = bs.getactivity()
        factory = activity.customdata.get(cls._STORENAME)
        if factory is None:
            factory = cls()
            activity.customdata[cls._STORENAME] = factory
        return factory


class Rocket(bs.Actor):
    """A homing rocket. Bomb-like, so Absorb Shield can charge it."""

    def __init__(self, spaz: Spaz, position: Sequence[float],
                 direction: Sequence[float], target: bs.Node | None):
        super().__init__()
        factory = RocketFactory.get()
        self.owner = spaz.node
        self._source_player = spaz.source_player
        self._target = target
        self._dir, _ = _norm(direction)
        self._speed = ROCKET_SPEED * 0.45
        self._age = 0.0
        self._exploded = False
        self._explode_callbacks: list[Any] = []
        self._color = _color(spaz)

        # The warhead follows the fighter's bombs: ice, sticky, impact...
        self.bomb_type = (
            spaz.bomb_type
            if spaz.bomb_type in ('normal', 'ice', 'sticky', 'impact')
            else 'normal'
        )
        self.blast_radius = spaz.blast_radius * ROCKET_BLAST_MULT
        if self.bomb_type == 'ice':
            self.blast_radius *= 1.2
        elif self.bomb_type == 'impact':
            self.blast_radius *= 0.7

        self.node = bs.newnode(
            'prop',
            delegate=self,
            attrs={
                'position': position,
                'velocity': tuple(c * self._speed for c in self._dir),
                'body': 'sphere',
                'body_scale': 0.6,
                'mesh': factory.mesh,
                'mesh_scale': 0.75,
                'color_texture': factory.tex,
                'shadow_size': 0.3,
                'reflection': 'powerup',
                'reflection_scale': [1.5],
                'materials': (factory.material,),
            },
        )
        light = bs.newnode(
            'light',
            owner=self.node,
            attrs={
                'color': (1.0, 0.55, 0.2),
                'radius': 0.12,
                'intensity': 0.9,
                'height_attenuated': False,
                'volume_intensity_scale': 0.3,
            },
        )
        self.node.connectattr('position', light, 'position')
        sound = bs.newnode(
            'sound',
            owner=self.node,
            attrs={'sound': factory.fly_sound, 'volume': 0.35},
        )
        self.node.connectattr('position', sound, 'position')
        self._timer = bs.Timer(
            _TICK, bs.WeakCallStrict(self._step), repeat=True
        )

    # Bomb-like interface (used by Absorb Shield's charge).
    def add_explode_callback(self, call: Any) -> None:
        self._explode_callbacks.append(call)

    def get_source_player(self, playertype: Any) -> Any:
        player = self._source_player
        if player is not None and player.exists() and isinstance(
            player, playertype
        ):
            return player
        return None

    def _step(self) -> None:
        if not self.node or self._exploded:
            return
        self._age += _TICK
        if self._age > ROCKET_LIFETIME:
            self.explode()
            return
        self._speed = min(ROCKET_SPEED, self._speed + ROCKET_SPEED * 2 * _TICK)
        pos = self.node.position

        target = self._target
        victim = target.getdelegate(Spaz) if target else None
        if victim is not None and victim.is_alive():
            want, dist = _norm(
                [a - b for a, b in zip(target.position_center, pos)]
            )
            if dist < 0.9 + self._speed * _TICK:
                self.explode()
                return
            # Turn toward the target, limited like a real rocket; works in
            # full 3D (up/down too) for Happy Thoughts flying maps.
            cos = max(-1.0, min(1.0, sum(a * b for a, b in zip(self._dir,
                                                                 want))))
            angle = math.acos(cos)
            max_turn = ROCKET_TURN * _TICK
            if angle <= max_turn:
                self._dir = want
            else:
                frac = max_turn / angle
                self._dir, _ = _norm(
                    [a + (b - a) * frac for a, b in zip(self._dir, want)]
                )
        self.node.velocity = tuple(c * self._speed for c in self._dir)

        # Exhaust.
        back = tuple(p - d * 0.4 for p, d in zip(pos, self._dir))
        bs.emitfx(position=back,
                  velocity=tuple(-d * 3.0 for d in self._dir),
                  count=2, scale=0.5, spread=0.08, chunk_type='spark')
        if random.random() < 0.35:
            bs.emitfx(position=back, count=1, emit_type='tendrils',
                      tendril_type='thin_smoke')

    def explode(self) -> None:
        if self._exploded:
            return
        self._exploded = True
        self._timer = None
        if self.node:
            blast = Blast(
                position=self.node.position,
                velocity=(0.0, 0.0, 0.0),
                blast_radius=self.blast_radius,
                blast_type=self.bomb_type,
                source_player=self.get_source_player(bs.Player),
                hit_type='explosion',
                hit_subtype='normal',
            ).autoretain()
            for call in self._explode_callbacks:
                call(self, blast)
        bs.timer(0.001, bs.WeakCallStrict(self.handlemessage, bs.DieMessage()))

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, _RocketImpactMessage):
            try:
                other = bs.getcollision().opposingnode
            except bs.NotFoundError:
                other = None
            if other is not None and other == self.owner:
                return None  # Never on its own shooter.
            self.explode()
        elif isinstance(msg, bs.HitMessage):
            self.explode()
        elif isinstance(msg, bs.OutOfBoundsMessage):
            self.handlemessage(bs.DieMessage())
        elif isinstance(msg, bs.DieMessage):
            self._timer = None
            if self.node:
                self.node.delete()
        else:
            return super().handlemessage(msg)
        return None


# ------------------------- Rocket aiming & firing -------------------------


def _update_counter(spaz: Spaz) -> None:
    """Show rockets in the counter over the head (mines when out of them)."""
    node = spaz.node
    if not node:
        return
    rockets = getattr(spaz, '_bst_rockets', 0)
    if rockets > 0:
        node.counter_text = f'x{rockets}'
        node.counter_texture = RocketFactory.get().box_tex
    elif spaz.land_mine_count > 0:
        _orig_set_land_mine_count(spaz, spaz.land_mine_count)
    else:
        node.counter_text = ''


def _clear_mark(spaz: Spaz) -> None:
    for node in spaz._bst_marks:
        if node:
            node.delete()
    spaz._bst_marks = []


def _mark(spaz: Spaz, target: bs.Node) -> None:
    """Ring, glow and a tag on the currently selected target."""
    _clear_mark(spaz)
    col = _color(spaz)
    ring = bs.newnode(
        'locator',
        owner=target,
        attrs={
            'shape': 'circleOutline',
            'color': col,
            'opacity': 0.9,
            'draw_beauty': False,
            'additive': True,
        },
    )
    target.connectattr('position', ring, 'position')
    bs.animate_array(ring, 'size', 1, {0: [3.0], 0.15: [1.5]})
    light = bs.newnode(
        'light',
        owner=target,
        attrs={
            'color': col,
            'radius': 0.3,
            'height_attenuated': False,
            'volume_intensity_scale': 0.2,
        },
    )
    target.connectattr('position_center', light, 'position')
    bs.animate(light, 'intensity', {0: 1.2, 0.25: 0.5, 0.5: 1.2}, loop=True)
    mnode = bs.newnode(
        'math',
        owner=target,
        attrs={'input1': (0, 1.3, 0), 'operation': 'add'},
    )
    target.connectattr('torso_position', mnode, 'input2')
    text = bs.newnode(
        'text',
        owner=target,
        attrs={
            'text': '[ ЦЕЛЬ ]',
            'in_world': True,
            'h_align': 'center',
            'shadow': 1.0,
            'flatness': 1.0,
            'color': (col[0], col[1], col[2], 1.0),
            'scale': 0.012,
        },
    )
    mnode.connectattr('output', text, 'position')
    spaz._bst_marks = [ring, light, mnode, text]
    _snd('tick', 0.8, target.position)


def _start_aiming(spaz: Spaz) -> None:
    spaz._bst_aiming = True
    targets = _enemies(spaz, spaz.node.position_center, ROCKET_RANGE)
    spaz._bst_target = targets[0][1] if targets else None
    if spaz._bst_target is not None:
        _mark(spaz, spaz._bst_target)
    _snd('activate_beep', 0.6, spaz.node.position)
    spaz._bst_cycle_timer = bs.Timer(
        ROCKET_CYCLE, _wcall(_next_target, spaz), repeat=True
    )


def _next_target(spaz: Spaz) -> None:
    if not spaz.node or not spaz._bst_aiming:
        return
    targets = [n for _, n in _enemies(spaz, spaz.node.position_center,
                                      ROCKET_RANGE)]
    if not targets:
        spaz._bst_target = None
        _clear_mark(spaz)
        return
    current = spaz._bst_target
    idx = targets.index(current) + 1 if current in targets else 0
    spaz._bst_target = targets[idx % len(targets)]
    _mark(spaz, spaz._bst_target)


def _stop_aiming(spaz: Spaz) -> None:
    spaz._bst_aiming = False
    spaz._bst_cycle_timer = None
    _clear_mark(spaz)


def _fire_rocket(spaz: Spaz) -> None:
    node = spaz.node
    target = spaz._bst_target
    _stop_aiming(spaz)
    if not node or spaz._bst_rockets <= 0:
        return
    victim = target.getdelegate(Spaz) if target else None
    if victim is None or not victim.is_alive():
        target = None

    facing, _ = _norm([a - b for a, b in zip(node.position_forward,
                                              node.position)])
    if facing == (0.0, 0.0, 0.0):
        facing = (1.0, 0.0, 0.0)
    center = node.position_center
    start = (center[0] + facing[0] * 0.7, center[1] + 0.4,
             center[2] + facing[2] * 0.7)
    if target is not None:
        # Leave the launcher pointing at the target, a little upward.
        aim, _ = _norm([a - b for a, b in zip(target.position_center, start)])
        direction = (aim[0], aim[1] + 0.35, aim[2])
    else:
        direction = (facing[0], facing[1] + 0.15, facing[2])

    spaz._bst_rockets -= 1
    _update_counter(spaz)
    rocket = Rocket(spaz, start, direction, target).autoretain()

    # Absorb Shield charge rides in the rocket.
    charge = getattr(Spaz, 'bsm_charge_projectile', None)
    if charge is not None:
        charge(spaz, rocket)

    _flash(start, (1.0, 0.6, 0.25), 0.6, 1.0, 1.5, 0.2)
    bs.emitfx(position=start, velocity=(0, 1, 0), count=2,
              emit_type='tendrils', tendril_type='smoke')
    _snd('laser', 0.8, start)
    _snd('swip2', 1.0, start)


# ------------------------------ Bomb kick ---------------------------------


def _is_own_active_bomb(spaz: Spaz, bomb: Bomb) -> bool:
    """Our own bomb with its fuse burning (or armed impact bomb/mine)."""
    if getattr(bomb, '_exploded', False) or not bomb.node:
        return False
    own = bomb.owner is not None and bomb.owner == spaz.node
    if not own:
        source = bomb.get_source_player(bs.Player)
        own = source is not None and source == spaz.source_player
    if not own:
        return False
    if bomb.bomb_type == 'tnt':
        return False
    if bomb.bomb_type in ('impact', 'land_mine'):
        armed_mat = BombFactory.get().land_mine_blast_material
        return armed_mat in bomb.node.materials
    return True  # Normal, ice and sticky bombs burn from the start.


def _find_kick_target(spaz: Spaz, bpos: Sequence[float]) -> bs.Node | None:
    """Closest enemy within the kick cone, in full 3D."""
    node = spaz.node
    kick, klen = _norm(node.punch_velocity)
    if klen < 0.1:
        kick, klen = _norm([a - b for a, b in zip(bpos, node.position)])
    if klen < 1e-4:
        return None
    min_cos = math.cos(math.radians(KICK_ANGLE))
    best: bs.Node | None = None
    best_score = 0.0
    for dist, target in _enemies(spaz, bpos, KICK_RANGE):
        if dist < 0.01:
            continue
        to, _ = _norm([a - b for a, b in zip(target.position_center, bpos)])
        cos = sum(a * b for a, b in zip(to, kick))
        if cos < min_cos:
            continue
        score = dist / cos  # Close and straight ahead wins.
        if best is None or score < best_score:
            best, best_score = target, score
    return best


def _kick_bomb(spaz: Spaz, bomb: Bomb, target: bs.Node) -> None:
    """Punch our live bomb into an enemy: a huge kinetic slug hit."""
    node = spaz.node
    bnode = bomb.node
    col = _color(spaz)
    hot = _bright(col, 2.0)
    source = bs.existing(spaz.source_player)
    take = getattr(Spaz, 'bsm_take_charge', None)
    charge = take(spaz) if take is not None else 0.0
    damage = KICK_DAMAGE + charge
    bomb.owner = node  # Don't go off on our own fist.

    ppos = node.punch_position
    pdir, _ = _norm(node.punch_velocity)
    _flash(ppos, hot, 1.0, 1.6, 2.5, 0.2)
    bs.emitfx(position=ppos, emit_type='distortion', spread=0.8 * FX_STRENGTH)
    _sparks(ppos, 25 + (25 if charge else 0),
            vel=(pdir[0] * 10.0, pdir[1] * 10.0 + 1.0, pdir[2] * 10.0),
            spread=0.2, scale=0.9)
    _shake(1.0 + (1.0 if charge else 0.0))
    _snd('super_punch', 1.0, ppos)
    _snd('swip2', 1.0, ppos)
    if charge:
        _snd('explosion02', 0.35, ppos)

    light = bs.newnode(
        'light',
        owner=bnode,
        attrs={
            'color': col,
            'radius': 0.18,
            'intensity': 1.2,
            'height_attenuated': False,
            'volume_intensity_scale': 0.3,
        },
    )
    bnode.connectattr('position', light, 'position')
    state = {'time': 0.0}

    def _stop() -> None:
        bomb._bst_kick_timer = None  # type: ignore[attr-defined]
        if light:
            light.delete()

    def _step() -> None:
        state['time'] += _TICK
        victim = target.getdelegate(Spaz) if target else None
        if (
            not bnode
            or victim is None
            or not victim.is_alive()
            or state['time'] > 1.5
        ):
            _stop()
            return
        bpos = bnode.position
        fdir, dist = _norm([a - b for a, b in zip(target.position_center,
                                                  bpos)])
        if dist < 0.9 + KICK_SPEED * _TICK:
            _stop()
            _impact(victim, fdir)
            return
        bnode.velocity = tuple(c * KICK_SPEED for c in fdir)
        _sparks(bpos, 2, vel=(0, 1, 0), spread=0.1, scale=0.6)
        if random.random() < 0.3:
            bs.emitfx(position=bpos, emit_type='distortion',
                      spread=0.4 * FX_STRENGTH)

    def _impact(victim: Spaz, fdir: Sequence[float]) -> None:
        bpos = bnode.position
        target.handlemessage(
            bs.HitMessage(
                pos=bpos,
                srcnode=node if node else None,
                source_player=bs.existing(source),
                force_direction=fdir,
                flat_damage=damage,
                hit_type='punch',
                hit_subtype='super_punch',
            )
        )
        if not _shielded(victim) and target:
            _knock(target, bpos, fdir, damage)
            target.handlemessage('knockout', 300.0)
        bnode.velocity = (-fdir[0] * 3.0, 4.0, -fdir[2] * 3.0)
        _flash(bpos, hot, 1.2, 2.5, 3.0, 0.3)
        _sparks(bpos, min(70, 25 + int(damage * 0.03)),
                vel=(fdir[0] * 4.0, 4.0, fdir[2] * 4.0), spread=0.5,
                scale=1.2)
        _shake(1.5 + min(2.0, damage / 600.0))
        _snd('big_impact', 1.0, bpos)
        _snd('punch_strong01', 1.0, bpos)
        # Contact bombs still go off on touching the living; fuses are
        # left alone.
        if bomb.bomb_type in ('impact', 'land_mine'):
            bomb.handlemessage(ExplodeMessage())

    # Kept on the bomb (which the game keeps alive) so it can't be
    # garbage-collected mid-flight.
    bomb._bst_kick_timer = bs.Timer(  # type: ignore[attr-defined]
        _TICK, _step, repeat=True
    )
    _step()


# ------------------------------- Patches ----------------------------------


def _patched_init(self: Spaz, *args: Any, **kwargs: Any) -> None:
    _orig_init(self, *args, **kwargs)
    self._bst_rockets = 0
    self._bst_aiming = False
    self._bst_target: bs.Node | None = None
    self._bst_marks: list[bs.Node] = []
    self._bst_cycle_timer: bs.Timer | None = None


def _patched_handlemessage(self: Spaz, msg: Any) -> Any:
    if not hasattr(self, '_bst_rockets'):
        return _orig_handlemessage(self, msg)

    if isinstance(msg, bs.PowerupMessage) and msg.poweruptype == 'rocket':
        if (
            self.node
            and self.is_alive()
            and (ROCKETS_FOR_BOTS or isinstance(self, PlayerSpaz))
        ):
            self._bst_rockets = min(ROCKET_MAX, self._bst_rockets + 1)
            self._flash_billboard(RocketFactory.get().box_tex)
            _update_counter(self)
        return _orig_handlemessage(self, msg)

    if isinstance(msg, PunchHitMessage) and self.node:
        try:
            hit = bs.getcollision().opposingnode
        except bs.NotFoundError:
            hit = None
        if hit is not None and hit not in self._punched_nodes:
            bomb = hit.getdelegate(Bomb)
            if bomb is not None and _is_own_active_bomb(self, bomb):
                target = _find_kick_target(self, bomb.node.position)
                if target is not None:
                    self._punched_nodes.add(hit)
                    _kick_bomb(self, bomb, target)
                    return None

    if isinstance(msg, bs.DieMessage):
        _stop_aiming(self)

    return _orig_handlemessage(self, msg)


def _patched_bomb_press(self: Spaz) -> None:
    node = self.node
    if (
        getattr(self, '_bst_rockets', 0) > 0
        and node
        and self.is_alive()
        and not self.frozen
        and node.knockout <= 0.0
        and not node.hold_node
    ):
        _start_aiming(self)
        return
    _orig_bomb_press(self)


def _patched_bomb_release(self: Spaz) -> None:
    if getattr(self, '_bst_aiming', False):
        _fire_rocket(self)
    _orig_bomb_release(self)


def _patched_set_land_mine_count(self: Spaz, count: int) -> None:
    _orig_set_land_mine_count(self, count)
    if getattr(self, '_bst_rockets', 0) > 0:
        _update_counter(self)


def _patched_box_factory_init(self: PowerupBoxFactory) -> None:
    _orig_box_factory_init(self)
    self._powerupdist.extend(['rocket'] * ROCKET_FREQ)


def _patched_box_init(self: PowerupBox, *args: Any, **kwargs: Any) -> None:
    if kwargs.get('poweruptype') == 'rocket':
        kwargs['poweruptype'] = 'triple_bombs'
    elif len(args) > 1 and args[1] == 'rocket':
        args = (args[0], 'triple_bombs', *args[2:])
    else:
        _orig_box_init(self, *args, **kwargs)
        return
    _orig_box_init(self, *args, **kwargs)
    self.poweruptype = 'rocket'
    self.node.color_texture = RocketFactory.get().box_tex


# ba_meta export babase.Plugin
class BoostersPlugin(babase.Plugin):
    """Rocket powerup and bomb kicks."""

    def __init__(self) -> None:
        # The mod may be both built into BSM and dropped into mods/;
        # only the first copy patches the game.
        if getattr(Spaz, '_bst_patched', False):
            return
        Spaz._bst_patched = True  # type: ignore[attr-defined]

        global _orig_init, _orig_handlemessage, _orig_bomb_press
        global _orig_bomb_release, _orig_set_land_mine_count
        global _orig_box_factory_init, _orig_box_init
        _orig_init = Spaz.__init__
        _orig_handlemessage = Spaz.handlemessage
        _orig_bomb_press = Spaz.on_bomb_press
        _orig_bomb_release = Spaz.on_bomb_release
        _orig_set_land_mine_count = Spaz.set_land_mine_count
        _orig_box_factory_init = PowerupBoxFactory.__init__
        _orig_box_init = PowerupBox.__init__

        Spaz.__init__ = _patched_init
        Spaz.handlemessage = _patched_handlemessage
        Spaz.on_bomb_press = _patched_bomb_press
        Spaz.on_bomb_release = _patched_bomb_release
        Spaz.set_land_mine_count = _patched_set_land_mine_count
        PowerupBoxFactory.__init__ = _patched_box_factory_init
        PowerupBox.__init__ = _patched_box_init
