from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Union
import os

import tcod

from actions import (
    Action,
    BumpAction,
    LookAroundAction,
    ObserveIdentityAction,
    ObserveInventoryAction,
    ObserveNeedsAction,
    ObserveRelationshipsAction,
    ObserveStatsAction,
    PickupAction,
    QueryAction,
    ReflectAction,
    WaitAction,
)
from game_time import tick
import actions
import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Item


MOVE_KEYS = {
    # Arrow keys.
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
}

WAIT_KEYS = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR,
}

CONFIRM_KEYS = {
    tcod.event.K_RETURN,
    tcod.event.K_KP_ENTER,
}

ActionOrHandler = Union[Action, "BaseEventHandler"]


class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    """An event handler return value which can trigger an action or switch active handlers.

    If a handler is returned then it will become the active handler for future events.
    If an action is returned it will be attempted and if it's valid then
    MainGameEventHandler will become the active handler.
    """

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle an event and return the next active event handler."""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} can not handle actions."
        return self

    def on_render(self, console: tcod.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Action | None:
        raise SystemExit()


class PopupMessage(BaseEventHandler):
    """Display a popup text window."""

    def __init__(self, parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text

    def on_render(self, console: tcod.Console) -> None:
        """Render the parent and dim the result, then print the message on top."""
        self.parent.on_render(console)
        console.tiles_rgb["fg"] //= 8
        console.tiles_rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg=color.white,
            bg=color.black,
            alignment=tcod.CENTER,
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> BaseEventHandler | None:
        """Any key returns to the parent handler."""
        return self.parent


class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            # A valid action was performed.
            if not self.engine.player.is_alive:
                # The player was killed sometime during or after the action.
                return GameOverEventHandler(self.engine)
            return MainGameEventHandler(self.engine)  # Return to the main handler.
        return self

    def handle_action(self, action: Action | None) -> bool:
        """Handle actions returned from event methods.

        Returns True if the action will advance a turn.
        """
        if action is None:
            return False
        assert action is not None  # for mypy

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.add_observation(exc.args[0], color.impossible)
            return False  # Skip enemy turn on exceptions.

        if not action.instant:
            tick()
        return True

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)


class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input."""

    def ev_keydown(self, event: tcod.event.KeyDown) -> ActionOrHandler | None:
        """By default any key exits this input handler."""
        if event.sym in {  # Ignore modifier keys.
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
            tcod.event.K_LGUI,
            tcod.event.K_RGUI,
            tcod.event.K_MODE,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> ActionOrHandler | None:
        """By default any mouse click exits this input handler."""
        return self.on_exit()

    def on_exit(self) -> ActionOrHandler | None:
        """Called when the user is trying to exit or cancel an action.

        By default this returns to the main event handler.
        """
        return MainGameEventHandler(self.engine)


class InventoryEventHandler(AskUserEventHandler):
    """This handler lets the user select an item.

    What happens then depends on the subclass.
    """

    TITLE = "<missing title>"

    def on_render(self, console: tcod.Console) -> None:
        """Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        Will move to a different position based on where the player is located, so the player can always see where
        they are.
        """
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        height = number_of_items_in_inventory + 2

        height = max(height, 3)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                console.print(x + 1, y + i + 1, f"({item_key}) {item.name}")
        else:
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> ActionOrHandler | None:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.add_observation("Invalid entry.", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> ActionOrHandler | None:
        """Called when the user selects a valid item."""
        raise NotImplementedError()


class InventoryActivateHandler(InventoryEventHandler):
    """Handle using an inventory item."""

    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> ActionOrHandler | None:
        """Return the action for the selected item."""
        return item.consumable.get_action(self.engine.player)


class InventoryDropHandler(InventoryEventHandler):
    """Handle dropping an inventory item."""

    TITLE = "Select an item to drop"

    def on_item_selected(self, item: Item) -> ActionOrHandler | None:
        """Drop this item."""
        return actions.DropItem(self.engine.player, item)


class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""

    def __init__(self, engine: Engine):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.tiles_rgb["bg"][x, y] = color.white
        console.tiles_rgb["fg"][x, y] = color.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> ActionOrHandler | None:
        """Check for key movement or confirmation keys."""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1  # Holding modifier keys will speed up key movement.
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            # Clamp the cursor index to the map size.
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None
        if key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> ActionOrHandler | None:
        """Left click confirms a selection."""
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> ActionOrHandler | None:
        """Called when an index is selected."""
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""

    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        """Return to main handler."""
        return MainGameEventHandler(self.engine)


class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected."""

    def __init__(self, engine: Engine, callback: Callable[[tuple[int, int]], Action | None]):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Action | None:
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""

    def __init__(
        self,
        engine: Engine,
        radius: int,
        callback: Callable[[tuple[int, int]], Action | None],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        x, y = self.engine.mouse_location

        # Draw a rectangle around the targeted area, so the player can see the affected tiles.
        console.draw_frame(
            x=x - self.radius - 1,
            y=y - self.radius - 1,
            width=self.radius**2,
            height=self.radius**2,
            fg=color.red,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Action | None:
        return self.callback((x, y))


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> ActionOrHandler | None:
        action: Action | None = None

        key = event.sym

        player = self.engine.player

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)

        elif key == tcod.event.K_ESCAPE:
            raise SystemExit()
        elif key == tcod.event.K_v:
            return ObservationsLogViewer(self.engine, self.engine.player)

        elif key == tcod.event.K_g:
            action = PickupAction(player)
        elif key == tcod.event.K_i:
            return InventoryActivateHandler(self.engine)
        elif key == tcod.event.K_d:
            return InventoryDropHandler(self.engine)
        elif key == tcod.event.K_q:
            return InputQueryHandler(self.engine, lambda query: QueryAction(player, query).perform())
        elif key == tcod.event.K_SLASH:
            return LookHandler(self.engine)
        elif key == tcod.event.K_l:
            return LookAroundAction(player)
        elif key == tcod.event.K_r:
            return ReflectAction(player)
        elif key == tcod.event.K_1:
            return ObserveStatsAction(player)
        elif key == tcod.event.K_2:
            return ObserveInventoryAction(player)
        elif key == tcod.event.K_3:
            return ObserveNeedsAction(player)
        elif key == tcod.event.K_4:
            return ObserveRelationshipsAction(player)
        elif key == tcod.event.K_5:
            return ObserveIdentityAction(player)

        # No valid key was pressed
        return action

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> ActionOrHandler | None:
        """Handle left clicks."""
        x, y = event.tile
        if event.button == 1 and self.engine.game_map.in_bounds(x, y) and self.engine.game_map.visible[x, y]:
            for actor in self.engine.game_map.actors:
                if actor.x == x and actor.y == y:
                    return ObservationsLogViewer(self.engine, actor)

        return super().ev_mousebuttondown(event)


class GameOverEventHandler(EventHandler):
    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")  # Deletes the active save file.
        raise exceptions.QuitWithoutSaving()  # Avoid saving a finished game.

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.K_ESCAPE:
            self.on_quit()


CURSOR_Y_KEYS = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: -10,
    tcod.event.K_PAGEDOWN: 10,
}


class InputQueryHandler(EventHandler):
    """Handles the input of a single line of text."""

    def __init__(self, engine: Engine, callback: Callable[[str], None]):
        super().__init__(engine)

        self.text: list[str] = []
        self.callback = callback

    def ev_keydown(self, event: tcod.event.KeyDown) -> ActionOrHandler | None:
        if event.sym == tcod.event.K_BACKSPACE:
            if len(self.text) > 0:
                self.text.pop()
        elif event.sym == tcod.event.K_SPACE:
            self.text.append(" ")
        elif event.sym == tcod.event.K_ESCAPE:
            return MainGameEventHandler(self.engine)
        elif event.sym == tcod.event.K_RETURN:
            self.callback("".join(self.text))
            return MainGameEventHandler(self.engine)
        else:
            self.text.append(event.sym.label)

        return None

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        console.print(1, 1, "".join(self.text))


class TextViewer(EventHandler):
    """Print the history on a larger window which can be navigated."""

    actor: Actor
    log_length: int
    cursor: int

    def ev_keydown(self, event: tcod.event.KeyDown) -> MainGameEventHandler | None:
        # Fancy conditional movement to make it feel right.
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.K_HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.sym == tcod.event.K_END:
            self.cursor = self.log_length - 1  # Move directly to the last message.
        else:  # Any other key moves back to the main game state.
            return MainGameEventHandler(self.engine)
        return None


class ObservationsLogViewer(TextViewer):
    def __init__(self, engine: Engine, actor: Actor):
        super().__init__(engine)
        self.actor = actor
        self.log_length = len(actor.observation_log.observations)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)
        log_console = tcod.Console(console.width - 6, console.height - 6)

        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0,
            0,
            log_console.width,
            1,
            f"┤Observations of {self.actor.name} ({self.actor.kind.name})├",
            alignment=tcod.CENTER,
        )

        # Render the message log using the cursor parameter.
        self.actor.observation_log.render_observations(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.actor.observation_log.observations[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)
