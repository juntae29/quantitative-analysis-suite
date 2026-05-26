import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from Visualizer.plots import set_font, generate_wordcloud
from Text_Mining.tokenizer import run_analysis