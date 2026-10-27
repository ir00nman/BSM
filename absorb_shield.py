# ba_meta require api 9
"""Absorb Shield — парирование с поглощением урона для BombSquad 1.8.x.

Нажми кнопку щита в правильный момент — вокруг бойца на 0.4 секунды
вспыхивает щит его цвета и поглощает ВЕСЬ входящий урон. Поглощённый урон
копится в заряд, и боец светится основным цветом своего скина. Следующая
атака выпускает заряд:
  * удар кулаком — весь заряд входит в этот же удар (один удар, а не два);
  * с плагином BSM Boosters заряд работает и через удар по своей ударной
    или ледяной бомбе (плагины складываются друг с другом);
  * бомба — бомба светится и при взрыве бьёт всех вокруг накопленным уроном;
    заряженная ледяная бомба вдобавок пускает морозную волну, которая
    замораживает всех в радиусе в 1.7 раза больше обычного взрыва.

Кнопка щита («5-я кнопка»):
  * двойное нажатие «Схватить» (работает везде, в том числе на сенсорном
    экране — экранные кнопки рисует движок, и Python-мод не может добавить
    к ним пятую, не сломав управление). Второе нажатие при этом всё равно
    хватает или бросает предмет, как обычно;
  * кнопка «удержание позиции» на геймпадах, где она есть.

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
from bascenev1lib.actor.bomb import Bomb
from bascenev1lib.actor.playerspaz import PlayerSpaz
from bascenev1lib.actor.spaz import PunchHitMessage, Spaz

if TYPE_CHECKING:
    from typing import Any, Sequence

    from bascenev1lib.actor.bomb import Blast

# ------------------------------- Настройки --------------------------------

SHIELD_TIME = 0.4  # Сколько секунд держится щит.
COOLDOWN = 1.0  # Перезарядка щита после его окончания (сек).
DOUBLE_TAP_WINDOW = 0.4  # Макс. пауза между двумя нажатиями «Схватить».
USE_DOUBLE_TAP_GRAB = True  # Щит по двойному нажатию «Схватить».
USE_HOLD_POSITION = True  # Щит по кнопке удержания позиции (геймпады).
CHARGE_TIME = 10.0  # Сколько секунд держится заряд, потом рассеивается.
RELEASE_MULT = 1.0  # Множитель отдаваемого урона (1.0 = весь поглощённый).
# Взрывы в обычной игре ранят ещё и ударом о землю после отброса; щит гасит
# отброс, поэтому урон взрывов засчитывается в заряд с этим множителем.
EXPLOSION_ABSORB_MULT = 2.0
MAX_STORED = 3000  # Предел заряда (1000 = полное здоровье бойца).
BOMB_RADIUS_MULT = 1.6  # Радиус бонусного взрыва относительно обычного.
PLAYERS_ONLY = True  # Только игроки (боты щит не используют).
SHOW_HINT = True  # Подсказка про щит в начале каждой игры.
FX_STRENGTH = 0.5  # Сила вспышек, света и тряски камеры (1.0 = максимум).
FROST_RADIUS_MULT = 1.7  # Радиус морозной волны: во столько раз больше
#                          радиуса взрыва заряженной ледяной бомбы.
FROST_TIME = 5.0  # Сколько секунд держится заморозка от волны.
FROST_WAVE_SPEED = 12.0  # Скорость фронта волны (метров в секунду).
ABSORB_GRACE = 0.25  # Щит продлевается на столько после каждого поглощения
#                     (чтобы цепочка взрывов нескольких бомб впиталась целиком).
SHIELD_MAX_TIME = 1.2  # Предел длительности щита вместе с продлениями.

# --------------------------------------------------------------------------

_DAMAGE_SCALE = 0.22  # Как в Spaz: node.damage -> очки урона.

# Captured when the plugin switches on (not at import), so plugins that
# patch the same Spaz methods chain instead of overwriting each other.
_orig_init: Any = None
_orig_handlemessage: Any = None
_orig_pickup_press: Any = None
_orig_hold_position_press: Any = None
_orig_drop_bomb: Any = None

# A charged punch in flight: the victim folds the bonus into the punch's
# own HitMessage so the release lands as a single hit.
_punch_bonus: list[dict | None] = [None]

# Charged-bomb bonus waiting for that bomb's own blast hit on each victim.
_blast_bonus: dict = {}


def _wcall(func: Any, spaz: Spaz) -> Any:
    """Timer callback that holds the spaz weakly (no ref cycles)."""
    ref = weakref.ref(spaz)

    def _call() -> None:
        obj = ref()
        if obj is not None:
            func(obj)

    return _call


def _snd(name: str, volume: float = 1.0, pos: Sequence[float] | None = None):
    """Play a classic game sound by its asset name."""
    try:
        sound = getattr(_classicassets.audio, name).get()
    except Exception:
        return
    if pos is None:
        sound.play(volume)
    else:
        sound.play(volume, position=pos)


def _bright(color: Sequence[float], scale: float = 1.0) -> tuple:
    """Normalize a skin color so even dark skins glow visibly."""
    rgb = [max(0.0, float(c)) for c in color[:3]]
    peak = max(rgb)
    if peak < 0.05:
        return (scale, scale, scale)
    return tuple(c / peak * scale for c in rgb)


def _flash(
    pos: Sequence[float],
    color: Sequence[float],
    size: float,
    light_radius: float,
    intensity: float,
    duration: float = 0.25,
) -> None:
    """A colored flash + light burst at a point."""
    size *= FX_STRENGTH
    light_radius *= FX_STRENGTH
    intensity *= FX_STRENGTH
    flash = bs.newnode(
        'flash', attrs={'position': pos, 'size': size, 'color': color}
    )
    bs.timer(0.08, flash.delete)
    light = bs.newnode(
        'light',
        attrs={
            'position': pos,
            'color': color,
            'radius': light_radius,
            'height_attenuated': False,
            'volume_intensity_scale': 0.6,
        },
    )
    bs.animate(light, 'intensity', {0: intensity, duration: 0.0})
    bs.timer(duration + 0.05, light.delete)


def _ring(
    pos: Sequence[float],
    color: Sequence[float],
    size: float,
    duration: float,
    owner: bs.Node | None = None,
) -> None:
    """An expanding circle that fades out (like target practice rings)."""
    ring = bs.newnode(
        'locator',
        owner=owner,
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


def _popup_text(
    text: str, pos: Sequence[float], color: Sequence[float], big: bool = False
) -> None:
    """Floating text that pops up and rises, like damage counters."""
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
    bs.animate(comb, 'input0', {0: pos[0], 1.0: pos[0]})
    bs.animate(comb, 'input1', {0: pos[1] + 1.2, 1.0: pos[1] + 2.2})
    bs.animate(comb, 'input2', {0: pos[2], 1.0: pos[2]})
    peak = 0.022 if big else 0.016
    bs.animate(txt, 'scale', {0: 0.0, 0.1: peak * 1.4, 0.2: peak, 1.0: 0.0})
    bs.timer(1.05, txt.delete)


def _shake(intensity: float) -> None:
    bs.camerashake(intensity * FX_STRENGTH)


def _sparks(
    pos: Sequence[float],
    count: int,
    vel: Sequence[float] = (0.0, 4.0, 0.0),
    spread: float = 0.6,
    scale: float = 1.0,
) -> None:
    bs.emitfx(
        position=pos,
        velocity=vel,
        count=count,
        scale=scale,
        spread=spread,
        chunk_type='spark',
    )


# ---------------------------- State on the Spaz ---------------------------


def _patched_init(self: Spaz, *args: Any, **kwargs: Any) -> None:
    _orig_init(self, *args, **kwargs)
    self._ab_shield_node: bs.Node | None = None
    self._ab_shield_timer: bs.Timer | None = None
    self._ab_active = False
    self._ab_ready_time = 0.0
    self._ab_last_grab_tap = -999.0
    self._ab_absorbed = 0.0  # Absorbed during the current shield.
    self._ab_stored = 0.0  # Charge waiting for the next attack.
    self._ab_glow_nodes: list[bs.Node] = []
    self._ab_glow_text: bs.Node | None = None
    self._ab_glow_timer: bs.Timer | None = None
    self._ab_charge_timer: bs.Timer | None = None
    if SHOW_HINT and isinstance(self, PlayerSpaz):
        _show_hint_once()


_hinted_activities: weakref.WeakSet = weakref.WeakSet()


def _show_hint_once() -> None:
    """Tell players how to use the shield, once per game."""
    activity = bs.getactivity(doraise=False)
    if activity is None or activity in _hinted_activities:
        return
    _hinted_activities.add(activity)
    bs.broadcastmessage(
        'ЩИТ: дважды быстро нажми «Схватить» прямо перед ударом',
        color=(0.5, 0.9, 1.0),
    )


def _color(spaz: Spaz) -> tuple:
    try:
        return _bright(spaz.node.color, 1.0)
    except Exception:
        return (1.0, 1.0, 1.0)


def _can_shield(spaz: Spaz) -> bool:
    if PLAYERS_ONLY and not isinstance(spaz, PlayerSpaz):
        return False
    node = spaz.node
    return bool(
        node
        and not spaz._dead  # pylint: disable=protected-access
        and not spaz.frozen
        and node.knockout <= 0.0
        and not getattr(spaz, '_ab_active', True)
        and bs.time() >= spaz._ab_ready_time
    )


# --------------------------------- Shield ---------------------------------


def _activate_shield(spaz: Spaz) -> None:
    node = spaz.node
    col = _color(spaz)
    hot = _bright(col, 1.6)
    pos = node.position_center

    spaz._ab_active = True
    spaz._ab_absorbed = 0.0
    spaz._ab_last_absorb_time = -1.0
    spaz._ab_shield_start = bs.time()
    spaz._ab_shield_end = bs.time() + SHIELD_TIME

    # Energy bubble in the skin color: snaps out, then holds.
    shield = bs.newnode(
        'shield', owner=node, attrs={'color': hot, 'radius': 0.2}
    )
    node.connectattr('position_center', shield, 'position')
    bs.animate(
        shield,
        'radius',
        {0: 0.2, 0.05: 1.65, 0.1: 1.35, SHIELD_TIME: 1.4},
    )
    spaz._ab_shield_node = shield

    _flash(pos, hot, 0.9, 1.0, 1.4, duration=SHIELD_TIME)
    _ring(node.position, col, 3.2, 0.3, owner=node)
    _sparks(pos, 12, spread=0.4, scale=0.6)
    _snd('shield_up', 0.9, pos)
    _snd('swip2', 0.8, pos)

    spaz._ab_shield_timer = bs.Timer(
        SHIELD_TIME, _wcall(_end_shield, spaz)
    )


def _end_shield(spaz: Spaz) -> None:
    spaz._ab_active = False
    spaz._ab_ready_time = bs.time() + COOLDOWN
    shield = spaz._ab_shield_node
    spaz._ab_shield_node = None
    if shield:
        bs.animate(shield, 'radius', {0: shield.radius, 0.1: 0.0})
        bs.timer(0.11, shield.delete)
    node = spaz.node
    if not node or spaz._dead:  # pylint: disable=protected-access
        return

    if spaz._ab_absorbed > 0:
        # One total for the whole shield (per-hit numbers overlapped).
        pos = node.position
        _popup_text(
            f'+{int(spaz._ab_absorbed / 10)}%',
            (pos[0], pos[1] + 0.5, pos[2]),
            _color(spaz),
            big=True,
        )
        _add_charge(spaz, spaz._ab_absorbed)
    else:
        # Miss: shield fizzles quietly.
        _snd('shield_down', 0.35, node.position)


def _calc_damage(spaz: Spaz, msg: bs.HitMessage) -> float:
    """How much a hit would hurt, without applying it (as Spaz shields do)."""
    if msg.flat_damage:
        return float(msg.flat_damage * spaz.impact_scale)
    fdir = msg.force_direction
    if fdir is None:
        fdir = (0.0, 0.0, 0.0)
    spaz.node.handlemessage(
        'impulse',
        msg.pos[0],
        msg.pos[1],
        msg.pos[2],
        msg.velocity[0],
        msg.velocity[1],
        msg.velocity[2],
        msg.magnitude * spaz.impact_scale,
        msg.velocity_magnitude * spaz.impact_scale,
        msg.radius,
        1,
        fdir[0],
        fdir[1],
        fdir[2],
    )
    return max(0.0, float(_DAMAGE_SCALE * spaz.node.damage))


def _apply_impulse(spaz: Spaz, msg: bs.HitMessage) -> None:
    """Apply a hit's physical push (used when its damage goes in flat)."""
    fdir = msg.force_direction
    if fdir is None:
        fdir = (0.0, 0.0, 0.0)
    spaz.node.handlemessage(
        'impulse',
        msg.pos[0],
        msg.pos[1],
        msg.pos[2],
        msg.velocity[0],
        msg.velocity[1],
        msg.velocity[2],
        msg.magnitude * spaz.impact_scale,
        msg.velocity_magnitude * spaz.impact_scale,
        msg.radius,
        0,
        fdir[0],
        fdir[1],
        fdir[2],
    )


def _absorb_hit(spaz: Spaz, msg: bs.HitMessage) -> None:
    """Eat a hit completely and remember how much it would have hurt."""
    node = spaz.node
    damage = _calc_damage(spaz, msg)
    if msg.hit_type == 'explosion':
        damage *= EXPLOSION_ABSORB_MULT
    first = spaz._ab_absorbed <= 0
    spaz._ab_absorbed += damage

    # Keep the shield up a bit after every hit so a chain of blasts from
    # several bombs is soaked up completely.
    now = bs.time()
    new_end = min(
        spaz._ab_shield_start + SHIELD_MAX_TIME,
        max(spaz._ab_shield_end, now + ABSORB_GRACE),
    )
    if new_end > spaz._ab_shield_end:
        spaz._ab_shield_end = new_end
        spaz._ab_shield_timer = bs.Timer(
            new_end - now, _wcall(_end_shield, spaz)
        )

    # Hits landing in the same moment (one blast touching several body
    # parts, several bombs at once) count as one hit: effects play once.
    if now - spaz._ab_last_absorb_time < 0.05:
        return
    spaz._ab_last_absorb_time = now

    col = _color(spaz)
    hot = _bright(col, 2.0)
    hitpos = msg.pos if msg.hit_type == 'punch' else node.position_center

    shield = spaz._ab_shield_node
    if shield:
        bs.animate(shield, 'radius', {0: 1.8, 0.08: 1.4})

    _flash(hitpos, hot, 0.5 + min(1.0, damage / 800.0), 1.4, 2.5, 0.3)
    _ring(node.position, hot, 4.0, 0.35, owner=node)
    _sparks(hitpos, min(40, 12 + int(damage * 0.03)), spread=0.8, scale=0.9)
    _shake(0.6)
    _snd('block', 1.0, hitpos)
    _snd('shield_hit', 1.0, hitpos)
    if first:
        # The "perfect parry" sting.
        _snd('orchestra_hit', 0.9, hitpos)
        _snd('ding_small_high', 0.8, hitpos)
        _popup_text('БЛОК!', node.position, hot, big=True)


# --------------------------------- Charge ---------------------------------


def _add_charge(spaz: Spaz, amount: float) -> None:
    spaz._ab_stored = min(MAX_STORED, spaz._ab_stored + amount)
    node = spaz.node
    col = _color(spaz)
    _snd('powerup01', 0.9, node.position)
    _snd('laser', 0.5, node.position)
    _flash(node.position_center, _bright(col, 1.5), 1.2, 1.2, 1.5, 0.4)
    _start_glow(spaz)
    spaz._ab_charge_timer = bs.Timer(
        CHARGE_TIME, _wcall(_charge_expired, spaz)
    )


def _start_glow(spaz: Spaz) -> None:
    """Make the spaz glow in their main skin color while charged."""
    node = spaz.node
    col = _color(spaz)
    level = min(1.0, spaz._ab_stored / 1000.0)
    _stop_glow(spaz)

    light = bs.newnode(
        'light',
        owner=node,
        attrs={
            'color': col,
            'radius': 0.25 + 0.15 * level,
            'height_attenuated': False,
            'volume_intensity_scale': 0.4,
        },
    )
    node.connectattr('position_center', light, 'position')
    lo, hi = 0.5 + 0.3 * level, 1.1 + 0.7 * level
    bs.animate(light, 'intensity', {0: lo, 0.35: hi, 0.7: lo}, loop=True)

    # Ground halo that breathes with the light.
    halo = bs.newnode(
        'locator',
        owner=node,
        attrs={
            'shape': 'circle',
            'color': col,
            'opacity': 0.25,
            'draw_beauty': False,
            'additive': True,
        },
    )
    node.connectattr('position', halo, 'position')
    bs.animate_array(
        halo, 'size', 1, {0: [1.1], 0.35: [1.4], 0.7: [1.1]}, loop=True
    )

    # Charge counter floating over the head.
    mnode = bs.newnode(
        'math',
        owner=node,
        attrs={'input1': (0, 1.45, 0), 'operation': 'add'},
    )
    node.connectattr('torso_position', mnode, 'input2')
    text = bs.newnode(
        'text',
        owner=node,
        attrs={
            'text': f'+{int(spaz._ab_stored / 10)}%',
            'in_world': True,
            'h_align': 'center',
            'shadow': 1.0,
            'flatness': 1.0,
            'color': (col[0], col[1], col[2], 1.0),
            'scale': 0.0,
        },
    )
    mnode.connectattr('output', text, 'position')
    bs.animate(text, 'scale', {0: 0.0, 0.12: 0.016, 0.25: 0.011})

    spaz._ab_glow_nodes = [light, halo, mnode, text]
    spaz._ab_glow_text = text
    spaz._ab_glow_timer = bs.Timer(
        0.12, _wcall(_glow_tick, spaz), repeat=True
    )


def _glow_tick(spaz: Spaz) -> None:
    node = spaz.node
    if not node:
        return
    pos = node.position_center
    _sparks(
        (
            pos[0] + random.uniform(-0.3, 0.3),
            pos[1] + random.uniform(-0.3, 0.4),
            pos[2] + random.uniform(-0.3, 0.3),
        ),
        2,
        vel=(0.0, 2.0, 0.0),
        spread=0.15,
        scale=0.5,
    )


def _stop_glow(spaz: Spaz) -> None:
    for gnode in spaz._ab_glow_nodes:
        if gnode:
            gnode.delete()
    spaz._ab_glow_nodes = []
    spaz._ab_glow_text = None
    spaz._ab_glow_timer = None


def _take_charge(spaz: Spaz) -> float:
    amount = spaz._ab_stored * RELEASE_MULT
    spaz._ab_stored = 0.0
    spaz._ab_charge_timer = None
    _stop_glow(spaz)
    return amount


def _charge_expired(spaz: Spaz) -> None:
    if spaz._ab_stored <= 0:
        return
    _take_charge(spaz)
    node = spaz.node
    if node:
        _snd('shield_down', 0.8, node.position)
        _sparks(node.position_center, 20, spread=0.5, scale=0.7)


def _clear_all(spaz: Spaz) -> None:
    spaz._ab_stored = 0.0
    spaz._ab_charge_timer = None
    spaz._ab_shield_timer = None
    spaz._ab_active = False
    _stop_glow(spaz)


# --------------------------- Releasing the charge -------------------------


def _knock(target: bs.Node, pos: Sequence[float], fdir: Sequence[float],
           power: float) -> None:
    """Shove a node; power ~ amount of damage released."""
    if target.getnodetype() not in ('spaz', 'prop', 'bomb'):
        return
    k = max(0.4, min(2.5, power / 600.0))
    target.handlemessage(
        'impulse',
        pos[0],
        pos[1],
        pos[2],
        0.0,
        0.0,
        0.0,
        700.0 * k,
        60.0 * k,
        0.0,
        0,
        fdir[0],
        fdir[1] + 0.3,
        fdir[2],
    )


def _merge_bonus(victim: Spaz, msg: bs.HitMessage, bonus: float,
                 pos: Sequence[float], fdir: Sequence[float]) -> None:
    """Fold released charge into an incoming hit so it lands as one hit."""
    shielded = victim.shield is not None or getattr(victim, '_ab_active', False)
    total = _calc_damage(victim, msg) + bonus
    if not shielded:
        # Flat damage skips the hit's own push; apply it, plus ours.
        _apply_impulse(victim, msg)
        _knock(victim.node, pos, fdir, bonus)
    msg.flat_damage = total / max(victim.impact_scale, 0.01)


def _sonic_boom(pos: Sequence[float], direction: Sequence[float],
                color: Sequence[float], power: float) -> None:
    """A fist breaking the sound barrier: shock rings, vapor cone, sparks."""
    dlen = math.sqrt(sum(c * c for c in direction))
    if dlen < 0.01:
        direction, dlen = (1.0, 0.0, 0.0), 1.0
    fx, fy, fz = (c / dlen for c in direction)
    power = max(0.3, min(2.0, power))

    # White-hot core and a short colored bloom.
    _flash(pos, (1.6, 1.6, 1.6), 0.5, 0.0, 0.0, 0.05)
    _flash(pos, _bright(color, 2.0), 0.9, 1.6, 2.5, 0.2)

    # Shock bubbles chasing the fist forward: the "barrier" breaking.
    for i in range(3):
        step = 0.3 + 0.3 * i
        bs.timer(
            0.025 * i,
            bs.CallStrict(
                bs.emitfx,
                position=(pos[0] + fx * step, pos[1] + fy * step,
                          pos[2] + fz * step),
                emit_type='distortion',
                spread=(0.6 + 0.4 * i) * FX_STRENGTH * power,
            ),
        )

    # Vapor cone: white mist thrown forward and out.
    bs.emitfx(position=pos, velocity=(fx * 9.0, fy * 9.0 + 1.0, fz * 9.0),
              count=int(25 * power), scale=0.7, spread=0.45,
              chunk_type='sweat')
    bs.emitfx(position=pos, velocity=(fx * 4.0, fy * 4.0, fz * 4.0),
              count=2, emit_type='tendrils', tendril_type='thin_smoke')

    # Sparks streaking ahead of the punch.
    bs.emitfx(position=pos, velocity=(fx * 14.0, fy * 14.0 + 1.0, fz * 14.0),
              count=int(30 * power), scale=0.9, spread=0.15,
              chunk_type='spark')
    _sparks(pos, int(15 * power), vel=(fx * 4.0, 3.0, fz * 4.0), spread=0.6,
            scale=0.8)

    _shake(0.8 + power)
    _snd('big_impact', 1.0, pos)
    _snd('explosion02', 0.35, pos)  # The boom.
    _snd('swish', 1.0, pos)


def _release_punch_fx(spaz: Spaz, amount: float,
                      victim: bs.Node | None) -> None:
    node = spaz.node
    col = _color(spaz)
    hot = _bright(col, 2.0)
    ppos = node.punch_position
    pdir = node.punch_velocity
    dlen = math.sqrt(sum(c * c for c in pdir)) or 1.0
    fwd = tuple(c / dlen for c in pdir)

    _sonic_boom(ppos, pdir, col, 0.5 + amount / 1000.0)

    # Particles shooting through the target: colored burst at the fist...
    expl = bs.newnode(
        'explosion',
        attrs={'position': ppos,
               'radius': (0.5 + min(0.8, amount / 1500.0)) * FX_STRENGTH,
               'color': col},
    )
    bs.timer(1.0, expl.delete)
    _flash(ppos, hot, 1.0, 2.5, 3.0, 0.35)
    _ring(ppos, hot, 3.5, 0.3)
    _sparks(ppos, min(60, 20 + int(amount * 0.03)),
            vel=(fwd[0] * 3.0, fwd[1] * 3.0 + 2.0, fwd[2] * 3.0),
            spread=0.5, scale=1.2)
    # ...and out of their back.
    if victim:
        vpos = victim.position_center
        exit_pos = (vpos[0] + fwd[0] * 0.5, vpos[1] + fwd[1] * 0.5,
                    vpos[2] + fwd[2] * 0.5)
        bs.emitfx(position=exit_pos,
                  velocity=(fwd[0] * 12.0, fwd[1] * 12.0 + 1.5,
                            fwd[2] * 12.0),
                  count=min(50, 15 + int(amount * 0.02)), scale=1.0,
                  spread=0.2, chunk_type='spark')
        bs.emitfx(position=exit_pos,
                  velocity=(fwd[0] * 6.0, fwd[1] * 6.0 + 2.0, fwd[2] * 6.0),
                  count=min(30, 8 + int(amount * 0.015)), scale=0.8,
                  spread=0.3, chunk_type='sweat')

    # The punch itself already plays the super-punch sound.
    _snd('orchestra_hit_big2', 0.7, ppos)
    _snd('punch_strong02', 1.0, ppos)
    if amount >= 600:
        _snd('cymbal', 0.5, ppos)


def _freeze_node(target: bs.Node) -> None:
    if not target:
        return
    tpos = target.position
    target.handlemessage(bs.FreezeMessage(time=FROST_TIME))
    bs.emitfx(position=tpos, velocity=(0, 3, 0), count=12, scale=0.6,
              spread=0.5, chunk_type='ice')
    _flash(tpos, (0.6, 0.9, 1.8), 0.6, 0.8, 1.5, 0.3)
    _snd('freeze', 1.0, tpos)


def _frost_wave(pos: Sequence[float], owner: bs.Node | None,
                radius: float) -> None:
    """Ring of frost rolling out from a charged ice bomb, freezing all."""
    ice = (0.45, 0.8, 1.6)
    duration = radius / FROST_WAVE_SPEED

    _ring(pos, ice, radius * 2.0, duration)
    _ring(pos, (0.85, 0.95, 1.6), radius * 1.7, duration * 0.85)

    # Frosty patch on the ground that grows with the wave, then melts.
    patch = bs.newnode(
        'locator',
        attrs={
            'shape': 'circle',
            'position': pos,
            'color': ice,
            'opacity': 0.35,
            'draw_beauty': False,
            'additive': True,
        },
    )
    bs.animate_array(
        patch, 'size', 1, {0: [0.5], duration: [radius * 2.0]}
    )
    bs.animate(patch, 'opacity', {0: 0.35, duration: 0.25, duration + 1.5: 0})
    bs.timer(duration + 1.6, patch.delete)

    light = bs.newnode(
        'light',
        attrs={
            'position': pos,
            'color': ice,
            'radius': radius * 0.15 * FX_STRENGTH,
            'height_attenuated': False,
            'volume_intensity_scale': 0.6,
        },
    )
    bs.animate(
        light,
        'intensity',
        {0: 3.0 * FX_STRENGTH, duration: 1.2 * FX_STRENGTH, duration + 0.6: 0},
    )
    bs.timer(duration + 0.7, light.delete)

    bs.emitfx(position=pos, emit_type='distortion', spread=radius * 0.5)
    bs.emitfx(position=pos, velocity=(0, 6, 0), count=40, scale=0.8,
              spread=1.5, chunk_type='ice')
    _snd('freeze', 1.0, pos)
    _snd('hiss', 1.0, pos)
    _snd('orchestra_hit3', 0.8, pos)

    # Ice shards along the wave front.
    def _emit_front(rad: float) -> None:
        points = max(6, int(rad * 2.5))
        for i in range(points):
            ang = 2.0 * math.pi * i / points
            bs.emitfx(
                position=(
                    pos[0] + rad * math.cos(ang),
                    pos[1],
                    pos[2] + rad * math.sin(ang),
                ),
                velocity=(0, 2, 0),
                count=2,
                scale=0.5,
                spread=0.2,
                chunk_type='ice',
                emit_type='stickers',
            )

    steps = 8
    for step in range(1, steps + 1):
        bs.timer(
            duration * step / steps,
            bs.CallStrict(_emit_front, radius * step / steps),
        )

    # Freeze everyone as the front reaches them (corpses shatter).
    for target in bs.getnodes():
        if not target or target == owner or target.getnodetype() != 'spaz':
            continue
        tpos = target.position
        dist = math.sqrt(
            (tpos[0] - pos[0]) ** 2
            + (tpos[1] - pos[1]) ** 2
            + (tpos[2] - pos[2]) ** 2
        )
        if dist <= radius:
            # Never before the blast itself lands (0.05 s): freezing first
            # would let the blast shatter them outright.
            bs.timer(
                max(0.07, dist / FROST_WAVE_SPEED),
                bs.CallStrict(_freeze_node, target),
            )


def _blast_bonus_fallback(target: bs.Node, entry: dict,
                          source: bs.Player | None) -> None:
    if _blast_bonus.get(target) is not entry:
        return  # Already merged into the blast hit.
    del _blast_bonus[target]
    if not target:
        return
    victim = target.getdelegate(Spaz)
    if victim is None or not victim.is_alive():
        return
    if victim.shield is None and not getattr(victim, '_ab_active', False):
        _knock(target, entry['pos'], entry['fdir'], entry['amount'])
    target.handlemessage(
        bs.HitMessage(
            pos=target.position,
            source_player=bs.existing(source),
            force_direction=entry['fdir'],
            flat_damage=entry['amount'],
            hit_type='explosion',
            hit_subtype='normal',
        )
    )


def _power_up_bomb(spaz: Spaz, bomb: Bomb) -> None:
    amount = _take_charge(spaz)
    if amount <= 0 or not bomb.node:
        return
    # Other BSM plugins can tell (and spend) a charged bomb by this.
    bomb._ab_charge = amount  # type: ignore[attr-defined]
    col = _color(spaz)
    hot = _bright(col, 1.8)
    owner = spaz.node
    bnode = bomb.node

    light = bs.newnode(
        'light',
        owner=bomb.node,
        attrs={
            'color': col,
            'radius': 0.15,
            'height_attenuated': False,
            'volume_intensity_scale': 0.5,
        },
    )
    bnode.connectattr('position', light, 'position')

    chunk = 'ice' if bomb.bomb_type == 'ice' else 'spark'

    def _trail() -> None:
        if bnode:
            bs.emitfx(position=bnode.position, velocity=(0, 1.5, 0), count=2,
                      scale=0.5, spread=0.1, chunk_type=chunk)

    # Kept in a list so the explode callback can stop it.
    trail: list[bs.Timer] = []
    if bomb.bomb_type == 'land_mine':
        # A mine can lie around for ages: just a faint glow, no sparks.
        bs.animate(light, 'intensity', {0: 0.2, 0.6: 0.6, 1.2: 0.2},
                   loop=True)
    else:
        bs.animate(light, 'intensity', {0: 0.8, 0.15: 2.2, 0.3: 0.8},
                   loop=True)
        trail.append(bs.Timer(0.08, _trail, repeat=True))

    _flash(bomb.node.position, hot, 0.6, 1.0, 1.5, 0.3)
    _snd('powerup01', 0.9, bomb.node.position)
    _snd('laser_reverse', 0.7, bomb.node.position)

    def _on_explode(bmb: Bomb, blast: Blast) -> None:
        trail.clear()
        if not blast.node:
            return
        pos = blast.node.position
        radius = blast.radius * BOMB_RADIUS_MULT

        expl = bs.newnode(
            'explosion',
            attrs={'position': pos, 'radius': radius * FX_STRENGTH,
                   'color': col, 'big': amount >= 1000 and FX_STRENGTH >= 1},
        )
        bs.timer(1.0, expl.delete)
        _flash(pos, hot, radius * 0.8, radius * 1.5, 4.0, 0.6)
        _ring(pos, hot, radius * 2.0, 0.45)
        _sparks(pos, 70, vel=(0, 8, 0), spread=radius * 0.5, scale=1.4)
        bs.emitfx(position=pos, emit_type='distortion',
                  spread=radius * FX_STRENGTH)
        _shake(2.0 + min(3.0, amount / 600.0))
        _snd('explosion05', 1.0, pos)
        _snd('orchestra_hit_big1', 0.9, pos)

        for target in bs.getnodes():
            if not target or target == owner:
                continue
            if target.getnodetype() != 'spaz':
                continue
            victim = target.getdelegate(Spaz)
            if victim is None or not victim.is_alive():
                continue
            tpos = target.position
            dx, dy, dz = tpos[0] - pos[0], tpos[1] - pos[1], tpos[2] - pos[2]
            dist = math.sqrt(dx * dx + dy * dy + dz * dz)
            if dist > radius:
                continue
            # Direct hits get the full charge; it fades further out.
            falloff = (
                1.0 if dist <= 1.2
                else max(0.35, 1.0 - (dist - 1.2) / max(radius - 1.2, 0.1))
            )
            dmg = amount * falloff
            norm = max(dist, 0.01)
            fdir = (dx / norm, dy / norm + 0.5, dz / norm)
            # Ride along with this bomb's own blast hit if it reaches the
            # victim; otherwise (outside the normal blast) hit on our own.
            entry = {'amount': dmg, 'pos': pos, 'fdir': fdir}
            _blast_bonus[target] = entry
            bs.timer(
                0.1,
                bs.CallStrict(
                    _blast_bonus_fallback, target, entry,
                    bmb.get_source_player(bs.Player),
                ),
            )

        # Charged ice bomb: frost wave on top of the bonus damage.
        if bmb.bomb_type == 'ice':
            _frost_wave(pos, owner, blast.radius * FROST_RADIUS_MULT)

    bomb.add_explode_callback(_on_explode)


# ------------------------------- Patches ----------------------------------


def _patched_handlemessage(self: Spaz, msg: Any) -> Any:
    if not hasattr(self, '_ab_active'):
        return _orig_handlemessage(self, msg)

    # Released charge rides inside the punch/blast hit: one hit, not two.
    if isinstance(msg, bs.HitMessage) and self.node and self.is_alive():
        if msg.hit_type == 'punch':
            pend = _punch_bonus[0]
            if (
                pend is not None
                and not pend['used']
                and msg.srcnode == pend['src']
                and self.node != pend['src']
            ):
                pend['used'] = True
                pend['victim'] = self.node
                _merge_bonus(self, msg, pend['amount'], msg.pos,
                             msg.force_direction or (0.0, 0.0, 0.0))
                msg.hit_subtype = 'super_punch'
        elif msg.hit_type == 'explosion' and self.node in _blast_bonus:
            entry = _blast_bonus[self.node]
            bpos = entry['pos']
            if (
                abs(msg.pos[0] - bpos[0]) < 0.5
                and abs(msg.pos[1] - bpos[1]) < 0.5
                and abs(msg.pos[2] - bpos[2]) < 0.5
            ):
                del _blast_bonus[self.node]
                _merge_bonus(self, msg, entry['amount'], bpos, entry['fdir'])

    if self._ab_active and self.node:
        if isinstance(msg, bs.HitMessage):
            _absorb_hit(self, msg)
            return True
        if isinstance(msg, bs.FreezeMessage):
            _snd('block', 1.0, self.node.position)
            return None

    if isinstance(msg, PunchHitMessage) and self._ab_stored > 0 and self.node:
        pend = {
            'src': self.node,
            'amount': self._ab_stored * RELEASE_MULT,
            'used': False,
        }
        _punch_bonus[0] = pend
        try:
            result = _orig_handlemessage(self, msg)
        finally:
            _punch_bonus[0] = None
        if pend['used']:
            amount = _take_charge(self)
            _release_punch_fx(self, amount, pend.get('victim'))
        return result

    if isinstance(msg, bs.DieMessage):
        _clear_all(self)

    return _orig_handlemessage(self, msg)


def _patched_pickup_press(self: Spaz) -> None:
    if USE_DOUBLE_TAP_GRAB and hasattr(self, '_ab_active') and self.node:
        now = bs.time()
        double = now - self._ab_last_grab_tap <= DOUBLE_TAP_WINDOW
        self._ab_last_grab_tap = now
        if double and _can_shield(self):
            # The 2nd tap still grabs/throws as usual, plus the shield.
            self._ab_last_grab_tap = -999.0
            _orig_pickup_press(self)
            _activate_shield(self)
            return
    _orig_pickup_press(self)


def _patched_hold_position_press(self: Spaz) -> None:
    if USE_HOLD_POSITION and hasattr(self, '_ab_active') and _can_shield(self):
        _activate_shield(self)
    _orig_hold_position_press(self)


def _patched_drop_bomb(self: Spaz) -> Bomb | None:
    bomb = _orig_drop_bomb(self)
    if bomb is not None and getattr(self, '_ab_stored', 0) > 0:
        _power_up_bomb(self, bomb)
    return bomb


def _hook_take_charge(spaz: Spaz) -> float:
    """Spend the whole charge (with its glow); returns the damage."""
    if getattr(spaz, '_ab_stored', 0) <= 0:
        return 0.0
    return _take_charge(spaz)


def _hook_charge_projectile(spaz: Spaz, projectile: Any) -> bool:
    """Put the charge into a bomb-like projectile; True if it had one."""
    if getattr(spaz, '_ab_stored', 0) <= 0 or not spaz.node:
        return False
    _power_up_bomb(spaz, projectile)
    return True


# ba_meta export babase.Plugin
class AbsorbShieldPlugin(babase.Plugin):
    """Parry shield that absorbs damage and returns it with the next hit."""

    def __init__(self) -> None:
        # The mod may be both built into BSM and dropped into mods/;
        # only the first copy patches the game.
        if getattr(Spaz, '_ab_patched', False):
            return
        Spaz._ab_patched = True  # type: ignore[attr-defined]

        global _orig_init, _orig_handlemessage, _orig_pickup_press
        global _orig_hold_position_press, _orig_drop_bomb
        _orig_init = Spaz.__init__
        _orig_handlemessage = Spaz.handlemessage
        _orig_pickup_press = Spaz.on_pickup_press
        _orig_hold_position_press = Spaz.on_hold_position_press
        _orig_drop_bomb = Spaz.drop_bomb

        # Hooks other BSM plugins use to spend the charge (see boosters.py).
        Spaz.bsm_take_charge = staticmethod(_hook_take_charge)
        Spaz.bsm_charge_projectile = staticmethod(_hook_charge_projectile)

        Spaz.__init__ = _patched_init
        Spaz.handlemessage = _patched_handlemessage
        Spaz.on_pickup_press = _patched_pickup_press
        Spaz.on_hold_position_press = _patched_hold_position_press
        Spaz.drop_bomb = _patched_drop_bomb
