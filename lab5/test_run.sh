#!/bin/bash

# Loop through all files in the 'in/' directory
for input_file in in/*; do
  # Run the Python script with the current input file
  python main.py "$input_file"
done