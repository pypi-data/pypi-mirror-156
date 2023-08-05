__version__ = "1.0.1"
__docformat__ = "numpy"


DEFAULT_INDENT_SIZE = 4
"""int: How many spaces to use as an indent if not specified"""
DEFAULT_MAX_LINE_LENGTH = 80
"""int: How many characters to limit line length to if not specified"""


def dumps(obj, indent=DEFAULT_INDENT_SIZE, max_line_length=DEFAULT_MAX_LINE_LENGTH):
    """Renders JSON content with indentation and line splits/concatenations to fit max_line_length.

    Only dicts, lists and basic types are supported

    Parameters
    ----------
    obj : dict, list, tuple, str
        A python object to be converted to JSON
    indent : int, optional
        How many spaces to use as an indent before nested keys. Default is 2
    max_line_length : int, optional
        How many characters to limit a single line to before wrapping to the next line. Default is 80 characters

    Returns
    -------
    str
        A representation of the JSON to be piped to a .json file
    """

    items, _ = _get_subitems(
        obj,
        item_key="",
        is_last=True,
        max_line_length=max_line_length - indent,
        indent=indent,
    )
    return _indent_items(items, indent, level=0)


def _get_subitems(obj, item_key, is_last, max_line_length, indent):
    """Get all of the items within an iterable object

    Parameters
    ----------
    obj : any
    item_key : str
        The key for the
    is_last : bool
        Whether or not `obj` is the last item in the JSON object.
    max_line_length : int
        How many characters to limit a single line to before wrapping to the next line. Default is 80 characters
    indent : int
        How many spaces to use as an indent before nested keys. Default is 2

    Returns
    -------
    list[str]
        All of the individual items in the obj
    bool
        Whether or not `obj` should be rendered on a single line
    """

    items = []
    is_inline = (
        True  # at first, assume we can concatenate the inner tokens into one line
    )
    is_dict = isinstance(obj, dict)
    is_list = isinstance(obj, list)
    is_tuple = isinstance(obj, tuple)
    is_basic_type = not (is_dict or is_list or is_tuple)

    max_line_length = max(0, max_line_length)

    # build json content as a list of strings or child lists
    if is_basic_type:
        # render basic type
        key_separator = "" if item_key == "" else ": "
        item_separator = "" if is_last else ","
        items.append(
            item_key + key_separator + _basic_type_to_string(obj) + item_separator
        )

    else:
        # render lists/dicts/tuples
        if is_dict:
            opening, closing, keys = ("{", "}", iter(obj.keys()))
        elif is_list:
            opening, closing, keys = ("[", "]", range(0, len(obj)))
        elif is_tuple:
            opening, closing, keys = (
                "[",
                "]",
                range(0, len(obj)),
            )  # tuples are converted into json arrays

        if item_key != "":
            opening = item_key + ": " + opening
        if not is_last:
            closing += ","

        item_key = ""
        subitems = []

        # get the list of inner tokens
        for (i, k) in enumerate(keys):
            is_last_ = i == len(obj) - 1
            item_key_ = ""
            if is_dict:
                item_key_ = _basic_type_to_string(k)
            inner, is_inner_inline = _get_subitems(
                obj[k], item_key_, is_last_, max_line_length - indent, indent
            )
            subitems.extend(inner)  # inner can be a string or a list
            is_inline = (
                is_inline and is_inner_inline
            )  # if a child couldn't be rendered inline, then we are not able either

        # fit inner tokens into one or multiple lines, each no longer than max_line_length
        if is_inline:
            multiline = True

            # in Multi-line mode items of a list/dict/tuple can be rendered in multiple lines if they don't fit on one.
            # suitable for large lists holding data that's not manually editable.

            # in Single-line mode items are rendered inline if all fit in one line, otherwise each is rendered in a separate line.
            # suitable for smaller lists or dicts where manual editing of individual items is preferred.

            # this logic may need to be customized based on visualization requirements:
            if is_dict:
                multiline = False
            if is_list:
                multiline = True

            if multiline:
                lines = []
                current_line = ""

                for (i, item) in enumerate(subitems):
                    item_text = item
                    if i < len(inner) - 1:
                        item_text = item + ","

                    if len(current_line) > 0:
                        try_inline = current_line + " " + item_text
                    else:
                        try_inline = item_text

                    if len(try_inline) > max_line_length:
                        # push the current line to the list if max_line_length is reached
                        if len(current_line) > 0:
                            lines.append(current_line)
                        current_line = item_text
                    else:
                        # keep fitting all to one line if still below max_line_length
                        current_line = try_inline

                    # Push the remainder of the content if end of list is reached
                    if i == len(subitems) - 1:
                        lines.append(current_line)

                subitems = lines
                if len(subitems) > 1:
                    is_inline = False
            else:  # single-line mode
                total_length = len(subitems) - 1  # spaces between items
                for item in subitems:
                    total_length += len(item)
                if total_length <= max_line_length:
                    str = ""
                    for item in subitems:
                        str += (
                            item + " "
                        )  # insert space between items, comma is already there
                    subitems = [str.strip()]  # wrap concatenated content in a new list
                else:
                    is_inline = False

        # attempt to render the outer brackets + inner tokens in one line
        if is_inline:
            item_text = ""
            if len(subitems) > 0:
                item_text = subitems[0]
            if len(opening) + len(item_text) + len(closing) <= max_line_length:
                items.append(opening + item_text + closing)
            else:
                is_inline = False

        # if inner tokens are rendered in multiple lines already, then the outer brackets remain in separate lines
        if not is_inline:
            items.append(opening)  # opening brackets
            items.append(subitems)  # Append children to parent list as a nested list
            items.append(closing)  # closing brackets

    return items, is_inline


def _basic_type_to_string(obj):
    """Convert a python object to its string representation

    Parameters
    ----------
    obj : any
        Any python object. If the object is not a basic type (str, bool, None), it must have a `__str__()` method.

    Returns
    -------
    str
        A string representation of the given `obj`.
    """

    if isinstance(obj, str):
        str_obj = '"' + str(obj) + '"'
    elif isinstance(obj, bool):
        str_obj = {True: "true", False: "false"}[obj]
    elif obj is None:
        str_obj = "null"
    else:
        str_obj = str(obj)
    return str_obj


def _indent_items(items, indent, level):
    """Recursively traverses the list of json lines, adds indentation based on the current depth

    Parameters
    ----------
    items : iterable
    indent : int
        How many spaces to use to differentiate between levels
    level : int
        How many `indent`s to place before the given item

    Returns
    -------
    str
        The `items` iterable as an indented JSON-style string
    """

    res = ""
    indent_str = " " * (indent * level)
    for (i, item) in enumerate(items):
        if isinstance(item, list):
            res += _indent_items(item, indent, level + 1)
        else:
            is_last = i == len(items) - 1
            # no new line character after the last rendered line
            if level == 0 and is_last:
                res += indent_str + item
            else:
                res += indent_str + item + "\n"
    return res
