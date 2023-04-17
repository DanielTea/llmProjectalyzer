import os
import openai
import argparse
from dotenv import load_dotenv

load_dotenv()

# create the parser object
parser = argparse.ArgumentParser(description='Compress a project directory and write it to a text file.')

# add arguments
parser.add_argument('--project', type=str, help='The path to the project directory.', required=True)
parser.add_argument('--prefix', type=str, help='The prefix prompt to add to the compressed output.', default="This is compressed text, in your own language. You should be able to decompress it because it's in your language. Here's what to decompress:")
parser.add_argument('--suffix', type=str, help='The suffix prompt to add to the compressed output.', default="Explain the decompressed content.")
parser.add_argument('--model', type=str, help='The OpenAI language model to use for compression.', default='gpt-3.5-turbo')
parser.add_argument('--temperature', type=float, help='The temperature setting to use for the language model.', default=0.3)
parser.add_argument('--excepted_filetypes', type=list, help='A list of file extensions to exclude from compression.', default=['.pdf', '.exe', '.xlsx', '.pyc', '.txt', '.png'])

# parse the arguments
args = parser.parse_args()

# assign arguments to variables
project_folderpath = args.project
prefix = args.prefix
suffix = args.suffix
model = args.model
temperature = args.temperature
excepted_filetypes = args.excepted_filetypes

def get_folder_structure(folder_path, prefix=''):
    """
    Returns a text representation of the folder structure for a given directory path.

    Args:
    - folder_path: A string representing the path to the directory.
    - prefix: A string representing the prefix to add to the folder structure text.

    Returns:
    A string representing the text of the directory structure.
    """

    folder_structure = f'{prefix}{os.path.basename(folder_path)}/\n'
    prefix += '|   '
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            folder_structure += f'{prefix}|-- {item}\n'
        elif os.path.isdir(item_path):
            folder_structure += get_folder_structure(item_path, prefix)
    return folder_structure

def compress_string(text, model, temperature):
    """
    Compresses a given string using OpenAI's language model.

    Args:
    - text: A string representing the text to be compressed.
    - model: A string representing the name of the OpenAI language model to use for compression.
    - temperature: A float representing the temperature setting to use for the language model.

    Returns:
    A string representing the compressed version of the input text.
    """

    prompt = "Compress the following text as much as possible in a way that you the LLM can reconstruct exactly 100% the original text. This is for yourself. It does not need to be human readable or understandable. Abuse of language mixing, abbreviations, symbols (unicode and emoji), or any other encodings or internal representations is all permissible, as long as it, if pasted in a new inference cycle, will yield exactly- 100% identical results as the original text."

    api_key = os.environ["OPENAI_API_KEY"]
    openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model = model,
        messages = [
            {'role': 'user', 'content': prompt+text}
        ],
        temperature=temperature,
        )
    
    return response['choices'][0]['message']['content']

def read_file_content(file_path, encoding='utf-8'):
    """
    Reads the content of a file and returns it as a string.

    Args:
    - file_path: A string representing the path to the file.
    - encoding: A string representing the encoding to use when reading the file. Defaults to 'utf-8'.

    Returns:
    A string representing the content of the file.
    """
    with open(file_path, 'r', encoding=encoding) as f:
        content = f.read()
    return content

def add_prefix_prompt(prompt_template, prefix, suffix):
    """
    Adds a prefix and suffix prompt to a given string.

    Args:
    - prompt_template: A string representing the text to which the prefix and suffix prompt should be added.
    - prefix: A string representing the prefix prompt to add.
    - suffix: A string representing the suffix prompt to add.

    Returns:
    A string representing the original text with the prefix and suffix prompts added.
    """
    prefix_prompt = f"{prefix}\n\n"
    suffix_prompt = f"\n\n{suffix}"
    return prefix_prompt + prompt_template.strip() + suffix_prompt

def compress_project(project_folderpath, excepted_filetypes, prefix='', suffix='', model='gpt-3.5-turbo', temperature=0.7):
    """
    Compresses a project directory and saves the compressed data to a text file.

    Args:
    - project_folderpath: A string representing the path to the project directory.
    - excepted_filetypes: A list of strings representing file extensions to exclude from compression.
    - prefix: A string representing the prefix prompt to add to the compressed output. Defaults to an empty string.
    - suffix: A string representing the suffix prompt to add to the compressed output. Defaults to an empty string.
    - model: A string representing the name of the OpenAI language model to use for compression. Defaults to 'gpt-3.5-turbo'.
    - temperature: A float representing the temperature setting to use for the language model. Defaults to 0.7.

    Returns:
    A string representing the compressed data.
    """

    print(f"Compressing project at {project_folderpath}...")
    folder_structure = get_folder_structure(project_folderpath)
    comp_folder_structure = compress_string(folder_structure, model, temperature)
    print("Folder structure compressed successfully!")

    compressed_content = {}
    for root, _, files in os.walk(project_folderpath):
        for file in files:
            file_path = os.path.join(root, file)
            file_ext = os.path.splitext(file_path)[1]
            if file_ext not in excepted_filetypes:
                file_size = os.path.getsize(file_path)
                if file_size == 0:
                    print(f"{file_path} is empty, skipping compression...")
                    continue
                content = read_file_content(file_path)
                comp_content = compress_string(content, model, temperature)
                compressed_content[file_path] = comp_content
                print(f"{file_path} compressed successfully!")

    prompt_template = """
    This is the compressed folder and file structure of the project: {}

    """.format(comp_folder_structure)

    for file_path, comp_content in compressed_content.items():
        prompt_template += f"""
        This is the compressed content of {file_path}: {comp_content}

        """
    print("Project compressed successfully!")

    #TODO Fix a problem where the LLM returns incomplete responses when long messages are compressed
    # compressed_prompt_template = compress_string(prompt_template)

    compressed_prompt_template = prompt_template

    prompt_template = add_prefix_prompt(compressed_prompt_template, prefix, suffix)

    with open('compressed_project_prompt.txt', 'w', encoding='utf-8') as f:
        f.write(prompt_template)
        print("Compressed data saved to compressed_project.txt file.")

    return prompt_template

if __name__ == '__main__':
    # parse the arguments
    args = parser.parse_args()

    # assign arguments to variables
    project_folderpath = args.project
    prefix = args.prefix
    suffix = args.suffix
    model = args.model
    temperature = args.temperature
    excepted_filetypes = args.excepted_filetypes

    prompt_template = compress_project(project_folderpath, excepted_filetypes, prefix=prefix, suffix=suffix, model=model, temperature=temperature)
    print(prompt_template)
