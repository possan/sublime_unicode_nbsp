'''
Highlights unicode nbsp. and trailing stuff
based on: https://bitbucket.org/theblacklion/sublime_plugins/src/3ea0c9e35d2f/highlight_trailing_spaces.py
'''

import sublime
import sublime_plugin

DEFAULT_MAX_FILE_SIZE = 1048576
DEFAULT_COLOR_NAME = 'invalid'

def view_is_too_big(view, max_size_setting, default_max_size=None):
    settings = view.settings()
    max_size = settings.get(max_size_setting, default_max_size)
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
        print "Hej"

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
        self.defered_update(view)

    def on_load(self, view):
        self.defered_update(view)

    def on_activated(self, view):
        if view.id() not in self.seen_views:
            self.defered_update(view)

class HighlightUnicodeListener(DeferedViewListener):

    # list originally from http://stackoverflow.com/a/6609998/96664
    chars = {
        u'\x82' : ',',        # High code comma
        u'\x84' : ',,',       # High code double comma
        u'\x85' : '...',      # Tripple dot
        u'\x88' : '^',        # High carat
        u'\x91' : ' \x27',     # Forward single quote
        u'\x92' : '\x27',     # Reverse single quote
        u'\x93' : '\x22',     # Forward double quote
        u'\x94' : '\x22',     # Reverse double quote
        u'\x95' : ' ',
        u'\x96' : '-',        # High hyphen
        u'\x97' : '--',       # Double hyphen
        u'\x99' : ' ',
        u'\xa0' : ' ',
        u'\xa6' : '|',        # Split vertical bar
        u'\xab' : '<<',       # Double less than
        u'\xbb' : '>>',       # Double greater than
        u'\xbc' : '1/4',      # one quarter
        u'\xbd' : '1/2',      # one half
        u'\xbe' : '3/4',      # three quarters
        u'\xbf' : '\x27',     # c-single quote
        u'\xa8' : '',         # modifier - under curve
        u'\xb1' : ''          # modifier - under line
    }

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
        regions = []
        for x in view.find_all(u'[' + ''.join(self.chars.keys()) + u']+'):
            regions.append(x)
        for x in view.find_all(u'[ \t]+$'):
            regions.append(x)
        
        #for x in view.find_all(u'^$'):
        #    regions.append(x)
        view.add_regions('HighlightUnicodeJunk', regions, color_name,
                         sublime.DRAW_EMPTY_AS_OVERWRITE)
