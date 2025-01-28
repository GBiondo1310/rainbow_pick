from pick import (
    Picker,
    curses,
    SYMBOL_CIRCLE_EMPTY,
    Container,
    Iterable,
    List,
    Optional,
    Sequence,
    Union,
    Option,
    textwrap,
    OPTION_T,
    Position,
)

SYMBOL_CIRCLE_FILLED = "(✔)"


class RainbowPicker(Picker):
    def __init__(
        self,
        options: Sequence[OPTION_T],
        title: Optional[str] = None,
        indicator: str = "->",
        default_index: int = 0,
        multiselect: bool = False,
        min_selection_count: int = 0,
        screen: Optional["curses._CursesWindow"] = None,
        position: Position = Position(0, 0),
        clear_screen: bool = True,
        quit_keys: Optional[Union[Container[int], Iterable[int]]] = None,
    ):
        super().__init__(
            options,
            title,
            indicator,
            default_index,
            multiselect,
            min_selection_count,
            screen,
            position,
            clear_screen,
            quit_keys,
        )

    def draw(self, screen: "curses._CursesWindow") -> None:
        """draw the curses ui on the screen, handle scroll if needed"""
        if self.clear_screen:
            screen.clear()

        y, x = self.position  # start point

        max_y, max_x = screen.getmaxyx()
        max_rows = max_y - y  # the max rows we can draw

        lines, current_line = self.get_lines(max_width=max_x)

        # calculate how many lines we should scroll, relative to the top
        scroll_top = 0
        if current_line > max_rows:
            scroll_top = current_line - max_rows

        lines_to_draw = lines[scroll_top : scroll_top + max_rows]

        description_present = False
        for option in self.options:
            if isinstance(option, Option) and option.description is not None:
                description_present = True
                break

        title_length = len(self.get_title_lines(max_width=max_x))

        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i, i, -1)

        for i, line in enumerate(lines_to_draw):
            if i == 0:
                screen.addstr(y, x, "", max_x // 2 - 2)
                screen.addstr(line, curses.color_pair(4))
            elif description_present and i > title_length:
                screen.addstr(y, x, "", max_x // 2 - 2)
                screen.addstr(line, curses.color_pair(0))
            else:
                screen.addstr(y, x, "", max_x - 2)
                if self.indicator + " ( )" in line or self.indicator in line:
                    screen.addstr(line, curses.color_pair(3))
                elif "(✔)" in line:
                    screen.addstr(line, curses.color_pair(2))
                else:
                    screen.addstr(line, curses.color_pair(0))

            y += 1

        option = self.options[self.index]
        if isinstance(option, Option) and option.description is not None:
            description_lines = textwrap.fill(option.description, max_x // 2 - 2).split(
                "\n"
            )

            for i, line in enumerate(description_lines):
                screen.addstr(
                    i + title_length, max_x // 2, line, max_x - 2, curses.color_pair(1)
                )

        screen.refresh()

    def get_option_lines(self) -> List[str]:
        lines: List[str] = []
        for index, option in enumerate(self.options):
            if index == self.index:
                prefix = "    " + self.indicator
            else:
                prefix = len(self.indicator) * " "

            if self.multiselect:
                symbol = (
                    SYMBOL_CIRCLE_FILLED
                    if index in self.selected_indexes
                    else SYMBOL_CIRCLE_EMPTY
                )
                prefix = f"{prefix} {symbol}"

            option_as_str = option.label if isinstance(option, Option) else option
            lines.append(f"{prefix} {option_as_str}")

        return lines


def rainbow_pick(
    options: Sequence[OPTION_T],
    title: Optional[str] = None,
    indicator: str = "->",
    default_index: int = 0,
    multiselect: bool = False,
    min_selection_count: int = 0,
    screen: Optional["curses._CursesWindow"] = None,
    position: Position = Position(0, 0),
    clear_screen: bool = True,
    quit_keys: Optional[Union[Container[int], Iterable[int]]] = None,
):
    rpicker: RainbowPicker = RainbowPicker(
        options,
        title,
        indicator,
        default_index,
        multiselect,
        min_selection_count,
        screen,
        position,
        clear_screen,
        quit_keys,
    )
    return rpicker.start()
