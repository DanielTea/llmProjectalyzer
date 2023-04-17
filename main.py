import argparse
import os
import yaml
from project_compression.project_compression import ProjectCompressor
from project_compression.openai_utils import compress_string
from project_compression.prompt_utils import compress_data_with_chunking

# create the parser object
parser = argparse.ArgumentParser(description='Compress a project directory and write it to a text file.')

# add arguments
parser.add_argument('--project', type=str, help='The path to the project directory.', required=True)
parser.add_argument('--prefix', type=str, help='The prefix prompt to add to the compressed output.', default="This is compressed text, in your own language. You should be able to decompress it because it's in your language. Here's what to decompress:")
parser.add_argument('--suffix', type=str, help='The suffix prompt to add to the compressed output.', default="Explain the decompressed content.")
parser.add_argument('--model', type=str, help='The OpenAI language model to use for compression.', default='gpt-3.5-turbo')
parser.add_argument('--temperature', type=float, help='The temperature setting to use for the language model.', default=0.2)
parser.add_argument('--config', type=str, help='The path to the configuration file for folders and files to ignore during compression.', default='config.yml')
parser.add_argument('--max_content_tokens', type=int, help='The maximum number of content tokens allowed for each chunk of compressed data.', default=4000)
parser.add_argument('--double_comp', type=bool, help='Whether to compress the compressed output again or not.', default=False)


# parse the arguments
args = parser.parse_args()

# assign arguments to variables
project_folderpath = args.project
prefix = args.prefix
suffix = args.suffix
model = args.model
temperature = args.temperature
config_file_path = args.config
max_content_tokens = args.max_content_tokens
double_comp = args.double_comp

def read_config_file(config_file_path):
    with open(config_file_path) as f:
        config = yaml.safe_load(f)
    return config

config = read_config_file(config_file_path)

ignored_folders = config.get('ignored_folders', [])
ignored_files = config.get('ignored_files', [])
ignored_extensions = config.get('ignored_extensions', [])

compressor = ProjectCompressor(model=model, temperature=temperature, max_content_tokens=max_content_tokens)

compressed_data = compressor.compress_project(project_folderpath, ignored_folders=ignored_folders, ignored_files=ignored_files, ignored_extensions=ignored_extensions)

# check if double compression is requested
if double_comp:
    compressed_data = compress_data_with_chunking(compressed_data, model, temperature, max_content_tokens)

with open('compressed_project.txt', 'w') as f:
    f.write(f"{prefix}\n{compressed_data}\n{suffix}")

print("Compressed project saved to compressed_project.txt.")