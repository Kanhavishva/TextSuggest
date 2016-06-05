#!/usr/bin/env python

# Copyright © 2016 Bharadwaj Raju <bharadwaj.raju777@gmail.com>

# Licensed under the GNU General Public License 3 (https://www.gnu.org/licenses/gpl.txt)

# A simple linux tool to autocomplete text inputs in the GUI

# Uses the English Open Word List (http://dreamsteep.com/projects/the-english-open-word-list.html)
# Plus another set (in Custom_Words.txt) to include a few words that
# the EOWL doesn't.

# Inspired by zsh's smart tab completion

# Bind this script to a keyboard shortcut and press it to show
# a list of suggested words.

import os
import subprocess as sp
import sys

if '--noselect' in sys.argv:

    current_word = ''

    suggest_method = 'insert'

else:

    current_word_p = sp.Popen(['xclip', '-o', '-sel'], stdout=sp.PIPE)

    current_word, err_curr_word = current_word_p.communicate()

    current_word = current_word.decode('utf-8').strip()

    suggest_method = 'replace'

script_cwd = os.path.abspath(os.path.join(__file__, os.pardir))

dict_dir = os.path.join(script_cwd, 'EnglishOpenWordList')

def get_all_words():

    full_words_list = []

    for file in os.listdir(dict_dir):

        file = os.path.join(dict_dir, file)

        with open(file) as f:

            for word in f:

                full_words_list.append(word)

        f.close()

    with open(os.path.join(script_cwd, 'Custom_Words.txt')) as f:

        for word in f:

            full_words_list.append(word)

    f.close()

    return full_words_list

def get_suggestions(string):

    orig_string = string

    string = string.lower()

    if suggest_method == 'insert':

        return get_all_words()

    if suggest_method == 'replace':

        alphabet = str(current_word[:1]).upper()

        print(current_word)

        print(alphabet)

        dict_file = os.path.join(dict_dir, '%s.txt' % alphabet)

        print(dict_file)

        suggestions = []

        with open(dict_file) as f:

            for word in f:

                if string in word:

                    suggestions.append(word)

        f.close()

        with open(os.path.join(script_cwd, 'Custom_Words.txt')) as f:

            for word in f:

                suggestions.append(word)

        f.close()

        return suggestions

def display_dialog_list(item_list):

    dmenu_string = ''

    if item_list == [] or item_list == ['']:

        return None

    for i in item_list:

        dmenu_string += i

    if '--dmenu2' in sys.argv:

        # Make use of advanced dmenu2 features. Requires dmenu2 (fork of dmenu)
        # to be installed. (https://bitbucket.org/melek/dmenu2)

        mouse_loc_p = sp.Popen(['xdotool getmouselocation --shell'], shell=True, stdout=sp.PIPE)

        mouse_loc_raw, err_mouse_loc = mouse_loc_p.communicate()

        mouse_loc_raw = mouse_loc_raw.decode('utf-8')

        x = mouse_loc_raw.split('\n')[0].replace('X=', '')

        y = mouse_loc_raw.split('\n')[1].replace('Y=', '')

        dmenu_cmd_str = r'echo ' + str('"%s"' % dmenu_string) + ' | dmenu -i -p "Type to search >" -l 5 -w 320 -h 20 -x %s -y %s -dim 0.4' % (x, y)

    else:

        dmenu_cmd_str = r'echo ' + str('"%s"' % dmenu_string) + ' | dmenu -b -i -p "Type to search >"'

    if suggest_method == 'insert':

        # The argument list will be too long since it includes ALL dictionary
        # words.
        # subprocess can't handle it, and will raise OSError.
        # So we will write it to a script file.

        full_dict_dmenu_script_path = os.path.expanduser('~/.textsuggest_full.sh')

        with open(full_dict_dmenu_script_path, 'w') as f:

            f.truncate()

            f.write(dmenu_cmd_str)

        f.close()

        full_dict_dmenu_script_p = sp.Popen(['sh %s' % full_dict_dmenu_script_path], shell=True, stdout=sp.PIPE)

        choice, err_choice = full_dict_dmenu_script_p.communicate()

        return choice

    dmenu_p = sp.Popen(dmenu_cmd_str, shell=True, stdout=sp.PIPE)

    choice, err_choice = dmenu_p.communicate()

    return choice

def apply_suggestion(suggestion):

    suggestion = suggestion.decode('utf-8')

    if suggestion == '':

        # User doesn't want any suggestion
        # exit

        sys.exit(0)

    if suggest_method == 'replace':

        # Erase current word

        sp.Popen(['xdotool key BackSpace'], shell=True)

        if current_word[:1].isupper():

            suggestion = suggestion.capitalize()

            print(suggestion)

    # Type suggestion

    sp.Popen(['xdotool type %s' % suggestion], shell=True)

apply_suggestion(display_dialog_list(get_suggestions(current_word)))