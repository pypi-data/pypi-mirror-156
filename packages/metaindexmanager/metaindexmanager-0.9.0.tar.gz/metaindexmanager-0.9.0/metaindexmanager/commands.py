import pathlib
import tempfile
import subprocess
import string
import datetime

from cursedspace import ShellContext, InputLine

import metaindex.shared
import metaindex.indexer
import metaindex.indexers
import metaindex.ocr
import metaindex.stores
from metaindex import index_files, CacheEntry

from metaindexmanager import layouts
from metaindexmanager import utils
from metaindexmanager.command import registered_command, Command, simple_command
from metaindexmanager.docpanel import DocPanel
from metaindexmanager.filepanel import FilePanel
from metaindexmanager.detailpanel import DetailPanel
from metaindexmanager.keyhelppanel import KeyHelpPanel
from metaindexmanager.editorpanel import EditorPanel
from metaindexmanager.utils import parse_key_sequence, logger


@registered_command
class QuitCommand(Command):
    """Quit metaindexmanager"""
    NAME = 'quit'

    def execute(self, context):
        for panel in context.application.panels:
            panel.on_close()
        context.application.panels = []


@registered_command
class ClosePanel(Command):
    """Close the current panel"""
    NAME = 'close'

    def execute(self, context):
        context.application.close_panel(context.panel)


@registered_command
class OpenItem(Command):
    """Open the selected file or folder"""
    NAME = 'open'
    ACCEPT_IN = (DocPanel, FilePanel, EditorPanel)

    def execute(self, context):
        context.panel.open_selected()


@registered_command
class OpenItemWith(Command):
    """Open the selected file or folder with a user-specified program"""
    NAME = 'open-with'
    ACCEPT_IN = (DocPanel, FilePanel, EditorPanel)

    def completion_options(self, context, *args):
        if len(args) == 0 or len(args[0]) == 0:
            return [p.name for p in context.application.known_programs]

        return [p.name for p in context.application.known_programs
                if args[0] in p.name]

    def execute(self, context, *args):
        context.panel.open_selected_with(list(args))


@registered_command
class FocusNextPanel(Command):
    """Put the focus on the next panel"""
    NAME = 'next-panel'

    def execute(self, context):
        if context.panel not in context.application.panels:
            return
        idx = context.application.panels.index(context.panel)
        next_panel = context.application.panels[(idx + 1) % len(context.application.panels)]
        context.application.activate_panel(next_panel)


@registered_command
class FocusPreviousPanel(Command):
    """Put the focus on the next panel"""
    NAME = 'previous-panel'

    def execute(self, context):
        if context.panel not in context.application.panels:
            return
        idx = context.application.panels.index(context.panel)
        next_panel = context.application.panels[(idx - 1) % len(context.application.panels)]
        context.application.activate_panel(next_panel)


class PanelNumberReader(InputLine):
    def __init__(self, application):
        height, width = application.size()
        super().__init__(application, width, (height-1, 0), prefix="Focus panel: ")

    def handle_key(self, key):
        self.app.activate_panel(self.app.previous_focus)
        self.destroy()
        if len(str(key)) == 1 and str(key) in string.digits:
            FocusPanel.do_focus_panel(self.app, int(str(key)))
        self.app.hide_key_help()
        self.app.paint()


@registered_command
class FocusPanel(Command):
    """Focus the named panel"""
    NAME = 'focus'

    def execute(self, context, panel=None):
        if panel is None:
            lines = [(str(idx+1), panel.title())
                     for idx, panel in enumerate(context.application.panels)]
            panel = KeyHelpPanel(lines, context.application)
            context.application.key_help_panel = panel
            panel.autosize()
            reader = PanelNumberReader(context.application)
            context.application.activate_panel(reader)
            context.application.paint()
            return

        try:
            panel = int(panel)
        except:
            context.application.error(f"Not a number: {panel}")
            return

    @staticmethod
    def do_focus_panel(application, panelnr):
        # panelnr is 1-based
        if 0 < panelnr <= len(application.panels):
            application.activate_panel(application.panels[panelnr-1])


@registered_command
class EnterCommandMode(Command):
    """Start the command input field"""
    NAME = 'enter-command'

    def execute(self, context, text=""):
        if context.application.command_input is not None:
            return
        context.application.make_command_input(text)
        context.application.previous_focus = context.panel
        context.application.activate_panel(context.application.command_input)
        context.application.paint()
        logger.debug("Enter command input")


@registered_command
class CancelCommandInput(Command):
    """Unfocus the command input field"""
    NAME = 'cancel-command'

    def execute(self, context):
        context.application.command_input.destroy()
        context.application.command_input = None
        context.application.activate_panel(context.application.previous_focus)
        context.application.previous_focus = None
        context.application.paint()
        logger.debug(f"cancel command input")


@registered_command
class Repaint(Command):
    """Enforce repainting of screen"""
    NAME = 'repaint'

    def execute(self, context):
        context.application.resize_panels()
        context.application.paint(True)
        context.application.screen.noutrefresh()


@registered_command
class EditMetadataExternally(Command):
    """Launch an external text editor to edit the metadata of the selected file"""
    NAME = 'edit-metadata-external'
    ACCEPT_IN = (DocPanel, FilePanel, EditorPanel)

    def execute(self, context):
        target = context.panel
        file = target.selected_path

        # ensure there is something to edit
        if file is None:
            logger.debug("No file to edit")
            context.application.error("Nothing selected")
            return

        app = context.application

        # Try to find an existing, non-collection
        sidecar = None
        store = None
        is_collection = False
        for fname, is_collection in app.metaindexconf.find_all_sidecar_files(file):
            sidecar = fname
            store = metaindex.stores.BY_SUFFIX.get(sidecar.suffix)
            break

        if sidecar is None:
            fname, is_collection, store_ = app.metaindexconf.resolve_sidecar_for(file)
            if fname is not None:
                sidecar = fname
                store = store_

        if store is None or sidecar is None:
            app.error("No store set up to write into")
            return

        if sidecar == file or app.metaindexconf.is_sidecar_file(file):
            context.application.error("Cannot edit metadata of a file that's "
                                      "probably a metadata file")
            return

        if sidecar.is_file():
            if is_collection:
                meta = store.get_for_collection(sidecar, '')
                if file not in meta:
                    is_collection = False
                    meta = CacheEntry(file)
                else:
                    meta = meta[file]
            else:
                meta = store.get(sidecar)
                meta.pop(metaindex.shared.IS_RECURSIVE)

        else:
            # get the metadata for the selected item as a dict
            results = app.cache.get(file)
            logger.debug(f"Cached metadata for {file}: {results}")
            if len(results) > 0:
                meta = results[0]
            else:
                meta = CacheEntry(file)

        # resolve the external editor
        editor = context.application.get_text_editor(True)
        if editor is None:
            return

        # create the temporary file to edit
        with tempfile.NamedTemporaryFile("w+t", encoding="utf-8", suffix=sidecar.suffix) as fh:
            store.store(meta, fh)
            fh.flush()
            original = fh.read()
            with ShellContext(context.application.screen):
                subprocess.run(editor + [fh.name], check=False)
            context.application.paint(True)
            fh.flush()
            fh.seek(0)
            new_content = fh.read()
            fh.seek(0)
            changed = new_content != original
            if is_collection:
                updated = store.get_for_collection(fh, file.parent)
                updated = updated[file.parent]
            else:
                updated = store.get(fh)
                updated.pop(metaindex.shared.IS_RECURSIVE)

        if changed:
            store.store(updated, sidecar)
            context.application.cache.refresh(file)

            if isinstance(target, DocPanel):
                target.search(target.query)
                target.jump_to(file)
            elif isinstance(target, EditorPanel):
                target.reload()


@registered_command
class SelectFileAndExit(Command):
    """Write the selected file path to the requested location and exit"""
    NAME = 'select-and-exit'
    ACCEPT_IN = (DocPanel, FilePanel)

    def execute(self, context, *args):
        target = context.panel
        if target.is_busy:
            return

        if not context.application.select_file_mode:
            return

        item = target.items[target.cursor]
        path = None
        if isinstance(target, DocPanel):
            path = pathlib.Path(item[-1][0])
        elif isinstance(target, FilePanel):
            path = item
        else:
            return

        logger.debug(f"Selected file {path}")
        context.application.selected_file = path

        context.application.execute_command('quit')


@registered_command
class RefreshPanel(Command):
    """Refresh the current panel"""
    NAME = 'refresh'
    ACCEPT_IN = (DocPanel, FilePanel)

    def execute(self, context):
        if context.panel.is_busy:
            return

        target = context.panel
        logger.debug(f"Refresh {target}")

        if isinstance(target, DocPanel):
            target.search(target.query)
        elif isinstance(target, FilePanel):
            target.change_path(target.path)
        target.paint(True)


@registered_command
class DeleteItem(Command):
    """Delete selected item"""
    ACCEPT_IN = (FilePanel,)
    NAME = 'rm'

    def execute(self, context):
        if context.panel.is_busy:
            return

        context.panel.delete(context.panel.selected_paths)


class BookmarkNameReader(InputLine):
    def __init__(self, application, prefix):
        height, width = application.size()
        application.clear_info_text()
        super().__init__(application, width, (height-1, 0), prefix=prefix)

    def handle_key(self, key):
        self.app.activate_panel(self.app.previous_focus)
        self.win.erase()
        self.win.noutrefresh()
        self.destroy()
        if len(str(key)) == 1 and str(key) in string.ascii_letters:
            self.bookmark_selected(str(key))
        else:
            self.text = None
        self.app.paint(True)

    def bookmark_selected(self, mark):
        raise NotImplementedError("Must be implemented in subclasses")


class LoadBookmarkNameReader(BookmarkNameReader):
    def __init__(self, application):
        super().__init__(application, 'Bookmark to load: ')

    def handle_key(self, key):
        self.app.hide_key_help()
        super().handle_key(key)

    def bookmark_selected(self, mark):
        self.app.load_bookmark(mark)


class CreateBookmarkNameReader(BookmarkNameReader):
    def __init__(self, application, panel):
        super().__init__(application, 'Letter for the bookmark: ')
        self.target_panel = panel

    def bookmark_selected(self, mark):
        BookmarkItem.create_bookmark(mark, self.app, self.target_panel)


@registered_command
class BookmarkItem(Command):
    """Bookmark the selected item"""
    NAME = 'mark'
    ACCEPT_IN = (FilePanel, DocPanel)

    def execute(self, context, mark=None):
        if context.panel.is_busy:
            return

        if mark is None:
            reader = CreateBookmarkNameReader(context.application, context.panel)
            context.application.activate_panel(reader)
            context.application.paint()
            return

        self.create_bookmark(mark, context.application, context.panel)

    @staticmethod
    def create_bookmark(mark, application, panel):
        item = panel.selected_path

        if isinstance(panel, DocPanel):
            path = panel.query
        elif isinstance(panel, FilePanel):
            path = panel.path
        else:
            logger.error(f"Programming error: BookmarkItem command does not accept {type(target)}")
            return

        application.save_bookmark(mark, panel, path, item)


@registered_command
class JumpToBookmark(Command):
    """Open and jump to bookmark"""
    NAME = 'jump-to-mark'

    def execute(self, context, mark=None):
        if len(context.application.bookmarks) == 0:
            context.application.error("No bookmarks defined")
            return

        if mark is None:
            lines = [(mark, str(loc[1])) for mark, loc in context.application.bookmarks.items()]
            context.application.key_help_panel = KeyHelpPanel(lines, context.application)
            context.application.key_help_panel.autosize()
            reader = LoadBookmarkNameReader(context.application)
            context.application.activate_panel(reader)
            context.application.paint()
            return

        context.application.load_bookmark(mark)


@registered_command
class ChangeLayout(Command):
    """Change the layout"""
    NAME = 'layout'

    def execute(self, context, layout=None):
        accepted = layouts.layouts()
        cls = layouts.get_layout(layout)
        if cls is None or layout not in accepted:
            context.application.error(f"Possible layouts are: {', '.join(accepted)}")
            return

        context.application.layout = cls(context.application)
        context.application.resize_panels()
        context.application.paint(True)

    def completion_options(self, context, *args):
        text = "" if len(args) == 0 else args[0]
        return [layout for layout in sorted(layouts.layouts()) if layout.startswith(text)]


@registered_command
class GoToLocation(Command):
    """Open the folder of this document"""
    NAME = 'go-to-location'
    ACCEPT_IN = (DocPanel, DetailPanel, EditorPanel)

    def execute(self, context):
        if context.panel.is_busy:
            return

        path = context.panel.selected_path
        logger.debug(f"Opening {path} in new file panel")

        context.application.execute_command('new-file-panel')

        filepanel = context.application.panels[-1]
        filepanel.jump_to(path)

        context.application.paint(True)


@registered_command
class LoadConfig(Command):
    """Load the given configuration file"""
    NAME = 'source'

    def execute(self, context, path=None):
        if path is None:
            context.application.error(f"No path to configuration file given")
            return

        path = pathlib.Path(path).expanduser()

        if not path.is_file():
            msg = f"{path} does not exist or is not a file."
            logger.error(msg)
            context.application.error(msg)
            return

        context.application.load_config_file(path, context)


@simple_command('bind')
def bind_command(context, *args):
    """Set the keybinding to this command"""
    if len(args) < 3:
        context.application.error("Usage: bind scope keys command [help text]")
        return

    scope = args[0]
    keys = parse_key_sequence(args[1])
    context.application.keys.append((scope, keys, args[2:]))


@registered_command
class SetCommand(Command):
    """Set a configuration option"""
    NAME = 'set'

    def completion_options(self, context, *args):
        options = []
        if len(args) < 2:
            text = args[0] if len(args) > 0 else ""
            for group in sorted(context.application.configuration.conf.sections()):
                for option in sorted(context.application.configuration.conf[group]):
                    full = group + "." + option
                    if full.startswith(text):
                        options.append(group + "." + option)

        return options

    def execute(self, context, name=None, *values):
        if name is None:
            context.application.error("Usage: set name [value]")
            return

        if '.' in name:
            scope, name = name.split('.', 1)
        else:
            scope = 'all'

        if len(values) == 0:
            value = context.application.configuration.get(scope, name, '')
            context.application.info(f"{name}: {value}")
            return

        value = ' '.join(values)

        context.application.configuration.set(scope, name, value)
        context.application.configuration_changed((scope, name))


@simple_command('select', (FilePanel,))
def select_command(context):
    """Toggle whether or not the current item is selected"""

    panel = context.panel
    if panel.is_busy:
        return

    item = panel.selected_item
    if item in panel.multi_selection:
        panel.multi_selection.remove(item)
    else:
        panel.multi_selection.append(item)
    panel.paint_item(panel.cursor)
    panel.handle_key(panel.SCROLL_NEXT[0])


@registered_command
class ClearSelection(Command):
    """Unselect all selected items"""
    NAME = 'clear-selection'
    ACCEPT_IN = (FilePanel, DocPanel)

    def execute(self, context):
        if context.panel.is_busy:
            return

        indexes = [idx for idx, item in enumerate(context.panel.items)
                   if item in context.panel.multi_selection]
        context.panel.multi_selection = []
        for index in indexes:
            context.panel.paint_item(index)


@registered_command
class InvertSelection(Command):
    """Invert selection"""
    NAME = 'invert-selection'
    ACCEPT_IN = (FilePanel,)

    def execute(self, context):
        if context.panel.is_busy:
            return

        context.panel.multi_selection = [item for item in context.panel.items
                                         if item not in context.panel.multi_selection]
        context.panel.paint()


@simple_command("find")
def find_command(context, *args):
    """Find text in the current panel"""
    if context.panel.is_busy:
        context.application.error("Panel is currently busy")
        return

    context.panel.find(" ".join(args))


@simple_command("find-next")
def find_next_command(context):
    """Find the next occurrence"""
    if context.panel.is_busy:
        context.appliaction.error("Panel is currently busy")
        return

    context.panel.find_next()


@simple_command("find-prev")
def find_previous_command(context):
    """Find the previous occurrence"""
    if context.panel.is_busy:
        context.appliaction.error("Panel is currently busy")
        return

    context.panel.find_previous()


@registered_command
class RunOCR(Command):
    """Run OCR for this document"""
    NAME = 'ocr'
    ACCEPT_IN = (DocPanel, FilePanel, EditorPanel)

    def execute(self, context, languages=None):
        if context.panel.is_busy:
            return

        kwargs = {}
        if languages is not None:
            kwargs = {'languages': languages}

        path = context.panel.selected_path

        context.panel.run_blocking(self.run_ocr, context, path, **kwargs)
        context.application.paint(True)

    def run_ocr(self, blocker, context, path, **kwargs):
        blocker.title(f"Running OCR on {path.name}")
        success, fulltext = utils.do_ocr(path, **kwargs)

        if not success:
            logger.debug(f"OCR indexer returned nothing")
            context.application.info("OCR did not find anything useful")
            return

        meta = context.application.cache.get(path, False)
        if len(meta) == 0:
            meta = CacheEntry(path)
        else:
            meta = meta[0][1]

        meta.add('ocr.fulltext', fulltext)
        logger.debug(f"New metadata to write: {meta}")
        context.application.cache.insert(path, meta)

        if isinstance(context.panel, (DocPanel,)):
            context.application.callbacks.put((context.panel,
                                               lambda: context.panel.search(context.panel.query)))
        elif isinstance(context.panel, (EditorPanel,)):
            context.panel.reload()
            context.application.callbacks.put((context.panel,
                                               lambda: context.panel.paint(True)))


@registered_command
class RunIndexers(Command):
    """Run indexers on the selected document"""
    NAME = 'index'
    ACCEPT_IN = (DocPanel, FilePanel, EditorPanel)

    def execute(self, context):
        if context.panel.is_busy:
            return

        path = context.panel.selected_path
        context.panel.run_blocking(self.run_indexers, context.application, context.panel, path)
        context.application.paint(True)

    @staticmethod
    def run_indexers(blocker, application, panel, path, force=False):
        """Run the indexers on the file at ``path``

        ``force`` may be set to ``True`` to enforce re-indexing
        """
        blocker.title(f"Running indexers on {path.name}")
        logger.debug("Running indexers on %s", path.name)

        item = panel.selected_item

        if path.is_dir():
            paths = application.cache.find_indexable_files([path])
        else:
            paths = [path]

        last_modified = {}
        if force:
            last_modified = {p: datetime.datetime.max
                             for p in paths}

        results = index_files(paths,
                              application.metaindexconf,
                              ocr=metaindex.ocr.Dummy(),
                              fulltext=False,
                              last_modified=last_modified)
        if len(results) == 0:
            return

        blocker.progress((0, len(results)))

        # merge the results
        for idx, result in enumerate(results):
            logger.debug("index resulted in %s", result)

            base = application.cache.get(result.filename)
            if len(base) == 0:
                info = CacheEntry(result.filename)
            else:
                info = base[0]

            if not result.success:
                logger.debug(f"Indexer did not succeed on {result.filename}")
                continue
            logger.debug(f"Indexer found something for {result.filename}")

            # extend the cached metadata with the newly indexed data
            newly_added = False
            for key in set(result.info.keys()):
                for value in result.info[key]:
                    if value in info[key]:
                        continue
                    info.add(key, value)
                    newly_added = True

            if not newly_added:
                logger.debug("Nothing new here")
                return

            application.cache.insert(info)
            blocker.progress((idx+1, len(results)))

        if isinstance(panel, (DocPanel,)):
            panel.search(panel.query)
            application.callbacks.put((panel,
                                       lambda: panel.jump_to(item[-1].path)))
        elif isinstance(panel, (EditorPanel,)):
            application.callbacks.put((panel,
                                       panel.reload))
