'''
Highlights unicode nbsp.
based on: https://bitbucket.org/theblacklion/sublime_plugins/src/3ea0c9e35d2f/highlight_trailing_spaces.py

You might want to override the following parameters within your file settings:
* highlight_trailing_spaces_max_file_size
  Restrict this to a sane size in order not to DDOS your editor.
* highlight_trailing_spaces_color_name
  Change this to a valid scope name, which has to be defined within your theme.

@author: Oktay Acikalin <ok@ryotic.de>

@license: MIT (http://www.opensource.org/licenses/mit-license.php)

@since: 2011-02-11
'''

import sublime
import sublime_plugin

DEFAULT_MAX_FILE_SIZE = 1048576
DEFAULT_COLOR_NAME = 'comment'

def view_is_too_big(view, max_size_setting, default_max_size=None):
    settings = view.settings()
    max_size = settings.get(max_size_setting, default_max_size)
    # print max_size, type(max_size)
    if max_size not in (None, False):
        max_size = long(max_size)
        cur_size = view.size()
        if cur_size > max_size:
            return True
    return False


def view_is_widget(view):
    settings = view.settings()
    return bool(settings.get('is_widget'))

class DeferedViewListener(sublime_plugin.EventListener):

    def __init__(self):
        super(DeferedViewListener, self).__init__()
        self.seen_views = []
        self.max_size_setting = ''
        self.default_max_file_size = None
        self.delay = 500

    def is_enabled(self, view):
        return True

    def view_is_too_big_callback(self):
        pass

    def update(self, view):
        pass

    def defered_update(self, view):
        if not view.window():  # If view is not visible window() will be None.
            return

        if view.id() not in self.seen_views:
            self.seen_views.append(view.id())

        if view_is_widget(view):
            return

        if not self.is_enabled(view):
            return

        if view_is_too_big(view, self.max_size_setting,
                           self.default_max_file_size):
            self.view_is_too_big_callback(view)
            return

        def func():
            self.update(view)

        if self.delay:
            sublime.set_timeout(func, self.delay)
        else:
            func()

    def on_modified(self, view):
        '''
        Event callback to react on modification of the document.

        @type  view: sublime.View
        @param view: View to work with.

        @return: None
        '''
        self.defered_update(view)

    def on_load(self, view):
        '''
        Event callback to react on loading of the document.

        @type  view: sublime.View
        @param view: View to work with.

        @return: None
        '''
        self.defered_update(view)

    def on_activated(self, view):
        '''
        Event callback to react on activation of the document.

        @type  view: sublime.View
        @param view: View to work with.

        @return: None
        '''
        if view.id() not in self.seen_views:
            self.defered_update(view)

class HighlightUnicodeListener(DeferedViewListener):

    def __init__(self):
        super(HighlightUnicodeListener, self).__init__()
        self.max_size_setting = 'highlight_unicode_max_file_size'
        self.default_max_file_size = DEFAULT_MAX_FILE_SIZE
        self.delay = 0

    def view_is_too_big_callback(self, view):
        view.erase_regions('HighlightUnicodeListener')

    def update(self, view):
        settings = view.settings()
        color_name = settings.get('highlight_unicode_color_name', DEFAULT_COLOR_NAME)
        trails = view.find_all('[ \t]+$')
        regions = []
        for trail in trails:
            regions.append(trail)
        view.add_regions('HighlightUnicodeJunk', regions, color_name,
                         sublime.DRAW_EMPTY_AS_OVERWRITE)
