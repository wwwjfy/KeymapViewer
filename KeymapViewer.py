import json
import os
import re

import sublime
import sublime_plugin


platform_dict = {'osx': 'OSX',
                 'linux': 'Linux',
                 'windows': 'Windows'}

comment_re = re.compile(
    '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
    re.DOTALL | re.MULTILINE
)


def parse_json(content):
    match = comment_re.search(content)
    while match:
        # single line comment
        content = content[:match.start()] + content[match.end():]
        match = comment_re.search(content)

    # Return json file
    return json.loads(content)


class KeymapViewerCommand(sublime_plugin.TextCommand):
    keymaps = None

    def run(self, edit):
        if self.keymaps is None:
            self.keymaps = []
        ignored_packages = self.view.settings().get("ignored_packages", [])
        packages_path = sublime.packages_path()
        for subitem in os.listdir(packages_path):
            # TODO: cache loaded ones
            if subitem in ignored_packages:
                continue
            subitem_dir = os.path.join(packages_path, subitem)
            if not os.path.isdir(subitem_dir):
                continue
            keymap_file = os.path.join(subitem_dir,
                                       'Default (%s).sublime-keymap' %
                                        platform_dict.get(sublime.platform()))
            if not os.path.exists(keymap_file):
                continue

            try:
                keymaps = parse_json(open(keymap_file, 'r').read())
            except:
                continue

            if not isinstance(keymaps, list):
                continue

            for keymap in keymaps:
                command = keymap.get('command')
                keys = keymap.get('keys')
                if not command or not keys:
                    continue
                self.keymaps.append([', '.join(keys),
                                     'Package: ' + subitem,
                                     'Command: ' + command])
        self.view.window().show_quick_panel(self.keymaps, self.on_selected)

    def on_selected(self, index):
        if index == -1:
            return

        package = self.keymaps[index][1][9:]
        keymap_file = os.path.join(sublime.packages_path(),
                                   package,
                                   'Default (%s).sublime-keymap' %
                                        platform_dict.get(sublime.platform()))
        self.view.window().open_file(keymap_file)


class KeymapViewerByPackageCommand(sublime_plugin.TextCommand):
    packages = None

    def run(self, edit):
        self.packages = []
        ignored_packages = self.view.settings().get("ignored_packages", [])
        packages_path = sublime.packages_path()
        for subitem in os.listdir(packages_path):
            # TODO: cache loaded ones
            if subitem in ignored_packages:
                continue
            subitem_dir = os.path.join(packages_path, subitem)
            if not os.path.isdir(subitem_dir):
                continue

            keymap_file = os.path.join(subitem_dir,
                                       'Default (%s).sublime-keymap' %
                                        platform_dict.get(sublime.platform()))
            if not os.path.exists(keymap_file):
                continue

            self.packages.append(subitem)
        self.view.window().show_quick_panel(self.packages, self.on_selected)

    def on_selected(self, index):
        if index == -1:
            return

        package = self.packages[index]
        keymap_file = os.path.join(sublime.packages_path(),
                                   package,
                                   'Default (%s).sublime-keymap' %
                                        platform_dict.get(sublime.platform()))
        self.view.window().open_file(keymap_file)
