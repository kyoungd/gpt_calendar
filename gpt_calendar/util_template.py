import os
import json

def __load_template_file(templateFile: str):
    # file exists check
    tf1 = './templates/' + templateFile + '.json'
    if os.path.exists(tf1):
        with open(tf1) as json_file:
            template = json.load(json_file)
            return template
    tf2 = templateFile + '.json'
    if os.path.exists(tf2):
        with open(tf2) as json_file:
            template = json.load(json_file)
            return template
    return None

def save_template_file(templateFile: str, templateData: dict):
    # file exists check
    tf1 = './templates/' + templateFile + '.json'
    with open(tf1, 'w') as f:
        json.dump(templateData, f)

def _load_template_file(templateFile: str, configFile: str = None):
    # get folder path
    folderPath = os.path.dirname(templateFile)

    # Load the template file
    with open(templateFile, 'r') as file:
        template = json.load(file)
    
    # Default the config file to "units/<file-name>.json" if it's None
    if configFile is None:
        configFile = os.path.join(f"{folderPath}/units", os.path.basename(templateFile))
    
    # if the config file doesn't exist, return the template
    if not os.path.exists(configFile):
        return template
    
    # Load the config file
    with open(configFile, 'r') as file:
        config = json.load(file)
    
    # Create separate mappings for 'file' and 'string' replacements
    file_replacements = {key: item[key] for item in config if item['type'] == 'file' for key in item if key != 'type'}
    string_replacements = {key: item[key] for item in config if item['type'] == 'string' for key in item if key != 'type'}
    
    # Traverse the template and replace 'file' placeholders
    def replace_file_placeholders(obj):
        if isinstance(obj, str) and obj in file_replacements:
            with open(os.path.join(folderPath, file_replacements[obj]), 'r') as file:
                return json.load(file)
        elif isinstance(obj, dict):
            return {k: replace_file_placeholders(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_file_placeholders(element) for element in obj]
        else:
            return obj

    template = replace_file_placeholders(template)

    # Traverse the template and replace 'string' placeholders
    def replace_string_placeholders(obj):
        template = json.dumps(obj)
        for key, value in string_replacements.items():
            if key in template:
                template = template.replace(key, value)
        return json.loads(template)

    return replace_string_placeholders(template)


def load_template_file(templateFile: str, configFile: str = None):
    templateFile = "./templates/" + templateFile + ".json"
    return _load_template_file(templateFile, configFile)

def load_appointment_calendar(template: str):
    calendarFile = "./calendar/" + template + ".json"
    if os.path.exists(calendarFile):
        with open(calendarFile, 'r') as f:
            return json.load(f)
    else:
        return []
