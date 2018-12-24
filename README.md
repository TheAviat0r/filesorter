# External file sorter

There are two main tools - file generator and file sorter

## Generator
Arguments:

--config - path to config file, default is
config/generator_config.cfg

Config parameters:

output_path - Path to output file

string_size - Length of a single string in output file

batch_size - Internal parameter (batch of strings will be written on disk
instead of a single ones, and this parameter is a size of that batch)

file_size - Size of an output file
