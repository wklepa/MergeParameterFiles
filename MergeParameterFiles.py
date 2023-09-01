import os
import shutil
from datetime import datetime
import PySimpleGUI as sg


# Choose the color theme
sg.theme("SystemDefaultForReal")


def time_stamp(get_name: str, get_joiner: str = "_", formatter: bool = True) -> str:
    # Define local variables
    trimmer: int = 0
    # Start function body
    if formatter:
        trimmer = 2
    get_date: str = datetime.today().strftime('%Y%m%d')[trimmer:]
    return get_joiner.join([get_date, get_name])


def backup_file(full_file_name: str) -> bool:
    # Define local variables
    file_path: str = os.path.dirname(os.path.abspath(full_file_name))
    file_name_extension: list[str] = os.path.splitext(os.path.basename(full_file_name))
    backup_name_extension: str = time_stamp(file_name_extension[0]) + file_name_extension[1]
    backup_file_path: str = os.path.join(file_path, backup_name_extension)
    # Start function body
    try:
        shutil.copyfile(full_file_name, backup_file_path)
        pass
        return True
    except Exception:
        return False


def read_file(full_file_name: str) -> list[str]:
    # Define local variables
    eol_char: str = "\n"
    line_starter_body: str = "param"
    line_starter_group: str = "group"
    parameters_header: list[str] = []
    parameters_body: list[str] = []
    parameters_group: list[str] = []
    # Start function body
    with open(full_file_name, "r", encoding="UTF-16 LE") as fr:
        for line in fr:
            condition_body: bool = line.lower().startswith(line_starter_body)
            condition_group: bool = line.lower(). startswith(line_starter_group)
            if condition_group:
                parameters_group.append(line.rstrip(eol_char))
            if not condition_body and not condition_group:
                parameters_header.append(line.rstrip(eol_char))
            if condition_body and not condition_group:
                parameters_body.append(line.rstrip(eol_char))

    return parameters_header, parameters_body, parameters_group


def group_number_name(shared_group_names: list[str]) -> list[str]:
    # Define local variables
    group_names: list[str] = []
    group_numbers: list[str] = []
    splitter_char: str = "\t"
    split_shared_names: list[list[str]] = [item.split(splitter_char) for item in shared_group_names]
    # Start function body
    for line in split_shared_names:
        for index, item in enumerate(line):
            if index == 1:
                group_numbers.append(item)
            if index == 2:
                group_names.append(item)
    return group_numbers, group_names


def select_group(group_number: list[str], group_name: list[str]) -> str:
    # Define local variables
    group_integers: list[int] = [int(item) for item in group_number]
    min_int: int = min(group_integers)
    max_int: int = max(group_integers)

    def selection_window(number: str, name: str):
        formatted_name: str = f"{number} {name}"
        return [sg.Radio(formatted_name, 1)]

    layout = [selection_window(index, name) for index, name in zip(range(min_int, (max_int + 1)), group_name)] + [[sg.Button("Quit", size=(8, 1)), sg.Button("Save", size=(8, 1))]]
    window = sg.Window("List of groups", layout, keep_on_top=True, disable_minimize=True)

    while True:
        event, values = window.read()
        if event == "Quit":
            return_key: str = "1"
            break
        elif event == "Save":
            group_key: str = [key for key, value in values.items() if value is True][0]
            return_key: str = str(int(group_key) + 1)
            break
    window.close()
    return return_key


def unify_group(group_number: str, lines_to_change: list[str]) -> list[str]:
    group_index: int = 5
    line_splitter: str = "\t"
    split_lines: list[list[str]] = [line.split(line_splitter) for line in lines_to_change]
    substitute_group: list[str] = []
    for line in split_lines:
        temp: list[str] = []
        for index, item in enumerate(line):
            if index == group_index:
                temp.append(group_number)
            if index != group_index:
                temp.append(item)
        substitute_group.append(line_splitter.join(temp))
    return substitute_group


def write_file(main_file_name: str, items_to_add: list[str]) -> str:
    # Define local variables
    eol_char: str = "\n"
    # Start function body
    with open(main_file_name, "a", encoding="UTF-16 LE") as fw:
        try:
            for line in items_to_add:
                fw.write(line + eol_char)
            return "New lines were added to the source file."
        except Exception:
            return "Operation failed, no lines were added!"


def compare_file(main_file_body: list[str], reference_file_body: list[str]) -> (list[str], list[str]):
    # Define local variables
    line_delimiter: str = "\t"
    guid_index: int = 1
    parameter_name_index: int = 2
    # Start function body
    # Disassemble main body
    disassemble_main_body: list[str] = [item.split(line_delimiter) for item in main_file_body]
    extract_main_names: list[str] = [item[parameter_name_index] for item in disassemble_main_body]
    extract_main_guid: list[str] = [item[guid_index] for item in disassemble_main_body]
    # Disassemble reference body
    disassemble_reference_body: list[str] = [item.split(line_delimiter) for item in reference_file_body]
    extract_reference_names: list[str] = [item[parameter_name_index] for item in disassemble_reference_body]
    extract_reference_guid: list[str] = [item[guid_index] for item in disassemble_reference_body]
    # Compare items
    lines_to_add: list[str] = []
    lines_to_skip: list[str] = []
    for reference_guid, reference_name, reference_line in zip(extract_reference_guid, extract_reference_names, reference_file_body):
        if reference_guid not in extract_main_guid:
            if reference_name not in extract_main_names:
                lines_to_add.append(reference_line)
        elif reference_guid in extract_main_guid:
            lines_to_skip.append(reference_guid)
    return lines_to_add, lines_to_skip


def help_window():
    content = ["The tool updates one shared parameter file with the missing parameters",
               "from the other file. The files names must be entered together with their",
               "folder names. The tool makes a time-stamped copy of the modified file.",
               "Developed by wojciech.klepacki@grimshaw.global v.2.0 2019 - 2023"]

    layout = [[[sg.Text(line, font=("MS Sans Serif", 10))] for line in content], [sg.Button("Close", size=(8, 1))]]

    window = sg.Window("Help & Assistance", layout, modal=True, keep_on_top=True, element_justification="c", disable_minimize=True)

    while True:
        event, values = window.read()
        if event == "Close" or event == sg.WIN_CLOSED:
            break
    window.close()


# *********************************************************************************
# ! MAIN BODY
# *********************************************************************************
merge_to_default: str = r"C:\Project_XXX\Merge_to_SharedParameters.txt"
merge_from_default: str = r"C:\Project_XXX\Merge_from_SharedParameters.txt"


layout = [[sg.Frame("Browse for files:",
                    [[sg.FileBrowse("Merge to", size=(10, 1)), sg.Input(default_text=merge_to_default, key="-MERGE_TO-", tooltip="Location of shared parameter file to merge to.", size=(55,1))],
                     [sg.FileBrowse("Merge from", size=(10, 1)), sg.Input(default_text=merge_from_default, key="-MERGE_FROM-", tooltip="Location of shared parameter file to merge from.", size=(55,1))]])],
          [[sg.Frame("Output:",
                     [[sg.Multiline(size=(67, 20), key="-OUT_MSG-", tooltip="Displays progress message and status", autoscroll=True, horizontal_scroll=True)]])]],
          [sg.Frame("Action keys:",
                    [[sg.Button("Run", size=(8, 1), tooltip="Executes the script"), sg.Button("Quit", size=(8, 1), tooltip="Terminates the script"), sg.Button("Help", size=(8, 1), tooltip="Displays help & assistance")]])]]

window_main = sg.Window("Merge shared parameter files", layout, disable_minimize=True, keep_on_top=True)


def updateWindow(window_msg: str, window_name: str = "-OUT_MSG-"):
    window_main[window_name].print(window_msg, text_color="black", font=("MS Sans Serif", 10))


while True:
    event, values = window_main.read()
    get_merge_to: str = values["-MERGE_TO-"]
    get_merge_from: str = values["-MERGE_FROM-"]
    splitting_char: str = "\t"
    if event == "Quit" or event == sg.WIN_CLOSED:
        break
    elif event == "Help":
        help_window()
        continue
    elif event == "Run":
        if os.path.isfile(get_merge_to):
            if os.path.isfile(get_merge_from):
                if backup_file(get_merge_to):
                    source_names: list[str] = read_file(get_merge_to)[1]
                    group_names_numbers: list[str] = read_file(get_merge_to)[2]
                    reference_names: list[str] = read_file(get_merge_from)[1]
                    group_numbers: list[str] = group_number_name(group_names_numbers)[0]
                    group_names: list[str] = group_number_name(group_names_numbers)[1]
                    user_group: str = select_group(group_numbers, group_names)
                    lines_to_add: list[str] = compare_file(source_names, reference_names)[0]
                    lines_to_skip: list[str] = compare_file(source_names, reference_names)[1]
                    if lines_to_skip:
                        updateWindow("The list of duplicated GUIDs:")
                        for guid in lines_to_skip:
                            updateWindow(guid)
                    if lines_to_add:
                        modified_groups: list[str] = unify_group(user_group, lines_to_add)
                        updateWindow("The list of missing parameters:")
                        for parameter in modified_groups:
                            parameter_name: str = [name for name in parameter.split(splitting_char)][2]
                            updateWindow(parameter_name)
                        update_status: str = write_file(get_merge_to, modified_groups)
                        updateWindow(update_status)
                    else:
                        updateWindow("There are no parameters to be added.")
                else:
                    updateWindow("Failed to create \"Merge to\" backup file.")
            else:
                updateWindow("\"Merge from\" doesn't exist.")
        else:
            updateWindow("\"Merge to\" doesn't exist.")
