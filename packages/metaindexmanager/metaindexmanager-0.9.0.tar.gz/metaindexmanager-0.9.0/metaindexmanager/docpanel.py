"""A panel to browse files by their metadata"""
import shlex
import curses
from pathlib import Path

from cursedspace import Panel
from cursedspace import Completion

from metaindexmanager import command
from metaindexmanager import utils
from metaindexmanager import clipboard
from metaindexmanager.utils import logger
from metaindexmanager.panel import ListPanel, register


DEFAULT_COLUMNS = "title filename tags+ mimetype"
DEFAULT_SHOW_OFFLINE = "no"
DEFAULT_ONLINE_ICONS = ' -'


class Row:
    """A row in the list of documents"""
    def __init__(self, panel, item):
        self.panel = panel
        self.item = item
        self.columns = []

    def add(self, columntype, *args, **kwargs):
        """Append an instance of this columntype to the row

        Returns the new instance"""
        self.columns.append(columntype(self, *args, **kwargs))
        return self.columns[-1]

    def __lt__(self, other):
        return self.comparator() < other.comparator()

    def comparator(self):
        textcolumns = [c for c in self.columns if isinstance(c, TextColumn)]
        if len(textcolumns) == 0:
            return [self.item['mimetype'][0]]
        return [len(textcolumns[0]) == 0] + \
               [c.text(50).lower() for c in textcolumns]


class Column:
    """A column in a document list row"""
    def __init__(self, row):
        self.row = row

    def panel(self):
        return self.row.panel

    def app(self):
        return self.row.panel.app

    def __len__(self):
        return 0

    def text(self, maxlength):
        """Return the text of the column, reduced to the given maxlength"""
        return ""


class TextColumn(Column):
    """A simple column, showing text"""
    def __init__(self, row, key):
        super().__init__(row)
        self.key = key
        self.value = ""
        self.update_value()

    def update_value(self):
        values = []
        key = self.key
        multivalue = False
        if key.endswith('+'):
            key = key[:-1]
            multivalue = True

        for expandedkey in set(self.panel().synonyms.get(key, [key])):
            values += [self.app().as_printable(v)
                       for v in self.row.item[expandedkey]]
        values.sort()

        if len(values) == 0:
            return

        if multivalue and len(values) > 1:
            self.value = ", ".join([v for v in values if len(v.strip()) > 0])
        else:
            self.value = values[0]

        self.value = self.value.replace("\n", " ") \
                               .replace("\r", " ") \
                               .replace("\t", " ")

    def __len__(self):
        return len(self.value)

    def text(self, maxlength):
        return self.value[:maxlength]


class MimetypeIconColumn(Column):
    """A mimetype icon"""

    def __len__(self):
        return 1

    def text(self, maxlength):
        return utils.get_ls_icon(Path(self.row.item.path), {})


class OnlineStatusColumn(Column):
    """The icon whether or not an item is online"""

    def __len__(self):
        return 1

    def text(self, maxlength):
        return self.row.panel.online_icon if self.row.item.path.exists() \
               else self.row.panel.offline_icon


@register
class DocPanel(ListPanel):
    SCOPE = 'documents'

    CONFIG_COLUMNS = 'columns'
    CONFIG_SHOW_OFFLINE = 'show-offline'
    CONFIG_ONLINE_ICONS = 'online-icons'

    def __init__(self, application, searchterm=''):
        super().__init__(application)
        self.col_widths = []
        self.fieldkeys = []
        self.query = None
        self.post_load = None
        self.show_offline = False
        self.online_icon, self.offline_icon = DEFAULT_ONLINE_ICONS[:2]
        self.results = []

        self.configuration_changed()
        self.search(searchterm)

    @property
    def synonyms(self):
        return self.app.metaindexconf.synonyms

    def title(self):
        if self.query is None or len(self.query.strip()) == 0:
            return '(all documents)'
        return str(self.query)

    def on_focus(self):
        if self.selected_item is not None:
            self.paint_item(self.selected_item)

    def on_focus_lost(self):
        if self.selected_item is not None:
            self.paint_item(self.selected_item)
            self.win.noutrefresh()

    def on_copy(self, item):
        if self.is_busy:
            raise RuntimeError("Cannot copy right now: busy")
        return clipboard.ClipboardItem(item[-1].path, self)

    def configuration_changed(self, name=None):
        super().configuration_changed(name)

        changed = False
        must_repaint = False

        if name is None or name == self.CONFIG_COLUMNS:
            keys = self.app.configuration.list(self.SCOPE,
                                               self.CONFIG_COLUMNS,
                                               DEFAULT_COLUMNS,
                                               separator=' ')

            changed = self.fieldkeys != keys
            self.fieldkeys = keys

        if name is None or name == self.CONFIG_SHOW_OFFLINE:
            value = self.app.configuration.bool(self.SCOPE,
                                                self.CONFIG_SHOW_OFFLINE,
                                                DEFAULT_SHOW_OFFLINE)
            changed = self.show_offline != value
            self.show_offline = value

        if name is None or name == self.CONFIG_ONLINE_ICONS:
            value = self.app.configuration.get(self.SCOPE,
                                               self.CONFIG_ONLINE_ICONS,
                                               DEFAULT_ONLINE_ICONS)
            if len(value) >= 2:
                value = (value[0], value[1])
                must_repaint = value != (self.online_icon, self.offline_icon)
                self.online_icon, self.offline_icon = value

        if changed:
            must_repaint = True
            self.rebuild_items()
            self.calculate_grid_size()

        if must_repaint and self.win is not None:
            self.scroll()
            self.paint(True)

    def search(self, query):
        logger.debug(f"DocPanel: search for {query}")
        self.query = query
        self.run_in_background(self.do_search)

    def do_search(self):
        if not self.app.cache.is_initialized:
            self.app.cache.wait_for_reload()
        self.results = list(self.app.cache.find(self.query))
        self.cursor = 0
        self.rebuild_items()
        self.calculate_grid_size()
        if self.post_load is not None:
            self.post_load()
            self.post_load = None
        self.app.callbacks.put((self, lambda: True))

    def rebuild_items(self):
        maxwidth = self.content_area()[3]
        self.items = [self.make_row(result)
                      for result in self.results
                      if self.show_offline or result.path.exists()]
        self.items = [row
                      for row in self.items
                      if sum(len(column.text(maxwidth))
                             for column in row.columns) > 0]
        self.items.sort()

    def make_row(self, entry):
        logger.debug("make_row %s", entry.metadata)
        row = Row(self, entry)
        for key in self.fieldkeys:
            if key == 'icon':
                row.add(MimetypeIconColumn)
            elif key == 'online':
                row.add(OnlineStatusColumn)
            else:
                row.add(TextColumn, key)

        return row

    def calculate_grid_size(self):
        if self.win is None:
            return
        # calculate the spread of the grid prior to calling super.paint
        _, _, _, maxwidth = self.content_area()
        maxwidth -= 1 # leave one column for the cursor

        if len(self.fieldkeys) == 0:
            self.col_widths = [0]
            return

        # recalculate how wide each column is
        equal_colwidth = maxwidth//len(self.fieldkeys)
        self.col_widths = [max([0] + [max(2 if fkey in ['icon', 'online'] else equal_colwidth,
                                      len(row.columns[fkidx].text(maxwidth)))+1
                                      for row in self.items])
                           for fkidx, fkey in enumerate(self.fieldkeys)]

        # shrink each column if its wider than the equal_colwidths, start from
        # the last column (it's probably the least important)
        if len(self.col_widths) > 2:
            to_shrink = len(self.col_widths)-1
            while sum(self.col_widths) > maxwidth and to_shrink >= 0:
                self.col_widths[to_shrink] = min(equal_colwidth, self.col_widths[to_shrink])
                to_shrink -= 1
        # expand/shrink the last column to the rest of the available space
        self.col_widths[-1] = maxwidth - sum(self.col_widths[:-1])

        assert sum(self.col_widths) <= maxwidth
        logger.debug("Resized columns: %s (maxwidth: %s)",
                     self.col_widths, maxwidth)

    def resize(self, *args):
        super().resize(*args)
        self.calculate_grid_size()

    def paint(self, clear=False):
        if self.is_busy:
            Panel.paint(self, clear)
            x, y = 0, 0
            if (self.border & self.BORDER_TOP) != 0:
                y += 1
            if (self.border & self.BORDER_LEFT) != 0:
                x += 1
            self.win.addstr(y, x, "...")
            self.win.noutrefresh()
        else:
            super().paint(clear)

    def do_paint_item(self, y, x, maxwidth, is_selected, item):
        attr = curses.A_STANDOUT \
               if is_selected and self.app.current_panel is self \
               else curses.A_NORMAL

        # clean up
        try:
            self.win.addstr(y, x, " "*maxwidth, attr)
        except curses.error:
            pass

        # one character width space to the left
        x += 1

        # indent for multiselection
        if item in self.multi_selection:
            self.win.addstr(x, y, '  ', attr)
            x += 2

        # paint value per column
        for column in range(len(self.fieldkeys)):
            if self.col_widths[column] < 2:
                continue
            text = item.columns[column].text(self.col_widths[column])
            if column < len(self.fieldkeys) - 1 and len(text) >= self.col_widths[column]:
                text = text[:-1] + ' '
            if len(text) + x > maxwidth:
                text = text[:maxwidth-x]

            try:
                self.win.addstr(y, x, text, attr)
            except curses.error:
                pass

            x += self.col_widths[column]

    def display_text(self, item):
        """Returns an array of all columns that should be displayed for this item"""
        return [item.columns[column].text(50)
                for column in range(len(self.fieldkeys))]

    def line_matches_find(self, cursor):
        if self.items is None or self.find_text is None:
            return False
        item = self.items[cursor]
        texts = self.display_text(item)
        if self.app.configuration.find_is_case_sensitive:
            return any(self.find_text in text for text in texts)
        return any(self.find_text.lower() in text.lower() for text in texts)

    def jump_to(self, item, path=None):
        if path is None:
            path = self.query

        if path != self.query:
            self.search(path)

        if self.is_busy:
            logger.debug("postponing jump to %s", item)
            self.post_load = lambda: self.do_jump_to(item)
            return

        self.do_jump_to(item)

    def do_jump_to(self, item):
        targetitem = str(item)

        for cursor, row in enumerate(self.items):
            if str(row.item.path) == targetitem:
                self.cursor = cursor
                break

        self.scroll()
        if not self.is_busy:
            self.paint()

    @property
    def selected_path(self):
        result = self.selected_item
        if result is not None:
            result = Path(result.item.path)
        return result

    @property
    def selected_paths(self):
        return [Path(row.item.path)
                for row in self.selected_items
                if row is not None]

    def open_selected(self):
        if self.selected_item is None:
            self.app.error("Nothing selected")
            return
        path = Path(self.selected_item.item.path)
        if path.is_file():
            self.app.open_file(path)
        else:
            self.app.error(f"File '{path}' not found")

    def open_selected_with(self, cmd):
        if self.selected_item is None:
            self.app.error("Nothing selected")
            return
        path = Path(self.selected_item.item.path)
        if path.is_file():
            self.app.open_with(path, cmd)
        else:
            self.app.error(f"File '{path}' not found")


@command.registered_command
class NewMetaPanel(command.Command):
    """Create a new metadata panel"""
    NAME = 'new-documents-panel'

    def execute(self, context):
        if context.panel.is_busy:
            return

        panel = DocPanel(context.application)
        context.application.add_panel(panel)
        context.application.activate_panel(panel)


class SearchTagSuggestion(Completion.Suggestion):
    def __lt__(self, other):
        if isinstance(other, SearchTagSuggestion):
            return ['.' in self.text, str(self)] < ['.' in other.text, str(other)]


@command.registered_command
class Search(command.Command):
    """Search documents with this metaindex search term"""
    NAME = 'search'
    ACCEPT_IN = (DocPanel,)

    def completion_options(self, context, *args):
        docpanel = context.application.previous_focus
        if not isinstance(docpanel, DocPanel):
            return []

        if len(args) == 0:
            partial = ''
        else:
            partial = args[-1]

        if ':' in partial:
            return []

        synonyms = set(context.application.metaindexconf.synonyms.keys())

        suggestions = [SearchTagSuggestion(tag + ':', tag)
                       for tag in set(context.application.cache.keys()) | synonyms
                       if len(partial) == 0 or partial in tag]
        suggestions.sort()

        return suggestions

    def execute(self, context, *args):
        if context.panel.is_busy:
            return

        term = shlex.join(args)
        context.panel.search(term)
        context.panel.paint(clear=True)
        context.application.paint_focus_bar()


@command.registered_command
class SetColumns(command.Command):
    """Set the columns of this panel"""
    NAME = 'columns'
    ACCEPT_IN = (DocPanel,)

    def execute(self, context, *args):
        if len(args) == 0:
            context.application.info(f"columns = {' '.join(context.panel.fieldkeys)}")
            return

        if context.panel.is_busy:
            return

        context.panel.fieldkeys = args
        context.panel.rebuild_items()
        if context.panel.cursor >= len(context.panel.items):
            context.panel.cursor = len(context.panel.items)-1
        if context.panel.win is not None:
            context.panel.calculate_grid_size()
            context.panel.scroll()
            context.panel.paint(True)


@command.simple_command("toggle-show-offline", accept_in=(DocPanel,))
def toggle_show_offline_command(context):
    """Toggle whether or not to show offline files"""
    if context.panel.is_busy:
        return

    docpanel = context.panel
    docpanel.show_offline = not docpanel.show_offline
    docpanel.rebuild_items()
    docpanel.calculate_grid_size()
    docpanel.scroll()
    docpanel.paint(True)
